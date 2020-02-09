import psycopg2


def drop_tables():
    """ drop tables in the PostgreSQL database"""
    commands = (
        """
        DROP TABLE IF EXISTS event_data
        """,
        """
        DROP TABLE IF EXISTS fights_data
        """,
        """
        DROP TABLE IF EXISTS fighters_data
        """,
        """
        DROP TABLE IF EXISTS fight_actions_data
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
    drop_tables()
