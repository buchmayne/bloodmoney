landing_page = 'https://www.ufc.com/events'

headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }

events_per_page = 8
events_page = 'https://www.ufc.com/events?page=0'
output_path_fight_ids_csv = '../data/fight_ids.csv'
