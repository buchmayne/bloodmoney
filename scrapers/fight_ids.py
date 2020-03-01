import re
from requests import get
import pandas as pd
from bs4 import BeautifulSoup
import psycopg2
from parameters import headers, events_page
from models import db_connect


def extract_event_ids(events_page=events_page, headers=headers):
    """
    Inputs:
        events_page: str
            url of the first page of past events
        headers: dict
            headers defines the user agent and is used in the get request
    Outputs:
        event_ids: list
            list with the event link which contains the event id
    """
    # define prototype with the first event page
    events_raw_html = get(events_page, headers=headers)
    events_html = BeautifulSoup(events_raw_html.content, 'html.parser')

    # extract all of the event ids
    event_ids = []

    events_past = events_html.find(id="events-list-past")
    result_actions = events_past.find_all('div', 'c-card-event--result__actions')

    for i in list(range(len(result_actions))):
        try:
            tmp = result_actions[i].find('a')
            event_ids.append(tmp)
        except KeyError:
            pass

    return event_ids


def get_new_event_ids(most_recent_event_id, events_page=events_page, headers=headers):
    """
    Inputs:
        most_recent_event_id: int
            the event_id of the most recent event recorded in postgres
        events_page: str
            url of the first page of past events
        headers: dict
            headers defines the user agent and is used in the get request
    Outputs:
        event_ids_df: pd.DataFrame
            index:
                1) row_idx: int
            columns:
                1) event_url: str
                2) event_id: int
    """
    event_ids = extract_event_ids(events_page, headers)

    event_pattern = "(?<=href=\"/event/).*(?=\"><span)"
    event_ids = [re.findall(event_pattern, str(event)) for event in event_ids]

    # flatten the list
    event_ids = [item for sublist in event_ids for item in sublist]

    # convert the eventid list into a dataframe so that future pages can be bound
    event_ids_df = pd.DataFrame(event_ids, columns=['event'])
    event_ids_df = event_ids_df['event'].str.split(pat='#', expand=True)
    event_ids_df.columns = ['event_url', 'event_id']
    event_ids_df['event_id'] = event_ids_df['event_id'].astype(int)

    # get the row index of the most recently occured event_id
    if event_ids_df[event_ids_df['event_id'] == most_recent_event_id].empty:
        counter = 1
        events_page_format = 'https://www.ufc.com/events?page={}'
        tmp_pattern = "(?<=href=\"/event/).*(?=\"><span)"
        while most_recent_event_id not in event_ids_df['event_id'].tolist():
            # select the correct page from the listed past events
            tmp_page = events_page_format.format(counter)

            raw_html = get(tmp_page, headers=headers)
            html = BeautifulSoup(raw_html.content, 'html.parser')

            tmp_ids = []

            tmp_events_past = html.find(id="events-list-past")
            tmp_result_actions = tmp_events_past.find_all(
                'div',
                'c-card-event--result__actions'
                )

            for i in list(range(len(tmp_result_actions))):
                try:
                    tmp = tmp_result_actions[i].find('a')
                    tmp_ids.append(tmp)
                except KeyError:
                    pass

            tmp_ids = [re.findall(tmp_pattern, str(event)) for event in tmp_ids]

            # flatten the list
            tmp_ids = [item for sublist in tmp_ids for item in sublist]

            tmp_df = pd.DataFrame(tmp_ids, columns=['event'])
            tmp_df = tmp_df['event'].str.split(pat='#', expand=True)

            tmp_df.columns = ['event_url', 'event_id']
            tmp_df['event_id'] = tmp_df['event_id'].astype(int)

            # concatenate and reset index
            event_ids_df = pd.concat([event_ids_df, tmp_df], axis=0).reset_index(drop=True)
            counter += 1
        mp_idx = event_ids_df[event_ids_df['event_id'] == most_recent_event_id].index.values[0]
        event_ids_df = event_ids_df.iloc[:mp_idx, ]
        event_ids_df.reset_index(drop=True, inplace=True)
        event_ids_df.index.name = 'row_idx'

        return event_ids_df

    else:
        idx = event_ids_df[event_ids_df['event_id'] == most_recent_event_id].index.values[0]
        if idx == 0:
            return None
        elif most_recent_event_id in event_ids_df['event_id'].tolist():
            event_ids_df = event_ids_df.iloc[:idx, ]
            event_ids_df.index.name = 'row_idx'

            return event_ids_df


if __name__ == "__main__":
    conn = psycopg2.connect(
        host="localhost",
        database="bloodmoneydb",
        user="postgres",
        password="password"
    )

    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            event_id
        FROM
            eventid
        WHERE
            event_id IS NOT NULL
        ORDER BY
            row_idx ASC
        LIMIT 1;"""
        )
    most_recent_event_id = int(cur.fetchone()[0])
    cur.close()
    conn.close()

    event_df_updated = get_new_event_ids(most_recent_event_id)

    if event_df_updated is not None:
        print('Updating Database with new Event Data')
        event_df_updated.to_sql(
            name='eventid',
            con=db_connect(),
            if_exists='append'
        )
    print('done!')
