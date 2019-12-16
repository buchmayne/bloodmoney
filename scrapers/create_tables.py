import psycopg2


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE event_data (
            event_id TEXT PRIMARY KEY,
            time_stamp TIMESTAMP,
            date DATE,
            time TIME,
            gmt TEXT,
            venue TEXT,
            country TEXT,
            city TEXT,
            cur_fight TEXT,
            event_start TEXT,
            event_end TEXT
        )
        """,
        """
        CREATE TABLE fights_data (
            fight_id TEXT PRIMARY KEY,
            fight_order TEXT,
            accolade_name TEXT,
            weight_class_id TEXT,
            weight_class_name TEXT,
            status TEXT,
            possible_rds INTEGER,
            cur_rd INTEGER,
            method TEXT,
            ending_round_num INTEGER
        )
        """,
        """
        CREATE TABLE fighters_data (
            fighter_id TEXT PRIMARY KEY,
            color TEXT,
            first_name TEXT,
            last_name TEXT,
            short_name TEXT,
            full_name TEXT,
            nick_name TEXT,
            record_tot_fights INTEGER,
            record_win INTEGER,
            record_loss INTEGER,
            record_draw INTEGER,
            record_nc INTEGER,
            foo_city TEXT,
            foo_state TEXT,
            foo_county TEXT,
            foo_tricode TEXT,
            born_city TEXT,
            born_state TEXT,
            born_county TEXT,
            born_tricode TEXT,
            dob DATE,
            height FLOAT,
            weight FLOAT,
            stance TEXT,
            outcome TEXT
        )
        """,
        """
        CREATE TABLE fight_actions_data (
            action_id TEXT PRIMARY KEY,
            type TEXT,
            time TIME,
            truck_time TIME,
            fighter TEXT,
            fight_round INTEGER
        )
        """)
    conn = None
    try:
        conn = psycopg2.connect(
                host="localhost",
                database="bloodmoneydb",
                user="buchman",
                password="password"
        )
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
