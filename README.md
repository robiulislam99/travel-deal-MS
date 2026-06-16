# Travel Deal Management System (Part 01 + Part 02 + Part 03)

A Flask + SQLite REST API for managing travel deals, with search, filtering, sorting, update/delete operations, popularity tracking, and usage statistics.

## Project Structure
```
travel-deal-MS/
├── app.py                    # App entry point, blueprint registration, error handlers
├── config.py                 # App configuration (DB URI, etc.)
├── routes/
│   ├── deal_routes.py        # Deal-related API endpoints (Blueprint)
│   └── stats_routes.py       # Usage statistics endpoint (Blueprint)
├── services/
│   ├── deal_service.py       # Deal business logic (CRUD, search, filter, sort, views)
│   └── stats_service.py      # Usage statistics business logic
├── utils/
│   ├── validators.py         # Reusable validation functions (create & update share rules)
│   ├── responses.py          # Standard JSON response helpers
│   ├── logger.py             # Centralized logging configuration
│   └── stats_tracker.py      # Reusable decorator that auto-logs every API request
├── database/
│   ├── db.py                 # SQLAlchemy instance & table creation
│   └── models.py             # ORM models (Deal, RecentView, SearchLog, ApiRequestLog)
├── logs/
│   └── app.log               # Generated automatically at runtime
├── requirements.txt          # Project dependencies and package versions
├── postman_collection.json   # Pre-configured Postman collection for API testing
└── README.md                 # Project documentation and setup guide

```

## How to Run

### 1. Clone the project
```bash
git clone https://github.com/robiulislam99/travel-deal-MS.git
cd travel-deal-MS
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate       # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```
The SQLite database file (`travel_deals.db`) and the `deals` table are created automatically on first run. Server runs at `http://localhost:5000`.  A `logs/app.log` file is also created automatically to record API activity.  

## API Endpoints

### 1. Add Travel Deal
`POST http://localhost:5000/deals`

Request body:
```json
{
  "destination": "Dubai",
  "price": 5000,
  "platform": "Booking",
  "rating": 4.5,
  "travel_type": "Luxury"
}
```

### 2. Get All Deals
`GET http://localhost:5000/deals`

Returns all travel deals.

### 3. Get Single Deal  
`GET http://localhost:5000/deals/<id>`

Returns a specific deal based on the provided `<id>`.

### 4. Update Travel Deal
`PUT http://localhost:5000/deals/<id>`

Partial update — only send the fields you want to change. Validation rules for each field are identical to the create endpoint.

Request body (example - update only price):
```json
{ "price": 5500 }
```
### 5. Delete Travel Deal
`DELETE http://localhost:5000/deals/<id>`

Deletes a specific travel deal by its unique ID.

### 6. Search Deals
`GET http://localhost:5000/deals/search`

Query parameters (at least one required, partial & case-insensitive matching):
| Param | Description |
|---|---|
| `destination` | Partial match on destination name |
| `platform` | Partial match on platform name |
| `travel_type` | Exact match, must be one of `Budget`, `Luxury`, `Adventure`, `Family` |

Example:
GET /deals/search?destination=dubai

### 7. Filter Deals by Budget
`GET http://localhost:5000/deals/filter`

Query parameters (at least one required):
| Param | Description |
|---|---|
| `min_price` | Minimum price (inclusive), cannot be negative |
| `max_price` | Maximum price (inclusive), cannot be smaller than `min_price` |

Example:
GET /deals/filter?min_price=1000&max_price=5000

### 8. Sort Deals
`GET http://localhost:5000/deals/sort`

Query parameters:
| Param | Required | Description |
|---|---|---|
| `sort_by` | Yes | One of `price`, `rating`, `destination`, `platform`, `travel_type`, `created_at` |
| `order` | No (default `asc`) | `asc` or `desc` |

Example:
GET /deals/sort?sort_by=price&order=desc

### 9. Recently Viewed Deals
`GET http://localhost:5000/deals/recent`

Returns the 5 most recently viewed deals (via `GET /deals/<id>`), most recent first, with no duplicates. Each deal includes a `last_viewed_at` timestamp.

### 10. Most Viewed (Popular) Deals
`GET http://localhost:5000/deals/popular`

Returns the top 5 deals ranked by total number of views (all-time), each with a `view_count` field.

### 11. API Usage Statistics
`GET http://localhost:5000/stats`

Returns aggregate statistics across all API activity.
```json
{
  "status": "success",
  "message": "Statistics retrieved successfully",
  "data": {
    "total_requests": 23,
    "successful_requests": 14,
    "failed_requests": 9,
    "most_searched_destination": { "destination": "dubai", "search_count": 2 },
    "most_viewed_deal": { "id": 1, "destination": "Dubai", "...": "...", "view_count": 3 }
  }
}
```
`most_searched_destination` and `most_viewed_deal` are `null` if no data has been logged yet.

### API Testing with Postman 
You can import the following file directly into Postman to explore and test your integration environment:

[postman_collection.json](./postman_collection.json)

The collection includes pre-configured parameters matching edge cases for interacting with the APIs.


## Validation Rules
- `destination`: required (on create), non-empty
- `price`: required (on create), must be a positive number
- `rating`: required (on create), must be between 1 and 5
- `travel_type`: required (on create), must be one of `Budget`, `Luxury`, `Adventure`, `Family`
- `platform`: optional, cannot be empty string if provided
- Update (`PUT`) validates only the fields supplied, using the **same rules** as create
- `min_price` / `max_price`: cannot be negative; `max_price` cannot be smaller than `min_price`
- `sort_by`: must be one of `price`, `rating`, `destination`, `platform`, `travel_type`, `created_at`
- `order`: must be `asc` or `desc`

## Error Handling
All transaction responses inherit a uniform JSON envelope architecture:
```json
{ 
  "status": "success" | "error", 
  "message": "User friendly status string", 
  "data": {}, 
  "errors": "Detailed debugging tracer or null" 
}
```
Handles 400, 404, 405, 422, and 500. Delete and update operations handle missing deal IDs safely (return `404`, never raise an unhandled exception).

## Logging
All API activity is logged to console and `logs/app.log` using Python's built-in `logging` module:
- `logging.info()` — successful operations (deal created/updated/deleted, search/filter/sort performed, deal viewed, stats retrieved)
- `logging.warning()` — invalid requests (validation failures, deal not found, invalid id)
- `logging.error()` — failed/unexpected server errors

## Architecture & Reusability
- **Routes** (`routes/`) only handle request parsing and response formatting — no business logic.
- **Services** (`services/`) contain all business logic and database queries, split by domain: `deal_service.py` for deals, `stats_service.py` for statistics.
- **Validators** (`utils/validators.py`) define field-level validation functions once (`FIELD_VALIDATORS`) and reuse them for both create and update, so the two never drift out of sync.
- **Search, filter, and sort** all share a single reusable query builder (`build_deal_query`) in `deal_service.py`, avoiding duplicate filtering logic.
- **API usage tracking** is implemented as a reusable decorator (`@track_api_usage` in `utils/stats_tracker.py`) applied to every route, so statistics logging never needs to be duplicated inside route bodies.