from requests import get
import psycopg2
import datetime as dt
import numpy as np


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


# test_fight_id = list_of_fight_ids[0]

# r = get(
#     'https://dvk92099qvr17.cloudfront.net/V1/{}/Fnt.json'
#     .format(891)
#     ).json()
# f = r['FMLiveFeed']


def get_data(fight_id, connection):
        '''
        TBD: Main function with subcalls which writes data to db
        '''
        r = get(
                'https://dvk92099qvr17.cloudfront.net/V1/{}/Fnt.json'
                .format(fight_id)
        ).json()
        f = r['FMLiveFeed']

        event_id = int(f['EventID'])
        fights_data = f['Fights']

        add_event_data(feed_data=f, connection=connection)
        add_fights_data(fights_data=fights_data, event_id=event_id, connection=connection)


def add_event_data(feed_data, connection):
        event_id = int(feed_data['EventID'])
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


def add_fights_data(fights_data, event_id, connection):
        '''
        TBD: Loop through fights list and for each fight write data to table
        '''
        for fight in fights_data:
                fight_id = int(fight['FightID'])

                # write the fighters data to table
                fighters_dict = fight['Fighters']
                add_fighters_data(
                        fighters_dict=fighters_dict,
                        event_id=event_id,
                        fight_id=fight_id,
                        connection=connection
                        )

                order = fight['Order']
                accolade_name = fight['AccoladeName']
                weightclass_id = fight['WeightClassID']
                weightclass_name = fight['WeightClassName']
                status = fight['Status']
                possible_rds = int(fight['PossibleRds'])
                cur_rd = int(fight['CurRd'])
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
                            ending_round_num,
                            event_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                        ending_round_num,
                        event_id
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


def add_fighters_data(fighters_dict, event_id, fight_id, connection):
        fighters_data_query = (
                        """
                        INSERT INTO fighters_data(
                            fighter_id,
                            color,
                            first_name,
                            last_name,
                            short_name,
                            full_name,
                            nick_name,
                            record_tot_fights,
                            record_win,
                            record_loss,
                            record_draw,
                            record_nc,
                            foo_city,
                            foo_state,
                            foo_county,
                            foo_tricode,
                            born_city,
                            born_state,
                            born_county,
                            born_tricode,
                            dob,
                            height,
                            weight,
                            stance,
                            outcome,
                            event_id,
                            fight_id
                        ) VALUES (
                                %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s
                        )
                        """
                )

        for fighter in fighters_dict:
                fighter_id = int(fighter['FighterID'])
                color = fighter['Color']
                first_name = fighter['FirstName']
                last_name = fighter['LastName']
                short_name = fighter['ShortName']
                full_name = fighter['FullName']
                nick_name = fighter['NickName']
                record_tot_fights = int(fighter['Record']['TotFights'])
                record_win = int(fighter['Record']['Win'])
                record_loss = int(fighter['Record']['Loss'])
                record_draw = int(fighter['Record']['Draw'])
                record_nc = int(fighter['Record']['NC'])
                foo_city = fighter['FightsOutOf']['City']
                foo_state = fighter['FightsOutOf']['State']
                foo_country = fighter['FightsOutOf']['Country']
                foo_tricode = fighter['FightsOutOf']['TriCode']
                born_city = fighter['Born']['City']
                born_state = fighter['Born']['State']
                born_country = fighter['Born']['Country']
                born_tricode = fighter['Born']['TriCode']
                dob = fighter['DOB']
                height = float(fighter['Height'])
                weight = float(fighter['Weight'])
                stance = fighter['Stance']
                outcome = fighter['Outcome']

                insert_data = (
                        fighter_id,
                        color,
                        first_name,
                        last_name,
                        short_name,
                        full_name,
                        nick_name,
                        record_tot_fights,
                        record_win,
                        record_loss,
                        record_draw,
                        record_nc,
                        foo_city,
                        foo_state,
                        foo_country,
                        foo_tricode,
                        born_city,
                        born_state,
                        born_country,
                        born_tricode,
                        dob,
                        height,
                        weight,
                        stance,
                        outcome,
                        event_id,
                        fight_id
                )
                try:
                        # create a new cursor
                        cur = connection.cursor()
                        # execute the INSERT statement
                        cur.execute(fighters_data_query, insert_data)
                        # commit the changes to the database
                        connection.commit()
                except (Exception, psycopg2.DatabaseError) as error:
                        print(error)


# NOTE: Script breaks on event id: 891
if __name__ == "__main__":
    for idx in list_of_fight_ids:
        print(idx)
        get_data(fight_id=idx, connection=conn)
    conn.close()
    print('finished')
