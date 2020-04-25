import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine


def convert_event_date_and_fighter_dob_to_datetime(df, date_col='date', dob_col='date'):
    '''
    Convert date and dob columns to pandas datetime
    Input:
        df: pd.DataFrame
    Output:
        df: pd.DataFrame
    '''
    df[date_col] = pd.to_datetime(df[date_col])
    df[dob_col] = pd.to_datetime(df[dob_col])
    
    return df


def calculate_age_of_fighter(df, date_col='date', dob_col='dob'):
    '''
    Calculate the age of the fighter in years:
    Input:
        df: pd.DataFrame
        date_col: str (Datetime column name for event date)
        dob_col: str (Datetime column name for date of birth)
    Output:
        df: pd.DatFrame
            'age' column is an Int of the age of the fighter in years at the time of the event
    '''
    df = convert_event_date_and_fighter_dob_to_datetime(df=df, date_col='date', dob_col='dob')
    df['age'] = df[date_col].dt.year - df[dob_col].dt.year
    
    return df


def fighter_is_local(row):
    '''
    Define whether a given fighter is local which is whether the city of the event matches
    either the city they're either fighting out of or were born in. Iterate over rows of
    dataframe that contains the following columns:
        ['city', 'foo_city', 'born_city']
    '''
    if (row['city'] == row['foo_city']) | (row['city'] == row['born_city']):
        return True
    else:
        return False

    

def fighter_is_national(row):
    '''
    Define whether a given fighter's represented nation is the same nation hosting the event.
    Iterate over rows of
    dataframe that contains the following columns:
        ['country', 'foo_country', 'born_country']
    '''
    if (row['country'] == row['foo_country']) | (row['country'] == row['born_country']):
        return True
    else:
        return False
    
    
def fighter_home_court(df):
    '''
    Determine whether fighter is fighting in home town and home country.
    Input:
        df: pd.DataFrame
    Output:
        df: pd.DataFrame
        'is_local': boolean (event hosted in fighter's home town)
        'is_national': boolean (event hosted in fighter's country)
    '''
    df['is_local'] = df.apply(fighter_is_local, axis=1)
    df['is_national'] = df.apply(fighter_is_national, axis=1)
    
    return df


def calculate_pct_of_possible_rounds_fought(df, fighter_id_col='fighter_id', date_col='date'):
    '''
    Calculate the percentage of scheduled rounds a fighter has fought:
    Input:
        df: pd.DataFrame
        fighter_id_col: str (column name for the fighter_id column)
        date_col: str (Datetime column name for event date)
    Output:
        df: pd.DatFrame
            'cumulative_possible_rds' column is an Int of the total schedules rounds
                in a fighters' career up to that point
            'cumulative_fought_rds' column is an Int of the total rounds a figher
                has fought up to that point
            'pct_rds_fought' column is a float of the percent of scheduled rounds a fighter 
                has fought in their career
    '''
    df = df.sort_values([fighter_id_col, date_col])
    df['ending_round_num'] = pd.to_numeric(df['ending_round_num'], errors='coerce')
    df['possible_rds'] = pd.to_numeric(df['possible_rds'], errors='coerce')

    grouped_possible_rounds = df['possible_rds'].groupby(df[fighter_id_col])
    grouped_fought_rounds = df['ending_round_num'].groupby(df[fighter_id_col])

    cumulative_possible_rounds = grouped_possible_rounds.cumsum()
    cumulative_fought_rounds = grouped_fought_rounds.cumsum()

    df['cumulative_possible_rds'] = cumulative_possible_rounds 
    df['cumulative_fought_rds'] = cumulative_fought_rounds
    df['pct_rds_fought'] = df['cumulative_fought_rds'] / df['cumulative_possible_rds']
    
    return df


def iterate_win_streak(grouped_df):
    '''
    Loop through grouped dataframe by fighter and measure win/loss streaks
    '''
    win_streak = 0
    counter = 0
    output_values = []

    for index, row in grouped_df.iterrows():
        if counter == 0:
            counter += 1
            output_values.append(win_streak)
            if row['outcome'] == 'Win':
                win_streak = 1
            elif row['outcome'] == 'Loss':
                win_streak = -1
        else:
            counter += 1
            output_values.append(win_streak)
            if win_streak > 0:
                if row['outcome'] == "Win":
                    win_streak += 1
                elif row['outcome'] == 'Loss':
                    win_streak = -1
                else:
                    pass
            elif win_streak < 0:
                if row['outcome'] == "Win":
                    win_streak = 1
                elif row['outcome'] == 'Loss':
                    win_streak += -1
    
    return output_values


def calculate_win_streak(df, fighter_id_col='fighter_id', date_col='date'):
    '''
    Calculate the current win/loss streak of a fighter going into the event
    Input:
        df: pd.DataFrame
        fighter_id_col: str (column name for the fighter_id column)
        date_col: str (Datetime column name for event date)
    Output:
        df: pd.DatFrame
            'win_streak' column is an Int of the consecutive wins a fighter has entering the fight
    '''
    df = df.sort_values([fighter_id_col, date_col])
    grouped_win_streaks = df.groupby(fighter_id_col).apply(iterate_win_streak)
    
    win_streak_series = []
    for x in grouped_win_streaks:
        win_streak_series.extend(x)
    
    df['win_streak'] = win_streak_series
    
    return df


def transform_to_wide_by_fight(df, color_col='color'):
    '''
    Split the dataset into two separate datasets, one for red and blue corner.
    Join datasets together to have each observation be a single fight, with each
    fighter's features being specified by the color of the corner prefiex
    Input:
        df: pd.DataFrame with dimensions (m x n)
    Output:
        df: pd.DataFrame with dimensions (m/2, 2n-2)
    '''
    red = df[df[color_col] == 'Red'].copy()
    blue = df[df[color_col] == 'Blue'].copy()

    assert red.shape == blue.shape


    red_cols = ['red_{}'.format(col) for col in red.columns.tolist()]
    blue_cols = ['blue_{}'.format(col) for col in blue.columns.tolist()]

    red.columns = red_cols
    blue.columns = blue_cols

    red.rename(columns={'red_event_id': 'event_id', 'red_fight_id': 'fight_id'}, inplace=True)
    blue.rename(columns={'blue_event_id': 'event_id', 'blue_fight_id': 'fight_id'}, inplace=True)

    out_df = red.merge(blue, how='inner', on=['event_id', 'fight_id'])
    
    return out_df


def write_data_to_tbl(df):
    '''
    Write the transdformed data to the database, fail if the table already exists
    Input:
        df: pd.DataFrame
    Output:
        print statement indicating successful write to db
    '''
    engine = create_engine('postgres://postgres:password@localhost:5432/bloodmoneydb')
    df.to_sql('model_input_tbl_raw', engine, if_exists='fail')  # if need to recreate change this to 'replace'
    
    return 'Data successfully written to database'


if __name__ == "__main__":
    conn = psycopg2.connect(
            host="localhost",
            database="bloodmoneydb",
            user="postgres",
            password="password"
    )

    sql_query = """
        SELECT *
        FROM joined_fight_event_fighters_data
    """

    df = pd.read_sql_query(sql_query, con=conn)
    df = calculate_age_of_fighter(df=df)
    df = fighter_home_court(df)
    df = calculate_pct_of_possible_rounds_fought(df=df)
    df = calculate_win_streak(df=df)
    df = transform_to_wide_by_fight(df)
    
    write_data_to_tbl(df)

    print('Success')