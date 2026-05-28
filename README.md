# Expense Tracker System

## Project Overview

The Expense Tracker System is a workspace-based expense management application built using:

* Django
* Django REST Framework (DRF)
* Django Templates
* Bootstrap 5

Employees can submit expenses with receipt uploads, while managers/admins can review, approve, or reject submitted expenses.

This project uses server-rendered templates instead of React.

---

# Tech Stack

## Backend

* Django
* Django REST Framework
* PostgreSQL / SQLite
* Django ORM

## Frontend

* Django Templates
* Bootstrap 5
* Vanilla JavaScript

## File Uploads

* Django FileField
* Receipt storage support

---

# Core Features

## Employee Features

* Submit expense
* Upload receipts
* View own expenses
* Filter expenses
* Delete submitted expenses
* Pagination support

## Manager/Admin Features

* View all workspace expenses
* Filter expenses
* Approve expenses
* Reject expenses with review notes
* Review dashboard

---

# Expense Model

## Fields

| Field        | Type          |
| ------------ | ------------- |
| workspace    | ForeignKey    |
| title        | CharField     |
| amount       | DecimalField  |
| category     | CharField     |
| description  | TextField     |
| receipt      | FileField     |
| status       | CharField     |
| submitted_by | ForeignKey    |
| reviewed_by  | ForeignKey    |
| reviewed_at  | DateTimeField |
| review_notes | TextField     |
| created_at   | DateTimeField |
| updated_at   | DateTimeField |

---

# Expense Categories

* Travel
* Meals
* Software
* Equipment
* Other

---

# Expense Status

* Submitted
* Approved
* Rejected

---

# Backend Tasks

# 1. Expense Model

## Tasks

* Create Expense model
* Add category choices
* Add status choices
* Add positive amount constraint
* Add receipt upload support
* Create migration
* Register model in Django admin

---

# 2. Serializers

## ExpenseSerializer

### Tasks

* Read serializer
* Include receipt URL
* Add read-only fields

## ExpenseWriteSerializer

### Tasks

* Validate title
* Validate amount > 0
* Validate category
* Validate receipt MIME type
* Validate receipt max size (10 MB)

---

# 3. ExpenseService

## Tasks

### submit_expense()

* Create expense
* Save uploaded receipt
* Default status = submitted

### approve_expense()

* Validate submitted state
* Set approved status
* Save reviewer
* Save reviewed_at

### reject_expense()

* Validate submitted state
* Require review_notes
* Save rejected status

### delete_expense()

* Delete uploaded file
* Prevent deleting approved expense
* Allow only owner/admin

---

# 4. DRF API Views

## ExpenseListCreateView

### Endpoints

GET:
`/api/v1/workspaces/{workspace_id}/expenses/`

POST:
`/api/v1/workspaces/{workspace_id}/expenses/`

### Tasks

* Return current user expenses
* Handle multipart/form-data
* Support filters
* Add pagination

---

## ExpenseDetailView

### Endpoints

GET:
`/api/v1/workspaces/{workspace_id}/expenses/{id}/`

DELETE:
`/api/v1/workspaces/{workspace_id}/expenses/{id}/`

### Tasks

* Owner/admin delete only
* Prevent deleting approved expenses

---

## ExpenseApproveView

### Endpoint

POST:
`/api/v1/workspaces/{workspace_id}/expenses/{id}/approve/`

### Tasks

* Admin only
* Approve submitted expenses only

---

## ExpenseRejectView

### Endpoint

POST:
`/api/v1/workspaces/{workspace_id}/expenses/{id}/reject/`

### Tasks

* Admin only
* review_notes required

---

## AdminExpenseListView

### Endpoint

GET:
`/api/v1/workspaces/{workspace_id}/expenses/all/`

### Tasks

* Admin-only access
* Return all workspace expenses
* Support filters
* Pagination

---

# Frontend Tasks

# 5. My Expenses Page

## URL

`/workspaces/{id}/expenses/`

## Tasks

* Bootstrap table
* Status badges
* Filters
* Pagination
* Receipt links
* Delete button
* Empty state
* Error state
* Responsive design

---

# 6. Submit Expense Form

## URL

`/workspaces/{id}/expenses/create/`

## Tasks

* Bootstrap form styling
* File upload support
* Validation messages
* Multipart form
* Loading state
* Success/error alerts
* File preview

---

# 7. Manager Review Page

## URL

`/workspaces/{id}/expenses/review/`

## Tasks

* Admin-only access
* Filters
* Approve action
* Reject modal
* Review notes validation
* Status update
* Responsive Bootstrap table

---

# Permissions

## Employee Permissions

Can:

* Submit expense
* View own expenses
* Delete submitted expense

Cannot:

* Approve expenses
* Reject expenses
* View all workspace expenses

---

## Admin Permissions

Can:

* View all expenses
* Approve expenses
* Reject expenses
* Delete expenses

---

# Validation Rules

## Expense Validation

* Amount must be greater than 0
* Receipt max size = 10 MB
* Allowed file types:

  * JPG
  * PNG
  * PDF

---

# Pagination

| Page         | Pagination  |
| ------------ | ----------- |
| My Expenses  | 20 per page |
| Admin Review | 25 per page |

---

# UI Requirements

* Bootstrap 5 only
* Django Templates only
* No React
* No TypeScript
* Responsive layout
* Mobile support
* CSRF protection
* Bootstrap alerts and modals

---

# Project Structure

```text
project/
│
├── config/
├── apps/
│   └── expenses/
│       ├── models.py
│       ├── serializers.py
│       ├── services.py
│       ├── views.py
│       ├── urls.py
│       └── forms.py
│
├── templates/
│   └── expenses/
│       ├── list.html
│       ├── create.html
│       └── review.html
│
├── static/
│   ├── css/
│   │   └── expenses.css
│   └── js/
│       └── expenses.js
│
└── media/
    └── receipts/
```

---

# Future Improvements

* Expense analytics dashboard
* Monthly reports
* CSV export
* Email notifications
* Receipt OCR
* Multi-level approval workflow
* Expense limits per category

---

# Done When

* Expense CRUD works
* Receipt uploads work
* Admin approval flow works
* Validation works
* Responsive UI works
* Pagination works
* Permissions enforced
* Receipt cleanup works
* Bootstrap templates complete
