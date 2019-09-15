landing_page = 'https://www.ufc.com/events'

headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }

events_per_page = 8
events_page = 'https://www.ufc.com/events?page=0'
output_path_fight_ids_csv = '../data/fight_ids.csv'

# dvk92099qvr17.cloudfront.net/V1{id}/Fnt.json

# All standard UFC fight cards have a url of the following form, formatted with
# the fight card number (so UFC 235 would be https://www.ufc.com/event/ufc-235)
url_card_format = 'https://www.ufc.com/event/{}'

# All individual fights have a url of the following form, where the first
# number is the fight card ID number, and the second number is the individual
# fight number, so UFC 235 Jon Jones vs Anthony Smith is
# https://www.ufc.com/matchup/908/7717
url_fight_format = 'https://www.ufc.com/matchup/{}/{}'
