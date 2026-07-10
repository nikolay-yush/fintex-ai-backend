## 01. Architecture

## Overview choice - **Feature-Based Architecture**.

Each business feature is isolated into its own module and contains its models, schemas, services, repositories, routers, and dependencies.

### Why

* Easy to scale
* High cohesion
* Low coupling
* Clear project structure
* Independent feature development

---

## Project Structure

```
app/
├── core/
├── shared/
├── features/
│   ├── auth/
│   ├── users/
│   ├── wallets/
│   ├── transactions/
│   └── categories/
└── main.py
```
