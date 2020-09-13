# task-012

# Docker Setup
```bash
docker-compose build
docker-compose up -d
docker-compose exec time_tracking sh -c "python manage.py migrate"
docker-compose exec time_tracking sh -c "python manage.py loaddata fixtures/users.json"
docker-compose exec time_tracking sh -c "python manage.py compilemessages"
docker-compose exec time_tracking sh -c "python manage.py createcachetable"
docker-compose exec time_tracking sh -c "python manage.py test" # run the tests
docker-compose exec time_tracking sh -c "flake8" # run flake8
```

# PostgreSQL Environment variables
`DB_NAME`, `USER`, `PASSWORD`, `HOST`

