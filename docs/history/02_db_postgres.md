# 02. Database — PostgreSQL (Docker)

## Overview

PostgreSQL runs inside a Docker container managed by `docker-compose.yml`.

The application connects to the database using the Docker service name:

```text
Host: db
Port: 5432
Database: fintex_ai
User: postgres
```

---

## Docker Commands

# Command                                   |  Description                                              
-----------------------------------------   |  -------------------------------------------------------- 
`docker compose up -d`                      |  Start all services in the background.                    
`docker compose down`                       |  Stop and remove all containers.                          
`docker compose down -v`                    |  Stop containers and remove all volumes (reset database). 
`docker compose ps`                         |  Display the status of running containers.                
`docker compose logs -f db`                 |  Stream PostgreSQL logs in real time.                     
`docker compose exec db pg_isready`         |  Verify that PostgreSQL is ready to accept connections.   
`docker compose exec db psql -U postgres`   |  Open the PostgreSQL interactive shell (`psql`).          
`docker compose exec db sh`                 |  Open a shell inside the database container.              

---

## Expected Status

```text
$ docker compose ps

NAME             STATUS
fintex_ai_db     Up
```

---

## Health Check

```text
$ docker compose exec db pg_isready

accepting connections
```

---

## Exit Interactive Shells

### PostgreSQL (`psql`)

```text
\q
```

### Container Shell

```bash
exit
```
