DROP TABLE IF EXISTS joined_fight_event_fighters_data;
CREATE TABLE joined_fight_event_fighters_data AS
SELECT 
    event_data.date,
    event_data.country,
    event_data.city,
    event_data.cur_fight,
    fighters_data.*,
    fights_data.accolade_name,
    fights_data.weight_class_id,
    fights_data.weight_class_name,
    fights_data.possible_rds,
    fights_data.method,
    fights_data.ending_round_num
FROM 
    event_data
INNER JOIN fighters_data 
    ON (event_data.event_id = fighters_data.event_id) 
INNER JOIN fights_data 
    ON (event_data.event_id = fights_data.event_id)
    AND (fighters_data.fight_id = fights_data.fight_id);
