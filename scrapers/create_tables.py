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
            gmt VARCHAR (70),
            venue VARCHAR (70),
            country VARCHAR (70),
            city VARCHAR (70),
            cur_fight VARCHAR (70),
            event_start VARCHAR (70),
            event_end VARCHAR (70)
        )
        """,
        """
        CREATE TABLE fights_data (
            fight_id INTEGER PRIMARY KEY,
            fight_order VARCHAR (70),
            accolade_name VARCHAR (70),
            weight_class_id VARCHAR (70),
            weight_class_name VARCHAR (70),
            status VARCHAR (70),
            possible_rds INTEGER,
            cur_rd INTEGER,
            method VARCHAR (70),
            ending_round_num VARCHAR (10),
            event_id INTEGER
        )
        """,
        """
        CREATE TABLE fighters_data (
            fighter_id INTEGER,
            color VARCHAR (70),
            first_name VARCHAR (70),
            last_name VARCHAR (70),
            short_name VARCHAR (70),
            full_name VARCHAR (70),
            nick_name VARCHAR (70),
            record_tot_fights INTEGER,
            record_win INTEGER,
            record_loss INTEGER,
            record_draw INTEGER,
            record_nc INTEGER,
            foo_city VARCHAR (70),
            foo_state VARCHAR (70),
            foo_county VARCHAR (70),
            foo_tricode VARCHAR (70),
            born_city VARCHAR (70),
            born_state VARCHAR (70),
            born_county VARCHAR (70),
            born_tricode VARCHAR (70),
            dob DATE,
            height FLOAT,
            weight FLOAT,
            stance VARCHAR (70),
            outcome VARCHAR (70),
            event_id INTEGER,
            fight_id INTEGER
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
