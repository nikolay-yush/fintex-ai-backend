# Redis — Technical Reference & Cheat Sheet

Redis is an in-memory data store commonly used for caching, temporary data, counters, rate limiting, distributed locks, Pub/Sub, and Streams.

---

## 1. Why Redis?

Redis is useful when data requires:

- very fast access;
- automatic expiration with TTL;
- atomic operations;
- temporary storage;
- distributed coordination;
- caching.

Typical architecture:

```text
FastAPI
├── PostgreSQL
│   └── Permanent application data
│
└── Redis
    ├── Cache
    ├── Temporary tokens
    ├── Sessions
    ├── Rate limits
    ├── Distributed locks
    └── Streams
```

**PostgreSQL is usually the source of truth. Redis is an auxiliary fast storage layer.**

---

## 2. Common Use Cases

| Use case | Redis feature |
|---|---|
| Cache | Strings / Hashes |
| Temporary tokens | Strings + TTL |
| Sessions | Strings / Hashes + TTL |
| Rate limiting | Counters + TTL |
| Counters | `INCR` / `INCRBY` |
| Distributed locks | `SET ... NX EX` |
| Unique values | Sets |
| Ranking | Sorted Sets |
| Simple queues | Lists |
| Real-time messages | Pub/Sub |
| Reliable event processing | Streams |

---

# 3. Docker

## Start Redis

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:latest
```

Check container:

```bash
docker ps
```

## Open redis-cli

```bash
docker exec -it redis redis-cli
```

## Run a command directly

```bash
docker exec redis redis-cli PING
```

Expected:

```text
PONG
```

## Redis with password

```bash
docker exec -it redis redis-cli -a <password>
```

---

# 4. Server Commands

### Health check

```redis
PING
```

### Server information

```redis
INFO
```

Useful sections:

```redis
INFO server
INFO memory
INFO clients
INFO stats
INFO replication
```

### Number of keys

```redis
DBSIZE
```

### Select database

```redis
SELECT 1
```

> Redis Cluster supports only database `0`. Do not build application architecture around multiple logical databases.

### Delete current database

```redis
FLUSHDB
```

### Delete all databases

```redis
FLUSHALL
```

> `FLUSHDB` and `FLUSHALL` are destructive commands. Use them carefully.

---

# 5. Keys

## Create / update

```redis
SET user:100:name "Alex"
```

## Read

```redis
GET user:100:name
```

## Check existence

```redis
EXISTS user:100:name
```

## Delete

```redis
DEL user:100:name
```

## Get value type

```redis
TYPE user:100
```

---

# 6. Key Search

## `KEYS`

```redis
KEYS user:*
```

Useful for local development.

**Do not use `KEYS` on large production datasets.**

---

## `SCAN`

Use `SCAN` for production-safe key iteration:

```redis
SCAN 0 MATCH user:* COUNT 100
```

Continue using the returned cursor:

```redis
SCAN <cursor> MATCH user:* COUNT 100
```

Stop when the cursor becomes:

```text
0
```

---

# 7. TTL

Redis can automatically delete keys after a specified time.

## Set TTL

```redis
EXPIRE session:123 3600
```

## Check TTL

```redis
TTL session:123
```

Results:

```text
3600   # seconds remaining
-1     # key has no expiration
-2     # key does not exist
```

## Remove expiration

```redis
PERSIST session:123
```

---

## Set value with TTL

Preferred approach:

```redis
SET session:123 "active" EX 3600
```

Milliseconds:

```redis
SET session:123 "active" PX 5000
```

```text
EX = seconds
PX = milliseconds
```

---

# 8. Conditional SET

Create a key only if it does not already exist:

```redis
SET lock:order:123 "worker-1" NX EX 30
```

Options:

```text
NX → set only if key does not exist
EX → expiration in seconds
PX → expiration in milliseconds
```

This is commonly used as a building block for distributed locks.

---

# 9. Strings

Strings are the simplest Redis data type.

```redis
SET app:name "FintexAI"
GET app:name
```

## Counters

```redis
INCR page_views
```

```redis
INCRBY page_views 10
```

```redis
DECR page_views
```

```redis
DECRBY page_views 5
```

Common uses:

```text
cache
counters
flags
tokens
serialized JSON
simple values
```

---

# 10. Hashes

Hashes store field-value pairs.

Example:

```text
user:100
├── email
├── full_name
└── role
```

## Set fields

```redis
HSET user:100 \
  email "alex@example.com" \
  full_name "Alex" \
  role "user"
