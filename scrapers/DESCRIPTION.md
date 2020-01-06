This document serves as the description of the data scraping process. The following is a rough sketch of the schema for the database with the ways in which each table will be related outlined. The inital design idea for the data acquisition process was for there to be two sets of processes, one that initalizes the database and populates it with data, and another process that will update the database with more current information. These two prcoesses are delineated by the `init_` prefix in the file names within the `scrappers` folder. 

Outline for how the data is related. 

I. Fight ID:
    The fight id is pulled down from the database and each fight id will be appended to a url to make a request. The response will be a dictionary with one key for `FMLiveFeed`. This is itself a dictionary with the following keys:
        'EventID',
        'Timestamp',
        'Date',
        'Time',
        'GMT',
        'Venue',
        'Country',
        'City',
        'CurFight',
        'EventStart',
        'EventEnd',
        'Fights'
    The value for each of these keys are a length 1 list for every key except for `Fights`. The first step is to write to the database all of the above data except for `Fights` to a table. This table is called `event_data`. The `EventID` column provides the crosswalk between the event and the data and is consistent for every fight. 

II. Fights:
    When accessing the values for the `Fights` key from the `FMLiveFeed` dictionary, the values are a list. Each item in the list contains a dictionary with data for a single fight. For a single fight, the keys of the dictionary are as follows:
        'FightID', 
        'Order', 
        'AccoladeName', 
        'WeightClassID', 
        'WeightClassName', 
        'Status', 
        'PossibleRds', 
        'CurRd', 
        'Fighters', 
        'Method', 
        'EndingRoundNum', 
        'FightActions'
    Again, the values are all length 1 lists with the exception of `Fighters` and `FightActions`. This data with the exception of the `Fighters` and `FightActions` will be added to the database's `fights_data` table. Additionally, it is necessary to add an `event_id` column to make sure that each fight can be crosswalked back to the event where it happened. 

III. Fighters:
    TBD

IV. FightActions:
    TBD

Psuedo code of functionality:

```
f = request(fight_id)

def get_data(f):
    
    event_id = f['EventID']
    
    add_event_data_to_db(f)

    for fight in f['Fights']:
        add_fight_data_to_db(fight, event_id)
        add_fighters_data_to_db(fight, event_id)
        add_fight_actions_data_to_db(fight, event_id)


```