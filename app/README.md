# Project deployment

## Project structure

```
├── app
│   ├── .env
│   ├── Dockerfile
│   ├── README.md
│   ├── alembic
│   │   ├── README
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions
│   │       └── 31a78aaaf8e9_models.py
│   ├── alembic.ini
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logger_config.py
│   ├── main.py
│   ├── pyproject.toml
│   ├── tests
│   │   ├── __init__.py
│   │   └── test_users.py
│   ├── users
│   │   ├── __init__.py
│   │   ├── infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── api_client.py
│   │   │   └── repository.py
│   │   ├── interfaces.py
│   │   ├── models.py
│   │   ├── service.py
│   │   └── tasks.py
│   └── uv.lock
├── docker-compose.yml
└── postgresql-db
    ├── .pg-env
    └── data
```

## 1. Prerequisites

Before you begin, make sure you have **Docker** and **Docker Compose** installed on your system.

## 2. Project Setup

1. In the project's root directory (where `docker-compose.yml` is located),, create a folder named `app`.
2. Place all files from the project repository (the application source code) into **this** folder.
3. Make sure your `docker-compose.yml` file includes the following services configuration:

```bash
services:
  feeder-db:
    restart: always
    container_name: feeder-db
    image: postgres:16
    env_file: ./postgresql-db/.pg-env
    ports:
      - "5433:5432"
    volumes:
      - ./postgresql-db/data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  feeder-broker:
    image: rabbitmq:3.13-management-alpine
    container_name: feeder-broker
    restart: always
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 10s
      timeout: 5s
      retries: 5
      
  feeder-app:
    build:
      context: ./app
      dockerfile: Dockerfile
    container_name: feeder-app
    depends_on:
      feeder-db:
        condition: service_healthy
      feeder-broker:
        condition: service_healthy
    env_file: ./app/.env
    command: sh -c "alembic upgrade head && python main.py"

  feeder-worker:
    build:
      context: ./app
      dockerfile: Dockerfile
    container_name: feeder-worker
    depends_on:
      feeder-db:
        condition: service_healthy
      feeder-broker:
        condition: service_healthy
    env_file: ./app/.env
    command: celery -A users.tasks worker -l info

  feeder-beat:
    build:
      context: ./app
      dockerfile: Dockerfile
    container_name: feeder-beat
    depends_on:
      feeder-db:
        condition: service_healthy
      feeder-broker:
        condition: service_healthy
    env_file: ./app/.env
    command: celery -A users.tasks beat -l info


```

## 3. Database Configuration

1.  In the project's root directory (where `docker-compose.yml` is located), navigate to the `postgresql-db` folder.
2.  Create an empty directory named **`data`** and a file named **`.pg-env`**.
3.  Open the **`.pg-env`** file and add the following environment variables:

```ini
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=feeder_db
```

## 4. Application Configuration

1.  Navigate to the **`app`** folder.
2.  Create a file named **`.env`**.
3.  Open the **`.env`** file and add the following environment variables:

```ini
# Postgres settings
# DB_HOST must match the service name in docker-compose.yml
DB_HOST=feeder-db
DB_PORT=5432
DB_USER=user
DB_PASSWORD=password
DB_NAME=feeder_db

# Celery broker settings
# BROKER_HOST must match the service name in docker-compose.yml
BROKER_HOST=feeder-broker
BROKER_PORT=5672
BROKER_USER=guest
BROKER_PASSWORD=guest

# General settings
DEBUG=True
LOG_DIR=logs

# External API URLs
JSON_PLACEHOLDER_URL="https://jsonplaceholder.typicode.com"
FAKERAPI_URL="https://fakerapi.it/api/v2"
```

## 5. Running the Project
Once you have completed all the previous steps, return to the project's root directory (in **`docker-compose.yml`** level) and run the following command:

**`docker compose up --build`**
