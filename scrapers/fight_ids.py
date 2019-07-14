import re
import math
from requests import get

import pandas as pd
from bs4 import BeautifulSoup


# PARAMATERS #
landing_page = 'https://www.ufc.com/events'

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }

events_per_page = 8

# All standard UFC fight cards have a url of the following form, formatted with
# the fight card number (so UFC 235 would be https://www.ufc.com/event/ufc-235)
url_card_format = 'https://www.ufc.com/event/{}'

# All individual fights have a url of the following form, where the first
# number is the fight card ID number, and the second number is the individual
# fight number, so UFC 235 Jon Jones vs Anthony Smith is
# https://www.ufc.com/matchup/908/7717
url_fight_format = 'https://www.ufc.com/matchup/{}/{}'


# FUNCTIONS #


def get_total_pages(events_per_page):
    """
    TBD
    """
    page = get(landing_page, headers=headers)
    page_html = BeautifulSoup(page.content, 'html.parser')

    past_events = page_html.find(id="events-list-past")
    past_events = past_events.find_all('div', 'althelete-total')

    total_past_events = [event.text for event in past_events]

    # extract the total events as an int
    count_pattern = '^\\d*'
    total_past_events = int(re.findall(count_pattern, total_past_events[0])[0])

    # extract the total number of event pages
    total_pages = math.ceil(total_past_events / events_per_page)

    return total_pages


def get_first_page_event_ids():
    """
    TBD
    """
    # define prototype with the first event page
    events_page = 'https://www.ufc.com/events?page=0'

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
    TBD
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

    event_ids_df = pd.concat([event_ids_df, pd.concat(list_tmp_dfs)]).\
        reset_index(drop=True)

    return event_ids_df


def get_matchups_from_event(card_suffix):
    """
    TBD
    """
    url_card = url_card_format.format(card_suffix)

    raw_html = get(url_card, headers=headers)
    html = BeautifulSoup(raw_html.content, 'html.parser')

    # create data containers
    data = dict()

    fight_ids = []
    odds = []
    fighter_1 = []
    fighter_2 = []

    # Extract the inidivudal fight ids, fighter names, and odds
    # Looking through each div line
    for line in html.select('div'):
        # Checking to see if it contains an individual fight number
        try:
            if line['class'] == ['c-listing-fight']:
                fight_ids.append(line['data-fmid'])
        except KeyError:
            pass
        # Checking to see if it contains the odds
        try:
            if line['class'] == ['c-listing-fight__odds']:
                # Checking to see if there are odds recorded for this fight
                if line.contents[1].contents[0] == '-':
                    fighter_1_odds = fighter_2_odds = pd.np.nan
                else:
                    fighter_1_odds = int(line.contents[1].contents[0])
                    fighter_2_odds = int(line.contents[5].contents[0])
                odds.append([fighter_1_odds, fighter_2_odds])
        except KeyError:
            pass
        # Checking to see if it contains a red corner name
        try:
            if line['class'] == ['c-listing-ticker-fightcard__red_corner_name']:
                fighter_1.insert(0, line.contents[0])
        except KeyError:
            pass
        # Checking to see if it contains a red corner name
        try:
            if line['class'] == ['c-listing-ticker-fightcard__blue_corner_name']:
                fighter_2.insert(0, line.contents[0])
        except KeyError:
            pass

    data[card_suffix] = dict()
    data[card_suffix]['fight_ids'] = fight_ids
    data[card_suffix]['fighter_1'] = fighter_1
    data[card_suffix]['fighter_2'] = fighter_2
    data[card_suffix]['odds'] = odds

    event_data = pd.DataFrame(data[card_suffix])
    event_data['event_name'] = card_suffix

    return event_data


df = get_first_page_event_ids()
total_pages = get_total_pages(events_per_page=events_per_page)
df = get_all_event_ids(event_ids_df=df, total_pages=total_pages)

# Scraping a single UFC page
example_card_suffix = df.loc[0, 'event_url']

single_event = get_matchups_from_event(card_suffix=example_card_suffix)

print(single_event)

# test = 'https://www.ufc.com/matchup/908/7717/post'
# headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
#     }
# raw_html = get(test, headers=headers)
# html = BeautifulSoup(raw_html.content, 'html.parser')

# # This will pull down the general round and round statistics
# i = 1
# round_ = html.find_all('div', attrs={'class': 'l-flex--4col-2to4 round-{}'.format(i)})

