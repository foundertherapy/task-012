# task-012


# Setup
```bash
docker-compose build
docker-compose run --rm app sh -c "python manage.py migrate"
docker-compose run --rm app sh -c "python manage.py loaddata fixtures/users.json"
docker-compose run --rm app sh -c "python manage.py compilemessages"
docker-compose run --rm app sh -c "python manage.py test && flake8" # run the tests and flake8
docker-compose up
```
