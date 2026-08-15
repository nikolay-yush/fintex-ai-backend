# Redis CLI — Quick Reference


# Connect to Redis
sudo docker exec -it fintex_ai_redis \
  redis-cli -a 'REDIS_PASSWORD'


## Connection

| Command | Purpose |
|---|---|
| `redis-cli` | Connect to local Redis |
| `redis-cli -h <host> -p <port>` | Connect using host and port |
| `redis-cli -a <password>` | Connect with password |
| `redis-cli -h <host> -p <port> -a <password>` | Connect using host, port, and password |
| `docker exec -it <container> redis-cli` | Open Redis CLI inside Docker |
| `docker exec <container> redis-cli PING` | Check Redis inside Docker |

---

## Server

| Command | Purpose |
|---|---|
| `PING` | Check connection |
| `INFO` | Show server information |
| `INFO memory` | Memory information |
| `INFO clients` | Connected clients |
| `INFO stats` | Server statistics |
| `DBSIZE` | Number of keys in current database |
| `SELECT <db>` | Switch logical database |

---

## Keys

| Command | Purpose |
|---|---|
| `SET <key> <value>` | Create or update a value |
| `GET <key>` | Get a value |
| `EXISTS <key>` | Check if key exists |
| `DEL <key>` | Delete key |
| `TYPE <key>` | Get key type |
| `SCAN 0 MATCH <pattern>` | Safely iterate matching keys |
| `KEYS <pattern>` | Find matching keys — development only |

### Examples

```redis
SET user:100:name "Alex"
GET user:100:name

EXISTS user:100:name
TYPE user:100:name

DEL user:100:name

SCAN 0 MATCH user:* COUNT 100
```

> Prefer `SCAN` over `KEYS` in production.

---

## TTL / Expiration

| Command | Purpose |
|---|---|
| `SET <key> <value> EX <seconds>` | Set value with TTL |
| `SET <key> <value> PX <milliseconds>` | Set value with millisecond TTL |
| `EXPIRE <key> <seconds>` | Set TTL |
| `TTL <key>` | Check remaining TTL |
| `PERSIST <key>` | Remove expiration |

### Examples

```redis
SET session:123 "active" EX 3600

TTL session:123

EXPIRE session:123 600

PERSIST session:123
```

TTL results:

```text
-1 → key exists without expiration
-2 → key does not exist
```

---

## Counters

| Command | Purpose |
|---|---|
| `INCR <key>` | Increment by `1` |
| `INCRBY <key> <amount>` | Increment by amount |
| `DECR <key>` | Decrement by `1` |
| `DECRBY <key> <amount>` | Decrement by amount |

### Examples

```redis
INCR page_views
INCRBY page_views 10

DECR active_users
DECRBY active_users 5
```

---

## Hashes

| Command | Purpose |
|---|---|
| `HSET <key> <field> <value>` | Set field |
| `HGET <key> <field>` | Get field |
| `HGETALL <key>` | Get all fields |
| `HDEL <key> <field>` | Delete field |
| `HEXISTS <key> <field>` | Check field |
| `HINCRBY <key> <field> <amount>` | Increment numeric field |

### Examples

```redis
HSET user:100 email "alex@example.com" role "user"

HGET user:100 email

HGETALL user:100

HDEL user:100 role

HEXISTS user:100 email
```

---

## Lists

| Command | Purpose |
|---|---|
| `LPUSH <key> <value>` | Add to list head |
| `RPUSH <key> <value>` | Add to list tail |
| `LPOP <key>` | Remove from head |
| `RPOP <key>` | Remove from tail |
| `LRANGE <key> <start> <stop>` | Read list range |

### Example

```redis
LPUSH tasks "task_1"
RPUSH tasks "task_2"

LRANGE tasks 0 -1

LPOP tasks
RPOP tasks
```

---

## Sets

| Command | Purpose |
|---|---|
| `SADD <key> <value>` | Add value |
| `SMEMBERS <key>` | Get all values |
| `SISMEMBER <key> <value>` | Check membership |
| `SREM <key> <value>` | Remove value |

### Example

```redis
SADD user:100:roles admin user

SMEMBERS user:100:roles

SISMEMBER user:100:roles admin

SREM user:100:roles admin
```

---

## Sorted Sets

| Command | Purpose |
|---|---|
| `ZADD <key> <score> <value>` | Add value with score |
| `ZRANGE <key> <start> <stop>` | Read ascending |
| `ZREVRANGE <key> <start> <stop>` | Read descending |
| `ZRANGE ... WITHSCORES` | Include scores |

### Example

```redis
ZADD leaderboard 1500 user:100
ZADD leaderboard 2100 user:101

ZREVRANGE leaderboard 0 9 WITHSCORES
```

---

## Atomic / Conditional Operations

### Set only if key does not exist

```redis
SET lock:order:123 "worker-1" NX EX 30
```

```text
NX → only create if key does not exist
EX → expiration in seconds
```

Useful for distributed locks and similar coordination primitives.

---

## Transactions

| Command | Purpose |
|---|---|
| `MULTI` | Start transaction |
| `EXEC` | Execute transaction |
| `DISCARD` | Cancel transaction |
| `WATCH <key>` | Watch key for changes |

### Example

```redis
MULTI
SET user:100:status "active"
INCR user:100:updates
EXEC
```

---

## Pub/Sub

| Command | Purpose |
|---|---|
| `PUBLISH <channel> <message>` | Publish message |
| `SUBSCRIBE <channel>` | Subscribe to channel |
| `UNSUBSCRIBE <channel>` | Unsubscribe |

### Example

```redis
SUBSCRIBE notifications
```

In another client:

```redis
PUBLISH notifications "User registered"
```

> Pub/Sub is not a durable queue. Use Redis Streams when messages must be persisted for processing.

---

## Streams

| Command | Purpose |
|---|---|
| `XADD` | Add event |
| `XREAD` | Read events |
| `XGROUP CREATE` | Create consumer group |
| `XREADGROUP` | Read as consumer |
| `XACK` | Acknowledge event |

### Example

```redis
XADD events * type "user_registered" user_id "100"

XREAD COUNT 10 STREAMS events 0
```

---

## Dangerous Commands

| Command | Risk |
|---|---|
| `FLUSHDB` | Deletes all keys in current database |
| `FLUSHALL` | Deletes all keys in all databases |
| `KEYS *` | Can block Redis on large datasets |

Use carefully, especially in production.

---

## Most Used Commands

```redis
PING

SET key value
GET key
EXISTS key
DEL key

SET key value EX 3600
TTL key

SCAN 0 MATCH app:* COUNT 100

INCR counter

HSET user:100 role admin
HGET user:100 role
HGETALL user:100

SADD roles admin
SMEMBERS roles

ZADD leaderboard 100 user:100
ZREVRANGE leaderboard 0 9 WITHSCORES
```