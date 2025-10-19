# Document Management System (DMS) for Multi-Business, Multi-Site Engineering Company

**Storage Backbone:** Google Drive (via Drive API v3)

**Framework Target:** Web App (Python FastAPI or Node.js backend + React / Streamlit frontend)

**Authentication:** Firebase Auth (Google OAuth2.0)

## 1. Objective

Design and implement a centralized DMS to manage all engineering, project, and corporate documents across multiple Business Units (BUs), Sites, Disciplines, and Functional Departments.

The system must:

- Store and retrieve documents from Google Drive Shared Drives.
- Maintain metadata and version control in a structured database.
- Support role-based access and approval workflows.
- Enable fast search, tracking, and auditing.

## 2. System Entities

### 2.1 Business Units (BU)

| Code | Name |
| --- | --- |
| IWM | Industrial Waste Management |
| MSW | Municipal Solid Waste |
| BMW | Bio-Medical Waste |
| IES | Integrated Environmental Solutions |
| ISS | Integrated Sustainable Solutions |
| REC | Recycling |

Each BU → Multiple Sites → Each Site → Multiple Disciplines reporting to Functional Heads (centrally located).

### 2.2 Functional Units (Central)

- Projects and Engineering
- Procurement / SCM
- Finance
- HR / Admin
- Business Development
- QA/QC / HSE
- Legal / Compliance
- Design / Planning

### 2.3 Site Disciplines (Examples)

- Civil
- Mechanical
- Electrical
- Instrumentation
- QA/QC
- HSE

## 3. System Architecture (Logical Overview)

### Frontend

React or Streamlit Web App → Authentication via Firebase → Interacts with REST API.

### Backend

Python (FastAPI) or Node.js → Handles metadata, Drive API calls, workflow logic.

### Database

PostgreSQL or Firestore → Stores document metadata, users, access rights, and logs.

### Storage

Google Drive Shared Drives → Each BU/Site mapped to Drive Folder ID.

### Integration Points

- Google Drive API – File/folder operations
- Gmail API – Notifications
- Sheets API – Reports
- Firebase Auth – Identity management

## 4. Database Schema (Core Tables)

### 4.1 `business_units`

| id | code | name | description |
| --- | --- | --- | --- |

### 4.2 `sites`

| id | name | bu_id | location | drive_folder_id |
| --- | --- | --- | --- | --- |

### 4.3 `disciplines`

| id | name | site_id | drive_folder_id |
| --- | --- | --- | --- |

### 4.4 `documents`

| id | doc_code | bu_id | site_id | discipline_id | category | filename | drive_file_id | version | status | uploader_id | reviewer_id | approver_id | upload_date | approved_date | comments |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### 4.5 `users`

| id | name | email | role | function | bu_id | site_id | discipline_id |
| --- | --- | --- | --- | --- | --- | --- | --- |

### 4.6 `roles`

| id | name | permissions_json |
| --- | --- | --- |

### 4.7 `audit_logs`

| id | document_id | action | user_id | timestamp | details_json |
| --- | --- | --- | --- | --- | --- |

## 5. Core Modules and API Requirements

### 5.1 Authentication and Authorization

- Login via Google OAuth (Firebase Auth).
- JWT tokens for API requests.
- Role-based access:
  - Admin
  - BU Head
  - Functional Head
  - Site Manager
  - Discipline Engineer
  - Viewer

**API Example:** `POST /api/login` → Returns user profile and access scope.

### 5.2 Folder Structure Automation

When a new site is added, the API auto-creates Google Drive folders based on template: `/BU/Site/Discipline/Category`.

- Folder IDs stored in DB for direct mapping.
- Access permissions auto-granted based on user role.

**API Example:**

```
POST /api/folders/create
{
  "bu": "IWM",
  "site": "Surat",
  "disciplines": ["Civil", "Mechanical"]
}
```

### 5.3 Document Upload

- Drag-and-drop upload to correct Drive folder using Drive API.
- Metadata stored in `documents` table.
- Auto-generate unique document code pattern: `[BU]-[SITE]-[DISC]-[TYPE]-[NNN]`.

**API Example:**

```
POST /api/documents/upload
{
  "file": <binary>,
  "bu": "IWM",
  "site": "Surat",
  "discipline": "Civil",
  "category": "Drawing",
  "uploader_id": "U123"
}
```

**Output:** `{ "status": "success", "doc_id": "IWM-SUR-CIV-DRG-001" }`

### 5.4 Metadata and Version Control

- Each upload revision creates a new version entry.
- Google Drive revision ID mapped to internal version.
- Version comments required.

**API Example:**

