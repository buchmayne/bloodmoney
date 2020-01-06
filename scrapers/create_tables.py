import psycopg2


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE event_data (
            event_id INTEGER PRIMARY KEY,
            time_stamp TIMESTAMP,
            date DATE,
            time TIME,
            gmt VARCHAR (20),
            venue VARCHAR (30),
            country VARCHAR (20),
            city VARCHAR (20),
            cur_fight VARCHAR (20),
            event_start VARCHAR (20),
            event_end VARCHAR (20)
        )
        """,
        """
        CREATE TABLE fights_data (
            fight_id INTEGER PRIMARY KEY,
            fight_order VARCHAR (30),
            accolade_name VARCHAR (30),
            weight_class_id VARCHAR (30),
            weight_class_name VARCHAR (30),
            status VARCHAR (30),
            possible_rds INTEGER,
            cur_rd INTEGER,
            method VARCHAR (30),
            ending_round_num INTEGER,
            event_id INTEGER
        )
        """,
        """
        CREATE TABLE fighters_data (
            fighter_id INTEGER PRIMARY KEY,
            color VARCHAR (20),
            first_name VARCHAR (30),
            last_name VARCHAR (30),
            short_name VARCHAR (30),
            full_name VARCHAR (30),
            nick_name VARCHAR (30),
            record_tot_fights INTEGER,
            record_win INTEGER,
            record_loss INTEGER,
            record_draw INTEGER,
            record_nc INTEGER,
            foo_city VARCHAR (20),
            foo_state VARCHAR (20),
            foo_county VARCHAR (20),
            foo_tricode VARCHAR (20),
            born_city VARCHAR (20),
            born_state VARCHAR (20),
            born_county VARCHAR (20),
            born_tricode VARCHAR (20),
            dob DATE,
            height FLOAT,
            weight FLOAT,
            stance VARCHAR (20),
            outcome VARCHAR (20),
            event_id INTEGER,
            fight_id INTEGER
        )
        """,
        """
        CREATE TABLE fight_actions_data (
            action_id INTEGER PRIMARY KEY,
            type VARCHAR (20),
            time TIME,
            truck_time TIME,
            fighter VARCHAR (20),
            fight_round INTEGER,
            fight_id INTEGER,
            event_id INTEGER
        )
        """)
    conn = None
    try:
        conn = psycopg2.connect(
                host="localhost",
                database="bloodmoneydb",
                user="postgres",
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
