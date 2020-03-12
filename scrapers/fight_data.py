# Outline:

# Need to join the eventid table to the event_data table
# The purpose is to get the lowest row_idx value that joins to the event_data
# This will be the most recent event for which the event_data was scraped
# Knowing this I then need to pull down all the row_idx that are lower
# Then I need to simply pull down all the event id that are associated with the row_idx
# If I have the list of the event_ids with missing data
# Run the already defined functions from the init_fight_data program on the new event ids