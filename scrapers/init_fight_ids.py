import re
import math
from requests import get

import pandas as pd
from bs4 import BeautifulSoup

from parameters import landing_page, headers, events_per_page, events_page
from models import db_connect


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


def get_first_page_event_ids(events_page=events_page, headers=headers):
    """
    Inputs:
        events_page: str
            url of the first page of past events
        headers: dict
            headers defines the user agent and is used in the get request
    Outputs:
        event_ids_df: pd.DataFrame
            index:
                1) Deafult/Row Id
            columns:
                1) event_url: str
                2) event_id: str
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

    return event_ids_df


def get_all_event_ids(event_ids_df, total_pages):
    """
    Inputs:
        event_ids_df: pd.DataFrame
            index:
                1) row_idx
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
    event_ids_df.reset_index(drop=True, inplace=True)
    event_ids_df.index.names = 'row_idx'

    return event_ids_df


if __name__ == '__main__':
    total_pages = get_total_pages()
    first_page_event_ids = get_first_page_event_ids()
    all_event_ids = get_all_event_ids(first_page_event_ids, total_pages)
    all_event_ids.to_sql(
        name='eventid',
        con=db_connect(),
        if_exists='fail'  # if need to recreate change this to 'replace'
        )
    print('done!')