```
POST /api/documents/update_version
{
  "doc_id": "IWM-SUR-CIV-DRG-001",
  "new_file_id": "<DriveID>",
  "comment": "Updated GA drawing"
}
```

### 5.5 Workflow and Approvals

Configurable workflow:

- Level 1: Site → BU Reviewer
- Level 2: BU Reviewer → Functional Head

Each step logs approval and sends notification.

**API Example:**

```
POST /api/workflows/approve
{
  "doc_id": "IWM-SUR-CIV-DRG-001",
  "approver_id": "U567",
  "action": "approve",
  "remarks": "OK to issue"
}
```

### 5.6 Search and Retrieval

- Keyword, metadata, or filter-based search.
- Indexed columns: `doc_code`, `category`, `bu_id`, `site_id`, `discipline_id`.
- Optional full-text search using content embeddings (Phase 2).

**API Example:** `GET /api/search?query=Surat Civil Drawing`

### 5.7 Notifications

Trigger Gmail API notifications on upload, approval, rejection, or overdue items.

- Daily digest of pending tasks.

**API Example:**

```
POST /api/notifications/send
{
  "to": ["qa.qc@company.com"],
  "subject": "Pending Approvals",
  "message": "3 documents awaiting review."
}
```

### 5.8 Dashboards

**Company Dashboard**

KPIs:

- Documents uploaded (by BU, site, discipline)
- Status summary (draft/review/approved)
- Overdue approvals

**API Endpoint:** `GET /api/dashboard/company`

**Functional Dashboard**

- All documents related to function (e.g., Finance → all invoices)
- Drill-down by BU → Site → Status

**API Endpoint:** `GET /api/dashboard/function/{function_name}`

### 5.9 Audit and Reporting

- Every upload, approval, or access logged.
- Reports exportable as CSV or PDF.

**API Endpoint:** `GET /api/reports/audit?start=2025-10-01&end=2025-10-19`

## 6. Access Matrix (Role Permissions)

| Role | Upload | Review | Approve | Delete | View All | Audit Access |
| --- | --- | --- | --- | --- | --- | --- |
| Admin | Yes | Yes | Yes | Yes | Yes | Yes |
| BU Head | Yes | Yes | Yes | No | Yes | Yes |
| Functional Head | Yes | Yes | Yes | No | Yes | Yes |
| Site Manager | Yes | Yes | No | No | Yes | No |
| Discipline Engineer | Yes | No | No | No | Yes | No |
| Viewer | No | No | No | No | Yes | No |

## 7. Frontend Specification

### 7.1 Modules / Pages

- Login Page: Google Sign-in.
- Dashboard: KPIs, recent activity, filters by BU/Site.
- Document Upload: File chooser + metadata form.
- Document Viewer: File preview from Drive (iframe).
- Search Page: Filterable search table.
- Approvals: Pending list + action buttons.
- Audit Reports: Date-based export.
- Admin Settings: Role mapping, folder ID registry.

### 7.2 UI Guidelines

- Responsive design (desktop and tablet).
- Dark and light themes.
- Pagination and sorting in tables.
- Upload progress indicators.

## 8. Implementation Plan

| Phase | Duration | Deliverables |
| --- | --- | --- |
| Phase 1 | 0–3 months | Auth system, folder mapping, upload module |
| Phase 2 | 3–6 months | Workflow approvals, dashboards, audit logs |
| Phase 3 | 6–9 months | Full-text search, analytics, reporting |
| Phase 4 | 9–12 months | Mobile view, AI-assisted content indexing |

## 9. Success Metrics

| Metric | Target |
| --- | --- |
| Retrieval time | < 2 seconds |
| Document loss | 0% |
| Approval compliance | > 90% |
| Version accuracy | > 95% |
| User adoption (active users) | > 80% of total staff |

## 10. Sample Drive Structure

```
/Company_DMS/
 ├── IWM/
 │    ├── Surat/
 │    │     ├── Civil/
 │    │     │    ├── Drawings/
 │    │     │    ├── Reports/
 │    │     │    └── QAQC/
 │    │     ├── Mechanical/
 │    │     └── HSE/
 │    └── NaviMumbai/
 ├── MSW/
 ├── BMW/
 └── Central_Functions/
      ├── Finance/
      ├── HR/
      ├── SCM/
      ├── Projects/
      ├── QAQC/
      └── Legal/
```

This version is developer-ready — every section (database schema, API endpoints, workflow logic, folder mapping, access matrix) is structured so that an AI agent or developer can directly generate database models, scaffold API routes, map Drive folder creation logic, and build the frontend dashboards.