```

## Get field

```redis
HGET user:100 email
```

## Get all fields

```redis
HGETALL user:100
```

## Delete field

```redis
HDEL user:100 role
```

## Check field

```redis
HEXISTS user:100 email
```

## Increment field

```redis
HINCRBY user:100 login_count 1
```

---

# 11. Lists

Lists are ordered collections.

Useful for simple queues.

## Push

```redis
LPUSH tasks "task_1"
RPUSH tasks "task_2"
```

## Pop

```redis
LPOP tasks
RPOP tasks
```

## Get range

```redis
LRANGE tasks 0 -1
```

---

# 12. Sets

Sets contain unique values.

## Add

```redis
SADD user:100:roles admin user
```

## Get members

```redis
SMEMBERS user:100:roles
```

## Check membership

```redis
SISMEMBER user:100:roles admin
```

## Remove

```redis
SREM user:100:roles admin
```

Useful for:

```text
roles
permissions
tags
unique users
membership checks
```

---

# 13. Sorted Sets

Sorted Sets store unique values with a numeric score.

```redis
ZADD leaderboard 1500 user:100
ZADD leaderboard 2100 user:101
ZADD leaderboard 1800 user:102
```

Top 10:

```redis
ZREVRANGE leaderboard 0 9 WITHSCORES
```

All items:

```redis
ZRANGE leaderboard 0 -1 WITHSCORES
```

Useful for:

```text
leaderboards
ranking
priority queues
scheduled tasks
score-based ordering
```

---

# 14. Transactions

Redis transactions use:

```text
MULTI
EXEC
DISCARD
WATCH
```

Example:

```redis
MULTI
SET balance:user:100 500
INCR transactions:user:100
EXEC
```

`WATCH` provides optimistic concurrency control:

```redis
WATCH balance:user:100
```

---

# 15. Distributed Locks

Basic lock pattern:

```redis
SET lock:order:123 "worker-1" NX EX 30
```

If Redis returns:

```text
OK
```

the lock was acquired.

If Redis returns:

```text
(nil)
```

the lock already exists.

### Important

The lock owner must verify ownership before deleting the lock. Do not blindly execute:

```redis
DEL lock:order:123
```

in a multi-worker system.

---

# 16. Rate Limiting

Simple counter-based rate limit:

```redis
INCR rate:user:100
EXPIRE rate:user:100 60
```

Concept:

```text
Request
   │
   ▼
INCR counter
   │
   ├── within limit → allow
   │
   └── over limit   → reject
```

Production systems may use more precise algorithms such as:

```text
Fixed Window
Sliding Window
Token Bucket
Leaky Bucket
```

---

# 17. Caching

Typical cache flow:

```text
FastAPI
   │
   ▼
Redis
   │
   ├── Cache hit → return value
   │
   └── Cache miss
          │
          ▼
      PostgreSQL / API
          │
          ▼
        Redis
