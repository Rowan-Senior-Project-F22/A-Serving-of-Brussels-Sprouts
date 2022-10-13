#!/bin/bash


# Remove all prior migrations and load database with music data from the specified csv file

rm -f db.sqlite3 recommender/migrations/0*.py recommender/migrations/__pycache__/0*.pyc


# Initial migration ...
python manage.py makemigrations && python manage.py migrate
python manage.py makemigrations recommender && python manage.py migrate recommender



# Now load music data from the csv file into Django's database
# It will ask you for the music data file name

python manage.py shell -c "import importdata" 

echo "*********************************************"
echo "If needed, now create a super user"

# Windows: Remove the # at the beginning of the line below
#$SHELL
