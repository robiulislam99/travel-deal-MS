# Travel Deal Management System (Part 01)

A Flask + SQLite REST API for managing travel deals.


## Project Structure
```
travel-deal-MS/
├── app.py              # App entry point, blueprint registration, error handlers
├── routes/
│   └── deal_routes.py  # API endpoints (Blueprint)
├── services/
│   └── deal_service.py # Business logic & DB queries
├── utils/
│   ├── validators.py   # Reusable validation functions
│   └── responses.py    # Standard JSON response helpers
├── database/
│   └── db.py           # SQLite connection & table creation
├── requirements.txt
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
The SQLite database file (`travel_deals.db`) and the `deals` table are created automatically on first run. Server runs at `http://localhost:5000`.

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

Success (201):
```json
{
  "status": "success",
  "message": "Deal created successfully",
  "data": { "id": 1, "destination": "Dubai", "price": 5000, "platform": "Booking", "rating": 4.5, "travel_type": "Luxury", "created_at": "..." }
}
```

Validation error (422):
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": { "price": "price must be positive" }
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

## Validation Rules
- `destination`: required, non-empty
- `price`: required, must be a positive number
- `rating`: required, must be between 1 and 5
- `travel_type`: required, must be one of `Budget`, `Luxury`, `Adventure`, `Family`
- `platform`: optional, cannot be empty string if provided

## Error Handling
All responses follow a consistent shape:
```json
{ "status": "success" | "error", "message": "...", "data": ..., "errors": ... }
```
Handles 400, 404, 405, 422, and 500.

## Postman Collection
Import this JSON into Postman:
```
{
  "info": {
    "name": "Travel Deal API",
    "_postman_id": "8c1d2f11-2f3a-4b2c-9c11-abcdef123456",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Add Travel Deal",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"destination\": \"Dubai\",\n  \"price\": 5000,\n  \"platform\": \"Booking\",\n  \"rating\": 4.5,\n  \"travel_type\": \"Luxury\"\n}"
        },
        "url": "http://localhost:5000/deals"
      }
    },
    {
      "name": "Get All Deals",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/deals"
      }
    },
    {
      "name": "Get Single Deal",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/deals/1"
      }
    }
  ]
}
```