```

Example:

```redis
SET cache:currency:usd '{"rate":41.20}' EX 300
```

Read:

```redis
GET cache:currency:usd
```

Use TTL to prevent stale data from living indefinitely.

---

# 18. Pub/Sub

Publisher:

```redis
PUBLISH notifications "User registered"
```

Subscriber:

```redis
SUBSCRIBE notifications
```

Useful for real-time application events.

### Important

Pub/Sub is **not a durable message queue**.

If a subscriber is disconnected when a message is published, the message is lost.

For reliable processing, use **Redis Streams**.

---

# 19. Streams

Add an event:

```redis
XADD events * type "user_registered" user_id "100"
```

Read events:

```redis
XREAD COUNT 10 STREAMS events 0
```

## Consumer Groups

Create group:

```redis
XGROUP CREATE events workers 0 MKSTREAM
```

Read as consumer:

```redis
XREADGROUP GROUP workers worker-1 COUNT 10 STREAMS events >
```

Acknowledge:

```redis
XACK events workers <message_id>
```

Use Streams when events must survive consumer downtime and require controlled processing.

---

# 20. Key Naming Convention

Use `:` as a namespace separator.

Recommended:

```text
<app>:<domain>:<resource>:<identifier>
```

Examples:

```text
fintex:user:100
fintex:cache:wallet:100
fintex:rate_limit:user:100
fintex:lock:transaction:100
fintex:auth:refresh:<token_id>
fintex:auth:password_reset:<token_id>
```

For fields:

```text
fintex:user:100:session
```

Keep key names:

- predictable;
- consistent;
- easy to scan;
- namespaced by application.

---

# 21. Debugging

## Memory

```redis
INFO memory
```

## Clients

```redis
INFO clients
```

## Statistics

```redis
INFO stats
```

## Key count

```redis
DBSIZE
```

## Inspect a key

```redis
TYPE <key>
TTL <key>
EXISTS <key>
```

---

# 22. Dangerous Commands

Use with caution:

```redis
FLUSHDB
FLUSHALL
KEYS *
DEL
```

Especially:

```redis
FLUSHALL
```

which deletes all keys from all Redis databases.

For key inspection prefer:

```redis
SCAN 0 MATCH fintex:* COUNT 100
```

---

# 23. Quick Cheat Sheet

| Command | Purpose |
|---|---|
| `PING` | Health check |
| `INFO` | Server information |
| `DBSIZE` | Key count |
| `SET` | Create / update value |
| `GET` | Read value |
| `DEL` | Delete key |
| `EXISTS` | Check key |
| `TYPE` | Get value type |
| `EXPIRE` | Set TTL |
| `TTL` | Check TTL |
| `PERSIST` | Remove TTL |
| `SCAN` | Iterate keys |
| `KEYS` | Search keys — development only |
| `INCR` | Increment counter |
| `INCRBY` | Increment by amount |
| `HSET` | Set Hash fields |
| `HGET` | Get Hash field |
| `HGETALL` | Get Hash |
| `LPUSH` | Push to List |
| `LPOP` | Pop from List |
| `SADD` | Add to Set |
| `SMEMBERS` | Get Set members |
| `SISMEMBER` | Check Set membership |
| `ZADD` | Add Sorted Set item |
| `ZRANGE` | Read Sorted Set |
| `MULTI` | Start transaction |
| `EXEC` | Execute transaction |
| `WATCH` | Watch keys |
| `PUBLISH` | Publish message |
| `SUBSCRIBE` | Subscribe to channel |
| `XADD` | Add Stream event |
| `XREAD` | Read Stream |
| `XGROUP` | Manage consumer group |
| `XACK` | Acknowledge event |

---

# 24. Core Rules

1. **Use PostgreSQL as the source of truth for permanent data.**
2. **Use Redis for fast or temporary data.**
3. **Use TTL for temporary data.**
4. **Prefer `SCAN` over `KEYS` in production.**
5. **Use atomic commands such as `INCR` when possible.**
6. **Use `SET ... NX EX ...` for lock primitives.**
7. **Do not treat Pub/Sub as a durable queue.**
8. **Use Streams for reliable event processing.**
9. **Use consistent key namespaces.**
10. **Never run destructive commands accidentally in production.**