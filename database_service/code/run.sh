#!bin/bash

python3 -u /code/update_database.py &
# python3 -u /code/database_recorder.py

tail -f /dev/null