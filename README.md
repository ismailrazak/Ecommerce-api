# E-commerce API Platform

A full-featured e-commerce API with Razorpay payments, ElasticSearch for fuzzy search and autocomplete, Redis caching, Celery workers for background tasks, cart system, Google OAuth with JWT authentication, and AI-powered review summaries using Gemini 2.0 Flash.

## Features

- **User Management**
  - Customer and Seller registration
  - Google OAuth integration with JWT authentication
  - User profile management
  
- **Product Management**
  - Product listings with images
  - Product reviews with AI summaries
  - Hot deals with automatic refreshing via Celery

- **Search Capabilities**
  - ElasticSearch integration for fast and accurate searches
  - Fuzzy search to handle spelling mistakes
  - Autocomplete suggestions
  
- **Cart System**
  - Add/remove items
  - Persistent cart across sessions
  - One-click checkout

- **Payment Processing**
  - Secure Razorpay integration
  - Payment status handling and webhooks

- **AI-Powered Features**
  - Review summaries powered by Gemini 2.0 Flash
  - Sentiment analysis on customer reviews

## Fuzzysearch example

### Request
```http
GET http://127.0.0.1:8000/product_search/?search=electroncs
```

### Response
```json
{
    "count": 502,
    "next": "http://127.0.0.1:8000/product_search/?page=2&search=electroncs",
    "previous": null,
    "facets": {},
    "results": [
        {
            "name": "Prestigio MultiPhone 5000 Duo",
            "description": "description",
            "category": "Electronics Devices",
            "price": 18975.75
        },
        {
            "name": "Yezz Monte Carlo 55 LTE VR",
            "description": "description",
            "category": "Electronics Devices",
            "price": 70724.65
        },
        {
            "name": "Samsung Galaxy M21s",
            "description": "description",
            "category": "Electronics Devices",
            "price": 19838.95
        },
        {
            "name": "BlackBerry Keyone",
            "description": "description",
            "category": "Electronics Devices",
            "price": 5702.31
        }
    ]
```      

## Auto Complete example

### Request
```http
GET http://127.0.0.1:8000/product_search/suggest/?name_suggest__completion=p
```

### Response
```json
{
    "name_suggest__completion": [
        {
            "text": "p",
            "offset": 0,
            "length": 1,
            "options": [
                {
                    "text": "Pail For Lid 1537",
                    "_index": "products",
                    "_id": "c6bbd3cc-1f1e-4c79-a1a3-cc4c7dd9d225",
                    "_score": 1.0,
                    "_source": {
                        "name": "Pail For Lid 1537",
                        "category": "Grocery Items",
                        "id": "c6bbd3cc-1f1e-4c79-a1a3-cc4c7dd9d225",
                        "description": "description",
                        "price": 64399.96
                    }
                },
                {
                    "text": "Palm Palm",
                    "_index": "products",
                    "_id": "8371e1f2-fdfe-4685-9ab6-8231934b9dc0",
                    "_score": 1.0,
                    "_source": {
                        "category": "Electronics Devices",
                        "name": "Palm Palm",
                        "id": "8371e1f2-fdfe-4685-9ab6-8231934b9dc0",
                        "description": "description",
                        "price": 27874.06
                    }
                },
                {
                    "text": "Palm Pre",
                    "_index": "products",
                    "_id": "2fbfb24f-f19a-4b75-b105-93d7f477b4db",
                    "_score": 1.0,
                    "_source": {
                        "category": "Electronics Devices",
                        "name": "Palm Pre",
                        "id": "2fbfb24f-f19a-4b75-b105-93d7f477b4db",
                        "description": "description",
                        "price": 62717.44
                    }
                },
                {
                    "text": "Palm Treo 270",
                    "_index": "products",
                    "_id": "ef3fcdf1-afa5-4b11-b5f2-a8486c513098",
                    "_score": 1.0,
                    "_source": {
                        "category": "Electronics Devices",
                        "name": "Palm Treo 270",
                        "id": "ef3fcdf1-afa5-4b11-b5f2-a8486c513098",
                        "description": "description",
                        "price": 40167.06
                    }
                },
                {
                    "text": "Panasonic Eluga I7",
                    "_index": "products",
                    "_id": "214d1833-db3c-4734-81c4-d9b74cf8c4ee",
                    "_score": 1.0,
                    "_source": {
                        "category": "Electronics Devices",
                        "name": "Panasonic Eluga I7",
                        "id": "214d1833-db3c-4734-81c4-d9b74cf8c4ee",
                        "description": "description",
                        "price": 11902.39
                    }
                }
            ]
        }
    ]
}
```
## API Endpoints

### Authentication Endpoints

```
/auth/register/customer - Customer Registration
/auth/register/seller - Seller Registration
/auth/account_detail/<str:username> - Account Details
/auth/session_login/ - Session Login
/auth/google/login/ - Google Login Page
/auth/google/ - Google Login API
/auth/google/callback/ - Google Login Callback
/auth/account-confirm-email/<key>/ - Email Confirmation
```

### Cart Endpoints

```
/cart/ - View Cart
/cart/remove_all_items/ - Remove All Items From Cart
/cart/buy_all_items/ - Buy All Items In Cart
/cart/cart_payment_handler/ - Cart Payment Handler
```

### Product Endpoints

```
/products/product_image/<int:pk> - Product Image
/products/product_review_create/<str:pk> - Create Product Review
/products/product_review/<str:pk> - View Product Review
/products/hot_deals/<str:category> - Get Hot Deals By Category
/products/payment_handler/ - Product Payment Handler
/products/review_summary/<str:pk> - AI-Generated Review Summary
```

### Search Endpoints

```
/product_search/?search=<query> - Fuzzy Search Products
/product_search/suggest/?name_suggest__completion=<prefix> - Autocomplete Suggestions
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Razorpay API keys
- Google OAuth credentials
- ElasticSearch knowledge
- Gemini API access

### Installation with Docker

1. Clone the repository
   ```
   git clone https://github.com/ismailrazak/Ecommerce-api.git
   cd ecommerce-api
   ```

2. Create an `.env` file with the following variables:
   

3. Start the Docker containers
   ```
   docker-compose up -d
   ```

4. Run migrations
   ```
   docker-compose exec web python manage.py migrate
   ```

5. Create superuser
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

6. Build ElasticSearch indices
   ```
   docker-compose exec web python manage.py rebuild_index
   ```

7. The API is now available at http://localhost:8000/
