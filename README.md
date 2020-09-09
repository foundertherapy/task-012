# task-012


# Setup
```bash
docker-compose build
docker-compose up -d
docker-compose exec time_tracking sh -c "python manage.py migrate"
docker-compose exec time_tracking sh -c "python manage.py loaddata fixtures/users.json"
docker-compose exec time_tracking sh -c "python manage.py compilemessages"
docker-compose exec time_tracking sh -c "python manage.py createcachetable"
docker-compose exec time_tracking sh -c "python manage.py test && flake8" # run the tests and flake8
```
