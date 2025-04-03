# Career Progression App - Backend

This is the Django REST Framework API for the Progression application.

## Prerequisites

- **Git:** To clone the repository.
- **Docker Desktop:** To run the application environment using Docker Compose. ([https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/))
- **Python:** (Optional, for local commands) Version 3.13+ recommended.
- **pip:** Comes with Python.

## Getting Started (Docker Compose - Recommended)

This is the easiest way to run the full application stack (Frontend, Backend, Database).

1.  **Create Workspace Folder:** Make a main directory for the project on your computer.
    ```bash
    mkdir project-workspace
    cd project-workspace
    ```
2.  **Clone Repositories:** Clone both the frontend and backend repositories **inside** the workspace folder. Make sure they are named `frontend` and `backend`.
    ```bash
    git clone https://github.com/amarnuhovicbt/career-progression-web.git frontend
    git clone https://github.com/amarnuhovicbt/career-progression-api.git backend
    ```
3.  **Add `docker-compose.yml`:** Get the `docker-compose.yml` file (see content below) and place it directly inside your `project-workspace` folder.
4.  **Run Docker Compose:** Navigate **back up** to the `project-workspace` directory (the one containing `docker-compose.yml`). Run:
    ```bash
    docker-compose up --build
    ```
    - The `--build` flag is needed the first time or if Dockerfiles change.
    - This will build images and start containers for the frontend, backend, and database.
5.  **Access Application:** The backend is typically accessed via the frontend at `http://localhost:3000`.

### 🗂 Project Directory Layout

    project-workspace/
    ├── frontend/            <-- Cloned frontend repo (git clone ... frontend)
    │   └── ...
    ├── backend/                 <-- Cloned backend repo (git clone ... backend)
    │   └── ...
    └── docker-compose.yml   <-- The file that runs everything

## Available Scripts (Local)

- `cd backend`
- `python -m venv venv`
- `.\venv\Scripts\Activate.ps1`
- `pip install -r requirements.txt` - if not already
- `python manage.py runserver 0.0.0.0:8000`

## Docker Compose File (`docker-compose.yml`)

This file should be placed in the parent `project-workspace` directory.

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: skillapp-db
    volumes:
      - postgres-data:/var/lib/postgresql/data/
    env_file:
      - ./backend/.env
    environment:
      POSTGRES_DB: skillapp_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5433:5432"
    networks:
      - skillapp-network

  backend:
    build:
      context: ./backend
    container_name: skillapp-backend
    command: >
      sh -c "echo 'Waiting for database...' && sleep 5 &&
              python manage.py migrate &&
              echo 'Starting Django development server...' &&
              python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
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
    ports:
      - "3000:3000"
    command: npm run dev -- --host 0.0.0.0
    env_file:
      - ./frontend/.env
    environment:
      NUXT_HOST: 0.0.0.0
      NUXT_PORT: 3000
    depends_on:
      - backend
    networks:
      - skillapp-network

networks:
  skillapp-network:
    driver: bridge

volumes:
  postgres-data:
```
