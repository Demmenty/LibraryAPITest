# Library Management API


## Technologies

Python, FastAPI, PostgreSQL, Alembic, Docker, Redis

## Installation

- create .env file in root with your settings according to .env.example

### Docker

- install docker

- run application
```
docker-compose up -d --build
```

- run migrations to set up database
```
docker exec -it api alembic -c alembic.ini upgrade head
```

- create admin if needed
```
docker exec -it api python -m app.main createadmin
```

### Local

- install PostgreSQL database
- install Redis database

- run application
```
uvicorn app.main:app
```

- run migrations to set up database
```
alembic -c alembic.ini upgrade head
```

- create admin if needed
```
python -m app.main createadmin
```
