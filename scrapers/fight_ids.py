import re
from requests import get
import pandas as pd
from bs4 import BeautifulSoup
import psycopg2
from parameters import headers, events_page


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


def tmp_func(most_recent_event_id, events_page=events_page, headers=headers):
    """
    Inputs:
        events_page: str
            url of the first page of past events
        headers: dict
            headers defines the user agent and is used in the get request
    Outputs:
        event_ids_df: pd.DataFrame
            index:
                1) event_id: int
            columns:
                1) event_url: str
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
    idx = event_ids_df[event_ids_df['event_id'] == most_recent_event_id].index.values[0]
    if idx == 0:
        return None
    elif most_recent_event_id in event_ids_df['event_id'].tolist():
        event_ids_df = event_ids_df.iloc[:idx, ]   
        return event_ids_df
    else:
        pass
        # NOTE: this is where the function needs to iterate until the most recent id has been matched


def get_all_event_ids(event_ids_df, total_pages):
    """
    Inputs:
        event_ids_df: pd.DataFrame
            index:
                1) Default/Row Id
            columns:
                1) event_url: str
                2) event_id: str
        total_pages: int
            integer count of the total past ufc events divided by events per page
    """
    # loop through each page and append the event url and id to the dataframe
    list_tmp_dfs = []
    events_page_format = 'https://www.ufc.com/events?page={}'
    tmp_pattern = "(?<=href=\"/event/).*(?=\"><span)"

    for page_num in range(1, total_pages):
        # select the correct page from the listed past events
        tmp_page = events_page_format.format(page_num)

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

        list_tmp_dfs.append(tmp_df)

    event_ids_df = pd.concat([event_ids_df, pd.concat(list_tmp_dfs)])
    event_ids_df['event_id'] = pd.to_numeric(event_ids_df['event_id'])
    event_ids_df.set_index('event_id', drop=True, inplace=True)

    return event_ids_df


# NOTE: The current issue I have found is that the event_id are not incremented linearly. For example
# UFC 246 is event_id 963 but UFC 247 is event_id 958
# This is a problem because I can't select the highest event_id from the db and use
# it to compare to the newly scraped event_id. I need to improve SQL skills to just return the first row of the 
# table without ordering the column. Then I need to return all of the scraped event_ids that occur before 
# that event_id


if __name__ == "__main__":
    conn = psycopg2.connect(
        host="localhost",
        database="bloodmoneydb",
        user="postgres",
        password="password"
    )

    cur = conn.cursor()
    cur.execute("SELECT event_id FROM eventid WHERE event_id IS NOT NULL;")

    most_recent_event_id = int(cur.fetchone()[0])
    event_df_updated = tmp_func(most_recent_event_id)

    if event_df_updated is not None:
        print('Updating Database with new Event Data')
        for index, row in event_df_updated.itertuples():
            cur.execute("INSERT INTO eventid(event_id, event_url) VALUES (%s, %s)", (index, row))
            conn.commit()
    cur.close()
    conn.close()
    print('done!')
