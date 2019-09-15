from requests import get
import pandas as pd

fight_ids = pd.read_csv('../data/fight_ids.csv', dtype=str)
test_event_id = fight_ids.loc[0, 'event_id']

r = get('https://dvk92099qvr17.cloudfront.net/V1/{}/Fnt.json'.format(test_event_id)).json()
f = r['FMLiveFeed']

# keys from event
eventid_ = f['EventID']
timestamp_ = f['Timestamp']
date_ = f['Date']
time_ = f['Time']
gmt_ = f['GMT']
venue_ = f['Venue']
country_ = f['Country']
city_ = f['City']
curfight_ = f['CurFight']
eventstart_ = f['EventStart']
eventend_ = f['EventEnd']

# fight data is contained in the fights key
fights = f['Fights']

# keys that exist in the fights data
# 'FightID', 'Order', 'AccoladeName', 'WeightClassID', 'WeightClassName', 'Status', 'PossibleRds', 'CurRd', 'Fighters', 'Method', 'EndingRoundNum', 'FightActions'
