import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="localhost",
    database="bloodmoneydb",
    user="postgres",
    password="password"
)

cur = conn.cursor()

data_query = """
    SELECT event_id, date, country, city, cur_fight FROM event_data LIMIT 50;
"""
cur.execute(data_query)
data = cur.fetchall()

col_names = ['event_id', 'date', 'country', 'city', 'cur_fight']

data = pd.DataFrame(data, columns=col_names)


if __name__ == "__main__":
    print(data)

    conn.close()

