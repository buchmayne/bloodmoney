# to run sql script from command line
PGPASSWORD=password psql -U postgres -d bloodmoneydb -h 127.0.0.1 -a -f join_fighters_fights_events_data.sql
