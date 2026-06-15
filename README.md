# Travel Deal Management System (Part 01 + Part 02)

A Flask + SQLite REST API for managing travel deals, with search, filtering, sorting, recently viewed tracking, and logging.

## Project Structure
```
travel-deal-MS/
├── app.py              # App entry point, blueprint registration, error handlers
├── config.py           # App configuration (DB URI, etc.)
├── routes/
│   └── deal_routes.py  # API endpoints (Blueprint)
├── services/
│   └── deal_service.py # Business logic only
├── utils/
│   ├── validators.py   # Reusable validation functions
│   ├── responses.py    # Standard JSON response helpers
│   └── logger.py        # Centralized logging configuration
├── database/
│   ├── db.py            # SQLAlchemy instance & table creation
│   └── models.py        # ORM models (Deal, RecentView)
├── logs/
│   └── app.log          # Generated automatically at runtime
├── requirements.txt
├── postman_collection.json
└── README.md

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

- `200` on success
- `404` if not found
- `400` if `<id>` is not a positive integer

### 4. Search Deals
`GET http://localhost:5000/deals/search`

Query parameters (at least one required, partial & case-insensitive matching):
| Param | Description |
|---|---|
| `destination` | Partial match on destination name |
| `platform` | Partial match on platform name |
| `travel_type` | Exact match, must be one of `Budget`, `Luxury`, `Adventure`, `Family` |

Example:
GET /deals/search?destination=dubai

Responses:
- `200` with matching deals
- `200` with empty `data: []` and message `"No deals found matching the search criteria"` if no matches
- `400` if no query parameters are provided, or `travel_type` is invalid

### 5. Filter Deals by Budget
`GET http://localhost:5000/deals/filter`

Query parameters (at least one required):
| Param | Description |
|---|---|
| `min_price` | Minimum price (inclusive), cannot be negative |
| `max_price` | Maximum price (inclusive), cannot be smaller than `min_price` |

Example:
GET /deals/filter?min_price=1000&max_price=5000

Responses:
- `200` with matching deals
- `200` with empty `data: []` if no deals fall in range
- `400` if `min_price`/`max_price` is negative, `max_price` < `min_price`, or neither param is provided

### 6. Sort Deals
`GET http://localhost:5000/deals/sort`

Query parameters:
| Param | Required | Description |
|---|---|---|
| `sort_by` | Yes | One of `price`, `rating`, `destination`, `platform`, `travel_type`, `created_at` |
| `order` | No (default `asc`) | `asc` or `desc` |

Example:
GET /deals/sort?sort_by=price&order=desc

Responses:
- `200` with all deals sorted accordingly
- `400` if `sort_by` is missing/invalid, or `order` is invalid

### 7. Recently Viewed Deals
`GET http://localhost:5000/deals/recent`

Returns the 5 most recently viewed deals (via `GET /deals/<id>`), most recent first, with no duplicates. Each deal includes a `last_viewed_at` timestamp.

Responses:
- `200` with the list of recently viewed deals
- `200` with empty `data: []` and message `"No deals have been viewed yet"` if none viewed yet

### API Testing with Postman 
You can import the following files into Postman to explore and test all available API endpoints:

postman_collection_part1.json
postman_collection_part2.json

These collections include all possible requests for interacting with the API.


## Validation Rules
- `destination`: required, non-empty
- `price`: required, must be a positive number
- `rating`: required, must be between 1 and 5
- `travel_type`: required, must be one of `Budget`, `Luxury`, `Adventure`, `Family`
- `platform`: optional, cannot be empty string if provided
- `min_price` / `max_price`: cannot be negative; `max_price` cannot be smaller than `min_price`
- `sort_by`: must be one of `price`, `rating`, `destination`, `platform`, `travel_type`, `created_at`
- `order`: must be `asc` or `desc`

## Error Handling
All responses follow a consistent shape:
```json
{ "status": "success" | "error", "message": "...", "data": ..., "errors": ... }
```
Handles 400, 404, 405, 422, and 500.

## Logging
All API activity is logged to console and `logs/app.log` using Python's built-in `logging` module:
- `logging.info()` — successful operations (deal created, search/filter/sort performed, deal viewed)
- `logging.warning()` — invalid requests (validation failures, deal not found, invalid id)
- `logging.error()` — failed/unexpected server errors

## Code Reusability
Search, filter, and sort all share a single reusable query builder (`build_deal_query`) in `services/deal_service.py`, avoiding duplicate filtering logic across endpoints.