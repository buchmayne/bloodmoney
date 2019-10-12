from requests import get
import psycopg2


conn = psycopg2.connect(
        host="localhost",
        database="bloodmoneydb",
        user="buchman",
        password="password"
)

cur = conn.cursor()
cur.execute("SELECT event_id FROM eventid WHERE event_id IS NOT NULL ORDER BY event_id DESC;")
all_fights_ids = cur.fetchall()

list_of_fight_ids = [int(x[0]) for x in all_fights_ids]

# TO DO: Need to create a new table to store the fight data and
# will dump the actual fight data into JSON column for now.
# Once the table creation functionality is defined the next step will be to
# loop throught the event ids and write to table. Once that is finished need to 
# add script that will check for new fights and then pull down new data and
# update table

r = get('https://dvk92099qvr17.cloudfront.net/V1/{}/Fnt.json'.format(list_of_fight_ids[100])).json()
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
