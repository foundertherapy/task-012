# task-012


# Setup
```bash
docker-compose build
docker-compose run app sh -c "python manage.py migrate"
docker-compose run app sh -c "python manage.py loaddata users-fixture.json"
docker-compose up
```
