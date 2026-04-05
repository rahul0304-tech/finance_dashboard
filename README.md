# Zordyvn Assignment: Finance Dashboard Backend

## Project Overview
This repository contains the backend implementation for the Finance Dashboard system, constructed to satisfy all the core assignment requirements natively. The framework provides a secure, role-based backend architecture for aggregating financial metrics, logging records, and managing user access parameters efficiently.

## Tech Stack & Architectural Rationale
We selected a modern, highly dependable Python stack to meet the assignment requirements flawlessly:
- **Django 6.x**: Chosen as the foundational framework due to its robust ORM and its `AbstractUser` functionality. This allowed us to deeply embed custom string roles (`VIEWER`, `ANALYST`, `ADMIN`) directly into the system infrastructure efficiently.
- **Django Rest Framework (DRF)**: Chosen for its speed turning Python models into functional, serialized REST architecture elements. Specifically, DRF's `ViewSet` maps allow us to bind custom granular `permissions` automatically.
- **REST Framework SimpleJWT**: Standard token generation module. We explicitly overrode its base classes in this architecture to manually isolate the critical refresh variable into an `HttpOnly` Set-Cookie payload, securing the module against XSS JavaScript injections.
- **DRF-Spectacular**: The optimal module for modern OpenAPI Version 3 compliance natively over older alternatives like `drf-yasg`. It hooks into DRF seamlessly to provide a visually clear Swagger interface mapping complex payloads structurally automatically.
- **SQLite3**: Chosen as the database structure for portability and rapid evaluation grading.

## Superuser Administration
An advanced root administrative account is precompiled into the database when running our initialization scripts. This bypasses structural safeguards explicitly to allow evaluators complete access:
- **Username**: `admin`
- **Password**: `admin`
- **Scope**: Native full Django Admin Access and API `ADMIN` capabilities unconditionally.

## Core Requirements Implemented

### 1. Role-Based Access Control (RBAC)
A custom Django User model was engineered, defining strict hierarchical scopes:
- **`VIEWER`**: Restricted specifically to aggregate overview dashboard outputs without access to underlying transactional data rows.
- **`ANALYST`**: Inherits standard dashboard properties natively alongside the additional authorization mapping explicit historic list queries dynamically.
- **`ADMIN`**: Endowed with granular CRUD execution capabilities allowing structural changes to user roles and parameters securely.

### 2. Advanced Security Implementations
The generic JWT `TokenObtainPairView` is overridden explicitly to intercept native parameters. It injects the `refresh` token directly into an `HttpOnly` payload. This effectively secures offline credentials reliably.

### 3. Database Soft Deletion Architecture
For `FinancialRecord` structural models, the inherent framework `delete()` method is overridden smoothly. Triggers executing `DELETE` requests apply logical `is_deleted = True` modifications instead, protecting against destructive data loss inherently.

### 4. Database Seeding Automation 
- **`schema.py`**: Triggers explicit baseline generic schema migrations cleanly natively.
- **`data.py`**: Purges outdated structural nodes and seeds the required baseline structures: Admin accounts, Analyst accounts, Viewers, alongside a robust dataset of 50 randomly plotted transactions mapping directly to the DB dynamically.

### 5. Input Validation & Error Handling
- **Input Validation**: The custom DRF Serializers rigorously validate payloads. We explicitly appended rules demanding `amount > 0` and stripping trailing whitespaces targeting categorical arrays mitigating garbage data injection.
- **Unified Custom Exceptions**: Rather than executing variable JSON schemas depending on the origin of the Python error, we wrote a `custom_exception_handler` wrapper formatting standard HTTP payloads uniformly (returning `success: false`, exact `status_code`, and a nested `details` logic tree universally).

## Local Assessment Deployment

**Prerequisites:** Python 3.10+, Django 6.0+, Django Rest Framework

```bash
# Activate the testing environment
.\venv\Scripts\activate

# Install all requested dependencies
pip install django djangorestframework djangorestframework-simplejwt django-filter drf-spectacular

# Apply explicit schemas mapped correctly
python schema.py

# Inject dummy data configurations and User structures automatically
python data.py

# Run the backend locally
python manage.py runserver
```

## Testing Interfaces
- **Interactive API Tester (Swagger):** `http://127.0.0.1:8000/swagger/`
- **Architectural UI Panel:** `http://127.0.0.1:8000/`
