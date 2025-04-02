# Career Progression App - Backend API

This is the Django REST Framework API for the Progression application.

## Prerequisites

* **Git:** To clone the repository.
* **Docker Desktop:** To run the application environment using Docker Compose. ([https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/))
* **Python:** (Optional, for local commands) Version 3.13+ recommended.
* **pip:** Comes with Python.

## Getting Started (Docker Compose - Recommended)

This is the easiest way to run the full application stack (Frontend, Backend, Database).

1.  **Create Workspace Folder:** Make a main directory for the project on your computer.
    ```bash
    mkdir project-workspace
    cd project-workspace
    ```
2.  **Clone Repositories:** Clone both the frontend and backend repositories **inside** the workspace folder. Make sure they are named `frontend` and `api`.
    ```bash
    git clone https://github.com/amarnuhovicbt/career-progression-web.git frontend
    git clone https://github.com/amarnuhovicbt/career-progression-api.git api
    ```
3.  **Add `docker-compose.yml`:** Get the `docker-compose.yml` file (see content below) and place it directly inside your `project-workspace` folder.
4.  **Run Docker Compose:** Navigate **back up** to the `project-workspace` directory (the one containing `docker-compose.yml`). Run:
    ```bash
    docker-compose up --build
    ```
    * The `--build` flag is needed the first time or if Dockerfiles change.
    * This will build images and start containers for the frontend, backend, and database.
5.  **Access Application:** The API is typically accessed via the frontend at `http://localhost:3000`. You can test the health check directly at `http://localhost:8000/api/health/`.


project-workspace/
├── frontend/            <-- Cloned frontend repo (git clone ... frontend)
│   └── ...
├── api/                 <-- Cloned backend repo (git clone ... api)
│   └── ...
└── docker-compose.yml   <-- The file that runs everything

## Available Scripts (Local)

* `cd api`
* `python -m venv venv`
* `.\venv\Scripts\Activate.ps1`
* `pip install -r requirements.txt` - if not already
* `python manage.py runserver 0.0.0.0:8000`

## Docker Compose File (`docker-compose.yml`)

This file should be placed in the parent `project-workspace` directory.

```yaml
services:
  # Database Service (PostgreSQL)
  db:
    image: postgres:16-alpine
    container_name: skillapp-db
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - ./api/.env
    # environment:
    #   POSTGRES_DB: ${POSTGRES_DB}
    #   POSTGRES_USER: ${POSTGRES_USER}
    #   POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5433:5432" 
    networks:
      - skillapp-network

  # Backend API Service (Django)
  api:
    build:
      context: ./api 
    container_name: skillapp-api
    command: > 
     sh -c "echo 'Waiting for database...' && sleep 5 &&
             python manage.py migrate &&
             echo 'Starting Django development server...' &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./api:/app 
    ports:
      - "8000:8000" 
    env_file:
      - ./api/.env 
    depends_on:
      - db 
    networks:
      - skillapp-network

  frontend:
    build:
      context: ./frontend
      target: builder 
    container_name: skillapp-frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.nuxt
      #- /app/.output
    ports:
      - "3000:3000"
    command: npm run dev -- --host 0.0.0.0
    env_file:
      - ./frontend/.env
    environment:
      API_BASE_URL: http://api:8000/api
      NUXT_HOST: 0.0.0.0
      NUXT_PORT: 3000
    depends_on:
      - api
    networks:
      - skillapp-network

networks:
  skillapp-network:
    driver: bridge

volumes:
  postgres_data: