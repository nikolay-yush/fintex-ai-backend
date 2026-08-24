# Docker CLI — Quick Reference

## Docker Status

| Command | Purpose |
|---|---|
| `docker version` | Show Docker client/server version |
| `docker info` | Show Docker system information |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers |
| `docker images` | List local images |
| `docker system df` | Show Docker disk usage |

---

sudo docker compose --env-file .env.dev build backend
sudo docker compose --env-file .env.dev up -d

-----
docker compose \
  --env-file .env.test \
  -f docker-compose.test.yml \
  config

 docker compose \
  --env-file .env.test \
  -f docker-compose.test.yml \
  up -d --build

docker compose \
  -f docker-compose.test.yml \
  ps
  

# Images

## Pull image

```bash
docker pull <image>:<tag>
```

Example:

```bash
docker pull postgres:15-alpine
```

## List images

```bash
docker images
```

## Remove image

```bash
docker rmi <image>
```

## Build image

```bash
docker build -t <name>:<tag> .
```

Example:

```bash
docker build -t fintex-api:latest .
```

---

# Containers

## Run

```bash
docker run <image>
```

Run in background:

```bash
docker run -d <image>
```

Assign name:

```bash
docker run -d \
    --name postgres \
    postgres:15-alpine
```

Map ports:

```bash
docker run -d \
    --name postgres \
    -p 5432:5432 \
    postgres:15-alpine
```

Pass environment variables:

```bash
docker run -d \
    --name postgres \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=fintex_ai \
    postgres:15-alpine
```

---

# Container Lifecycle

| Command | Purpose |
|---|---|
| `docker start <container>` | Start stopped container |
| `docker stop <container>` | Stop container |
| `docker restart <container>` | Restart container |
| `docker pause <container>` | Pause container |
| `docker unpause <container>` | Resume container |
| `docker rm <container>` | Remove stopped container |
| `docker rm -f <container>` | Force remove container |

Example:

```bash
docker stop postgres
docker start postgres
docker restart postgres
```

---

# Inspect Containers

## Running containers

```bash
docker ps
```

## All containers

```bash
docker ps -a
```

## Detailed information

```bash
docker inspect <container>
```

## Container processes

```bash
docker top <container>
```

## Resource usage

```bash
docker stats
```

Specific container:

```bash
docker stats <container>
```

---

# Logs

Show logs:

```bash
docker logs <container>
```

Follow logs:

```bash
docker logs -f <container>
```

Last 100 lines:

```bash
docker logs --tail 100 <container>
```

Logs since a specific time:

```bash
docker logs --since 10m <container>
```

Useful combination:

```bash
docker logs -f --tail 100 <container>
```

---

# Execute Commands Inside Container

Open shell:

```bash
docker exec -it <container> sh
```

If Bash exists:

```bash
docker exec -it <container> bash
```

Run one command:

```bash
docker exec <container> <command>
```

Example:

```bash
docker exec postgres pg_isready
```

---

# Copy Files

Copy from host to container:

```bash
docker cp ./file.txt <container>:/app/file.txt
```

Copy from container to host:

```bash
docker cp <container>:/app/file.txt ./file.txt
```

---

# Ports

Show published ports:

```bash
docker port <container>
```

Example:

```bash
docker port postgres
```

Typical output:

```text
5432/tcp -> 0.0.0.0:5432
```

---

# Environment Variables

Show container environment:

```bash
docker inspect <container>
```

Filter environment:

```bash
docker inspect \
    --format='{{range .Config.Env}}{{println .}}{{end}}' \
    <container>
```

---

# Networks

List networks:

```bash
docker network ls
```

Inspect network:

```bash
docker network inspect <network>
```

Create network:

```bash
docker network create app-network
```

Connect container:

```bash
docker network connect app-network <container>
```

Disconnect:

```bash
docker network disconnect app-network <container>
```

---

# Volumes

List volumes:

```bash
docker volume ls
```

Create volume:

```bash
docker volume create postgres-data
```

Inspect volume:

```bash
docker volume inspect postgres-data
```

Remove volume:

```bash
docker volume rm postgres-data
```

> Removing a volume can permanently delete stored data.

---

# Bind Mounts

Mount local directory:

```bash
docker run -d \
    -v ./data:/app/data \
    <image>
```

Read-only mount:

```bash
docker run -d \
    -v ./config:/app/config:ro \
    <image>
```

---

# Docker Compose

## Start services

```bash
docker compose up
```

Background:

```bash
docker compose up -d
```

Build and start:

```bash
docker compose up -d --build
```

## Stop services

```bash
docker compose down
```

Stop and remove volumes:

```bash
docker compose down -v
```

> `-v` removes Compose volumes and can delete database data.

---

# Compose Status

List services:

```bash
docker compose ps
```

Show all containers:

```bash
docker compose ps -a
```

Service logs:

```bash
docker compose logs <service>
```

Follow logs:

```bash
docker compose logs -f <service>
```

All logs:

```bash
docker compose logs -f
```

---

# Compose Commands

Execute command inside service:

```bash
docker compose exec <service> <command>
```

Example:

```bash
docker compose exec postgres psql \
    -U postgres \
    -d fintex_ai
```

Open shell:

```bash
docker compose exec <service> sh
```

Restart service:

```bash
docker compose restart <service>
```

Stop service:

```bash
docker compose stop <service>
```

Start service:

```bash
docker compose start <service>
```

---

# Compose Build

Build services:

```bash
docker compose build
```

Build specific service:

```bash
docker compose build api
```

Rebuild without cache:

```bash
docker compose build --no-cache
```

Build and start:

```bash
docker compose up -d --build
```

---

# Compose Configuration

Validate Compose file:

```bash
docker compose config
```

Show resolved configuration:

```bash
docker compose config
```

Useful for checking:

- environment variables;
- service configuration;
- volumes;
- networks;
- interpolated values.

---

# PostgreSQL + Docker

Connect to PostgreSQL:

```bash
docker compose exec postgres \
    psql \
    -U postgres \
    -d fintex_ai
```

Check PostgreSQL:

```bash
docker compose exec postgres \
    pg_isready \
    -U postgres
```

Show PostgreSQL logs:

```bash
docker compose logs -f postgres
```

---

# Redis + Docker

Open Redis CLI:

```bash
docker compose exec redis redis-cli
```

Check Redis:

```bash
docker compose exec redis redis-cli PING
```

With password:

```bash
docker compose exec redis \
    redis-cli -a <password>
```

---

# Cleanup

Remove stopped containers:

```bash
docker container prune
```

Remove unused images:

```bash
docker image prune
```

Remove unused volumes:

```bash
docker volume prune
```

Remove unused networks:

```bash
docker network prune
```

Remove unused Docker resources:

```bash
docker system prune
```

More aggressive:

```bash
docker system prune -a
```

> Always check what will be removed before using cleanup commands.

---

# Dangerous Commands

| Command | Risk |
|---|---|
| `docker rm -f <container>` | Force removes container |
| `docker rmi <image>` | Removes image |
| `docker volume rm <volume>` | Can permanently delete data |
| `docker compose down -v` | Removes Compose volumes |
| `docker system prune` | Removes unused resources |
| `docker system prune -a` | Removes unused images and resources |

---

# Most Used Commands

### Containers

```bash
docker ps
docker ps -a

docker start <container>
docker stop <container>
docker restart <container>
```

### Logs

```bash
docker logs -f --tail 100 <container>
```

### Shell

```bash
docker exec -it <container> sh
```

### Inspect

```bash
docker inspect <container>
docker stats
```

### Compose

```bash
docker compose up -d
docker compose up -d --build

docker compose ps
docker compose logs -f

docker compose exec <service> sh

docker compose restart <service>

docker compose down
```

### Cleanup

```bash
docker container prune
docker image prune
docker volume prune
docker system prune
```