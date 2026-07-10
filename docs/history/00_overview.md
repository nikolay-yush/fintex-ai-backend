# 00. Project Overview

## Project

*Fintex AI* - application that helps users manage income, expenses and financial statistics. It also integrates AI features to simplify expense tracking and financial analysis.

---

## Goals

* Manage personal finances
* Track income and expenses
* Generate financial statistics
* Support AI-powered assistance

---

## Tech Stack Map(backend)

# Component      |  Technology  
---------------  |  ----------------
Language         |  Python 3.12+  
Package manager  |  uv          
Framework        |  FastAPI 
HTTP server      |  Granian         
Database         |  PostgreSQL              
ORM              |  SQLAlchemy 2.x (Async)  
Migrations       |  Alembic                 
Validation       |  Pydantic v2             
Containerization |  Docker 
Authentication   |  JWT                     
API Docs         |  OpenAPI / Swagger  
Tests            |  Pytest     

---

## Architecture
`Feature-Based Architecture`

---

## Core Business Components

### 1. Wallets
*Represents a user's financial accounts or funding sources (e.g., bank accounts, credit cards, cash wallets, or crypto addresses).

### 2. Categories
A system for classifying financial activity into specific groups (e.g., "Food", "Rent", "Salary").

Enables budget planning, structures financial data, and powers analytics/reporting by grouping income and expenses.

### 3. Transactions
Records of individual financial movements or events inside the system.

Captures specific details (amount, timestamp, sender/receiver, type: *income, expense, or transfer*) and links **Wallets** to **Categories** to update balances.