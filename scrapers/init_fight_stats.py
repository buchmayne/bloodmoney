from requests import get
from bs4 import BeautifulSoup

url = 'https://www.ufc.com/event/ufc-fight-night-february-15-2020'

event_id = '8241'

headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }

# /matchup/960/8238/post


r = get('https://www.ufc.com/matchup/960/8241/post')

soup = BeautifulSoup(r.content, 'html.parser')

total_strikes = soup.find('div', class_="c-stat-compare total_strikes")
sig_strikes = soup.find('div', class_="c-stat-compare sig_strikes")
takedowns = soup.find('div', class_="c-stat-compare takedowns")

def get_fighter_comp_stats(comp_stats_soup, fighter_color):
    if fighter_color == 'red':
        group_string = 'c-stat-compare__group-1 red'
    elif fighter_color == 'blue':
        group_string = 'c-stat-compare__group-2 blue'
    else:
        return None
    fighter_color_stats = comp_stats_soup.find('div', class_=group_string)
    stats_div_value = fighter_color_stats.find('div', class_='c-stat-compare__number')
    string_value = stats_div_value.string
    
    return string_value

def scrape_fight_stats(soup_obj):
    '''
    TBD
    '''
    total_strikes_soup = soup.find('div', class_="c-stat-compare total_strikes")
    sig_strikes_soup = soup.find('div', class_="c-stat-compare sig_strikes")
    takedowns_soup = soup.find('div', class_="c-stat-compare takedowns")
    
    ts_red = get_fighter_comp_stats(total_strikes_soup, 'red')
    ts_blue = get_fighter_comp_stats(total_strikes_soup, 'blue')
    
    ss_red = get_fighter_comp_stats(sig_strikes_soup, 'red')
    ss_blue = get_fighter_comp_stats(sig_strikes_soup, 'blue')
    
    td_red = get_fighter_comp_stats(takedowns_soup, 'red')
    td_blue = get_fighter_comp_stats(takedowns_soup, 'blue')
    
    return 'yup yup sure'