# while len(round_) > 0:
#     print('ROUND {}'.format(i))
#     for stats in round_:
#         # Dropping the elements that are simply line breaks
#         stats = [c for c in stats if c != '\n']

#         # What remains are the actual statistics
#         for stat in stats:
#             # The c-stat-metric-compare__label classes contains which statistic is being addressed
#             stat_header = stat.find_all(
#                 'div', attrs={'class': 'c-stat-metric-compare__label'}
#             )[0].contents[0].strip(' \n')
#             print(stat_header)
#             # The span tags all contains each fighter's raw and percent number for that statistic
#             temp = stat.find_all('span')
#             # If the length of temp is 4, then the statistic has percentanges
#             if len(temp) == 4:
#                 fighter_1_raw = temp[0].contents[0]
#                 fighter_1_perc = temp[1].contents[0]
#                 fighter_2_raw = temp[2].contents[0]
#                 fighter_2_perc = temp[3].contents[0]
#             # If the length of temp is 2, then the statistic does not have percentages
#             if len(temp) == 2:
#                 fighter_1_raw = temp[0].contents[0]
#                 fighter_2_raw = temp[1].contents[0]
#             print(fighter_1_raw, fighter_2_raw)
#     # Moving onto the next round
#     i += 1
#     round_ = html.find_all('div', attrs={'class': 'l-flex--4col-2to4 round-{}'.format(i)})

# # This will pull down the round by round significant strikes by area and distance
# i = 1
# round_ = html.find_all('div', attrs={'class': 'l-flex--3col-1to3 round-{}'.format(i)})

# while len(round_) > 0:
#     print('ROUND {}'.format(i))

#     # First we'll pull the round by round strikes by area
#     for stats in round_[1].contents:
#         # Dropping the elements that are simply line breaks
#         stats = [c for c in stats if c != '\n']

#         # What remains are the actual statistics
#         for stat in stats:
#             # The c-stat-metric-compare__label classes contains which statistic is being addressed
#             stat_header = stat.find_all(
#                 'div', attrs={'class': 'c-stat-metric-compare__label'}
#             )[0].contents[0].strip(' \n')
#             print(stat_header)
#             # The span tags all contains each fighter's raw and percent number for that statistic
#             temp = stat.find_all('span')
#             # If the length of temp is 4, then the statistic has percentanges
#             if len(temp) == 4:
#                 fighter_1_raw = temp[0].contents[0]
#                 fighter_1_perc = temp[1].contents[0]
#                 fighter_2_raw = temp[2].contents[0]
#                 fighter_2_perc = temp[3].contents[0]
#             # If the length of temp is 2, then the statistic does not have percentages
#             if len(temp) == 2:
#                 fighter_1_raw = temp[0].contents[0]
#                 fighter_2_raw = temp[1].contents[0]
#             print(fighter_1_raw, fighter_1_perc, fighter_2_raw, fighter_2_perc)

#     # Second we'll pull the round by round strikes by area
#     for stats in round_[1].contents:
#         # Dropping the elements that are simply line breaks
#         stats = [c for c in stats if c != '\n']

#         # What remains are the actual statistics
#         for stat in stats:
#             # The c-stat-metric-compare__label classes contains which statistic is being addressed
#             stat_header = stat.find_all(
#                 'div', attrs={'class': 'c-stat-metric-compare__label'}
#             )[0].contents[0].strip(' \n')
#             print(stat_header)
#             # The span tags all contains each fighter's raw and percent number for that statistic
#             temp = stat.find_all('span')
#             # If the length of temp is 4, then the statistic has percentanges
#             if len(temp) == 4:
#                 fighter_1_raw = temp[0].contents[0]
#                 fighter_1_perc = temp[1].contents[0]
#                 fighter_2_raw = temp[2].contents[0]
#                 fighter_2_perc = temp[3].contents[0]
#             # If the length of temp is 2, then the statistic does not have percentages
#             if len(temp) == 2:
#                 fighter_1_raw = temp[0].contents[0]
#                 fighter_2_raw = temp[1].contents[0]
#             print(fighter_1_raw, fighter_1_perc, fighter_2_raw, fighter_2_perc)

#     # Moving onto the next round
#     i += 1
#     round_ = html.find_all('div', attrs={'class': 'l-flex--3col-1to3 round-{}'.format(i)})
