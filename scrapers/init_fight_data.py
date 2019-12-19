from requests import get
import psycopg2
import datetime as dt


conn = psycopg2.connect(
        host="localhost",
        database="bloodmoneydb",
        user="postgres",
        password="password"
)

cur = conn.cursor()
cur.execute("SELECT event_id FROM eventid WHERE event_id IS NOT NULL ORDER BY event_id DESC;")
all_fights_ids = cur.fetchall()

list_of_fight_ids = [int(x[0]) for x in all_fights_ids]


def format_event_date(text):
    parts = text.split('-')
    formatted_date = dt.date(int(parts[0]), int(parts[1]), int(parts[2]))

    return formatted_date

# create list of all JSON repsonses vs. iterating through


r = get(
    'https://dvk92099qvr17.cloudfront.net/V1/{}/Fnt.json'
    .format(list_of_fight_ids[0])
    ).json()
f = r['FMLiveFeed']


def add_event_data(feed_data, connection):
        event_id = feed_data['EventID']
        timestamp = feed_data['Timestamp']
        date = format_event_date(feed_data['Date'])
        time = feed_data['Time']
        gmt = feed_data['GMT']
        venue = feed_data['Venue']
        country = feed_data['Country']
        city = feed_data['City']
        cur_fight = feed_data['CurFight']
        event_start = feed_data['EventStart']
        event_end = feed_data['EventEnd']

        event_data_query = (
                """
                INSERT INTO event_data(
                        event_id,
                        time_stamp,
                        date,
                        time,
                        gmt,
                        venue,
                        country,
                        city,
                        cur_fight,
                        event_start,
                        event_end
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        )
        insert_data = (
                event_id,
                timestamp,
                date,
                time,
                gmt,
                venue,
                country,
                city,
                cur_fight,
                event_start,
                event_end
        )
        try:
                # create a new cursor
                cur = connection.cursor()
                # execute the INSERT statement
                cur.execute(event_data_query, insert_data)
                # commit the changes to the database
                connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
                print(error)


def add_fights_data(feed_data, connection):
        fights_data = feed_data['Fights']

        for fight in fights_data:
                fight_id = fight['FightID']
                order = fight['Order']
                accolade_name = fight['AccoladeName']
                weightclass_id = fight['WeightClassID']
                weightclass_name = fight['WeightClassName']
                status = fight['Status']
                possible_rds = fight['PossibleRds']
                cur_rd = fight['CurRd']
                method = fight['Method']
                ending_round_num = fight['EndingRoundNum']

                fights_data_query = (
                        """
                        INSERT INTO fights_data(
                        fight_id,
                        fight_order,
                        accolade_name,
                        weight_class_id,
                        weight_class_name,
                        status,
                        possible_rds,
                        cur_rd,
                        method,
                        ending_round_num
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                )
                insert_data = (
                        fight_id,
                        order,
                        accolade_name,
                        weightclass_id,
                        weightclass_name,
                        status,
                        possible_rds,
                        cur_rd,
                        method,
                        ending_round_num
                )
                try:
                        # create a new cursor
                        cur = connection.cursor()
                        # execute the INSERT statement
                        cur.execute(fights_data_query, insert_data)
                        # commit the changes to the database
                        connection.commit()
                except (Exception, psycopg2.DatabaseError) as error:
                        print(error)


if __name__ == "__main__":
    add_event_data(feed_data=f, connection=conn)
    add_fights_data(feed_data=f, connection=conn)
    conn.close()
    print('finished')
