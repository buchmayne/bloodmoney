import psycopg2
from init_fight_data import get_data

conn = psycopg2.connect(
        host="localhost",
        database="bloodmoneydb",
        user="postgres",
        password="password"
)

most_recent_fight_id_to_have_fight_data_query = """
    WITH tmp_join AS (
        SELECT *
        FROM event_data
        INNER JOIN eventid ON (event_data.event_id = eventid.event_id)
    )
    SELECT
    tmp_join.row_idx
    FROM tmp_join
    ORDER BY tmp_join.row_idx ASC LIMIT 1;
"""

fight_ids_needing_fight_data_query = """
    SELECT eventid.event_id
    FROM eventid
    WHERE eventid.row_idx < %s;
"""

cur = conn.cursor()
cur.execute(most_recent_fight_id_to_have_fight_data_query)

most_recent_fight_id_to_have_fight_data = str(cur.fetchone()[0])

cur.execute(
    fight_ids_needing_fight_data_query, most_recent_fight_id_to_have_fight_data
    )

fight_ids_needing_fight_data = cur.fetchall()

fight_ids_needing_fight_data = [
    int(fight_id[0]) for fight_id in fight_ids_needing_fight_data
    ]


if __name__ == "__main__":
    for idx in fight_ids_needing_fight_data:
        print(idx)
        get_data(fight_id=idx, connection=conn)
    conn.close()
    print('finished')
