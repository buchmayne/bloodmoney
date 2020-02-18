import re
import math
from requests import get
import pandas as pd
from bs4 import BeautifulSoup
import psycopg2
from parameters import landing_page, headers, events_per_page, events_page


def get_total_pages(events_per_page=events_per_page, landing_page=landing_page, headers=headers):
    """
    Inputs:
        events_per_page: int
            the number of events on each page of the ufc site
        landing_page: str
            landing page is mostly likely static and directs to https://www.ufc.com/events
        headers: dict
            headers defines the user agent and is used in the get request
    Outputs:
        total_pages: int
            integer count of the total past ufc events divided by events per page
    """
    page = get(landing_page, headers=headers)
    page_html = BeautifulSoup(page.content, 'html.parser')

    past_events = page_html.find(id="events-list-past")
    past_events = past_events.find('div', 'althelete-total')
    total_past_events = past_events.get_text()

    # extract the total number of events as an int
    count_pattern = '^\\d*'
    total_past_events = int(re.search(count_pattern, total_past_events).group(0))

    # extract the total number of event pages
    total_pages = math.ceil(total_past_events / events_per_page)

    return total_pages


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


def get_most_recent_event_ids(most_recent_event_id, events_page=events_page, headers=headers):
    """
    Inputs:
        most_recent_event_id: str
            the most recent event id in the fight database
        events_page: str
            url of the first page of past events
        headers: dict
            headers defines the user agent and is used in the get request
    Outputs:
        new_rows: pd.DataFrame | None
            index:
                2) event_id: int
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

    event_ids_df['event_id'] = pd.to_numeric(event_ids_df['event_id'])

    # filter dataframe to only have new events
    if event_ids_df.loc[0, 'event_id'] != most_recent_event_id:
        most_recent_index = event_ids_df[event_ids_df['event_id'] == most_recent_event_id]\
            .index\
            .values\
            .astype(int)[0]

        new_rows = event_ids_df.loc[0:(most_recent_index - 1), :]\
            .set_index('event_id', drop=True)
        return new_rows
    else:
        return None


# TO DO: need to add function which updates data when there are more than one
# page of new eventids. Currently data is only being updated when the
# new data is on the first page of past events on the ufc site.
if __name__ == "__main__":
    conn = psycopg2.connect(
        host="localhost",
        database="bloodmoneydb",
        user="postgres",
        password="password"
    )

    cur = conn.cursor()
    cur.execute("SELECT event_id FROM eventid WHERE event_id IS NOT NULL ORDER BY event_id DESC;")

    most_recent_event_id = cur.fetchone()[0]
    event_df_updated = get_most_recent_event_ids(most_recent_event_id)

    if event_df_updated is not None:
        print('Updating Database with new Event Data')
        for index, row in event_df_updated.itertuples():
            cur.execute("INSERT INTO eventid(event_id, event_url) VALUES (%s, %s)", (index, row))
            conn.commit()
    cur.close()
    conn.close()
    print('done!')
