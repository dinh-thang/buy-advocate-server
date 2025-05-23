# Buy Advocate Server API Documentation

This document provides detailed information about the available API endpoints, their request/response formats, and usage examples.

## Authentication
All endpoints require authentication via Bearer token. Include the following header in your requests:
```
Authorization: Bearer <jwt_token>
```

## Table of Contents
- [Properties API](#properties-api)
- [Projects API](#projects-api)
- [Filters API](#filters-api)
- [Admin API](#admin-api)

## Properties API

### Get Properties
`POST /api/properties`

Retrieves a paginated list of properties with optional filtering.

**Request Body:**
```json
{
    "filters": [
        {
            "filter_type": "range",
            "filter_data": {
                "min": 100000,
                "max": 500000
            },
            "db_column_name": "asking_price"
        }
    ],
    "page": 1,
    "page_size": 100
}
```

**Response:**
```json
[
    {
        "id": "uuid",
        "asking_price": 250000,
        "address": "123 Main St",
        "property_images": ["url1", "url2"],
        "description": "Property description",
        "agent_name": "John Doe",
        "agent_phone_number": "+1234567890",
        "latitude": -37.8136,
        "longitude": 144.9631,
        "yield_percentage": 5.5,
        "lease_terms": "5 years"
    }
]
```

## Projects API

### Get Project
`GET /api/projects/{project_id}`

Retrieves a specific project by ID.

**Response:**
```json
{
    "id": "uuid",
    "created_at": "2024-03-20T10:00:00Z",
    "title": "Project Title",
    "user_id": "uuid",
    "site_type_id": "uuid",
    "market_status_id": "uuid",
    "market_status": {
        "id": "uuid",
        "name": "Market Status Name"
    },
    "site_types": {
        "id": "uuid",
        "name": "Site Type Name"
    },
    "user_filters": [
        {
            "id": "uuid",
            "filter_type": "range",
            "filter_data": {},
            "db_column_name": "column_name",
            "project_id": "uuid"
        }
    ]
}
```

### Get All Projects
`GET /api/projects`

Retrieves all projects for the authenticated user.

**Response:**
```json
[
    {
        "id": "uuid",
        "title": "Project Title"
    }
]
```

### Create Project
`POST /api/projects`

Creates a new project.

**Request Body:**
```json
{
    "title": "New Project",
    "site_type_id": "uuid",
    "user_id": "uuid",
    "market_status_id": "uuid"
}
```

**Response:**
```json
{
    "id": "uuid",
    "created_at": "2024-03-20T10:00:00Z",
    "title": "New Project",
    "user_id": "uuid",
    "site_type_id": "uuid",
    "market_status_id": "uuid",
    "market_status": {
        "id": "uuid",
        "name": "Market Status Name"
    },
    "site_types": {
        "id": "uuid",
        "name": "Site Type Name"
    },
    "user_filters": []
}
```

### Update Project
`PATCH /api/projects/{project_id}`

Updates an existing project.

**Request Body:**
```json
{
    "title": "Updated Project Title",
    "site_type_id": "uuid",
    "market_status_id": "uuid"
}
```

**Response:**
```json
{
    "id": "uuid",
    "title": "Updated Project Title",
    "site_type_id": "uuid",
    "market_status_id": "uuid"
}
```

### Delete Project
`DELETE /api/projects/{project_id}`

Deletes a project.

**Response:**
```json
{
    "message": "Project deleted successfully"
}
```

## Filters API

### Update Filter
`PATCH /api/filters/{filter_id}`

Updates a single filter.

**Request Body:**
```json
{
    "filter_type": "range",
    "filter_data": {
        "min": 100000,
        "max": 500000
    },
    "db_column_name": "asking_price"
}
```

**Response:**
```json
{
    "id": "uuid",
    "filter_type": "range",
    "filter_data": {
        "min": 100000,
        "max": 500000
    },
    "db_column_name": "asking_price",
    "project_id": "uuid"
}
```

### Batch Update Filters
`PATCH /api/filters/batch`

Updates multiple filters in a single request.

**Request Body:**
```json
[
    {
        "id": "uuid-1",
        "filter_data": {
            "min": 100000,
            "max": 500000
        }
    },
    {
        "id": "uuid-2",
        "filter_data": {
            "min": 50,
            "max": 100
        }
    }
]
```

**Response:**
```json
[
    {
        "id": "uuid-1",
        "filter_type": "range",
        "filter_data": {
            "min": 100000,
            "max": 500000
        },
        "db_column_name": "asking_price",
        "project_id": "uuid"
    },
    {
        "id": "uuid-2",
        "filter_type": "range",
        "filter_data": {
            "min": 50,
            "max": 100
        },
        "db_column_name": "yield_percentage",
        "project_id": "uuid"
    }
]
```

## Admin API

### Create Filter
`POST /api/admin/filters`

Creates a new filter with market status and site type association.

**Request Body:**
```json
{
    "filter_type": "range",
    "filter_data": {
        "min": 100000,
        "max": 500000
    },
    "db_column_name": "asking_price"
}
```

**Query Parameters:**
- `market_status_id`: UUID of the market status
- `site_type_id`: UUID of the site type

**Response:**
```json
{
    "id": "uuid",
    "filter_type": "range",
    "filter_data": {
        "min": 100000,
        "max": 500000
    },
    "db_column_name": "asking_price"
}
```

### Create Site Type
`POST /api/admin/site_types`

Creates a new site type.

**Request Body:**
```json
{
    "name": "New Site Type"
}
```

**Response:**
```json
{
    "id": "uuid",
    "name": "New Site Type"
}
```

### Create Market Status
`POST /api/admin/market_status`

Creates a new market status.

**Request Body:**
```json
{
    "name": "New Market Status"
}
```

**Response:**
```json
{
    "id": "uuid",
    "name": "New Market Status"
}
``` 