# Banas water API's

This project is dedicated to create a django rest framework API's for Mineral water billing and customer management application.

## Install
Go to the project folder and run this command.

    pip3 install -r requirements.txt

## Run the app

    python3 manage.py runserver

# REST API

The REST API which we have created and the usecase for this.

## Add Routes

### Request

`POST api/route/`

    Request : http://localhost:8000/api/route/
    
    {
        "route_name" : "ABC"
    }

### Response

    {
        "id": "be5b4f74-62c6-4bc0-92e4-d746421d0f12",
        "route_name": "Kishan",
        "date_added": "2023-02-06T13:50:14.527315Z",
        "date_updated": "2023-02-06T13:50:14.527351Z",
        "addedby": null,
        "updatedby": null
    }

## List All the Routes

### Request

`GET /api/route/`

    Request : http://localhost:8000/api/route/
    
### Response
    
    [
        {
            "id": "be5b4f74-62c6-4bc0-92e4-d746421d0f12",
            "route_name": "Kishan",
            "date_added": "2023-02-06T13:50:14.527315Z",
            "date_updated": "2023-02-06T13:50:14.527351Z",
            "addedby": null,
            "updatedby": null
        },
        {...}
    ]

## Update Route

### Request

`PUT /api/route/{$id}/`

    Request : http://localhost:8000/api/route/{$id}
    
    {
        "id": "be5b4f74-62c6-4bc0-92e4-d746421d0f12",
        "route_name": "Jeep"
    }
    
{$id} -> Is route Id for the Route 
    
### Response

    {
        "id": "be5b4f74-62c6-4bc0-92e4-d746421d0f12",
        "route_name": "Jeep",
        "date_added": "2023-02-06T13:50:14.527315Z",
        "date_updated": "2023-02-08T13:49:08.148565Z",
        "addedby": admin,
        "updatedby": "admin"
    }

## Add Customer

### Request

`POST /api/customer/`

    Request : http://localhost:8000/api/customer/

    {
        "name" : "Fine Tech",
        "route" : "86509742-40b2-4a26-b137-f8550eaec3d1",
        "rate" : 25
    }

### Response

    {
        "id": "9ca5b862-3e43-4e1e-a514-617ddf7242ca",
        "route": "86509742-40b2-4a26-b137-f8550eaec3d1",
        "name": "Fine Tech",
        "rate": 25,
        "date_added": "2023-02-08T14:21:10.642492Z",
        "date_updated": "2023-02-08T14:21:10.642515Z",
        "addedby": "admin",
        "updatedby": null,
        "active": true
    }

## Get All the Customer

### Request

`GET /api/customer/`

    Request : http://localhost:8000/api/customer/

### Response

    [
        {
            "id": "257b4678-92c0-4b44-8ead-5d818ce570d3",
            "name": "Elon Musk",
            "rate": 50,
            "date_added": "2022-12-10T11:37:36.815049Z",
            "date_updated": "2022-12-10T11:37:36.815064Z",
            "addedby": "admin",
            "updatedby": null,
            "active": true,
            "route": {
                "id": "c08f63e5-a9a1-4a28-b794-ce85fabd5f01",
                "route_name": "Andheri",
                "date_added": "2022-12-09T19:33:54.487577Z",
                "date_updated": "2022-12-09T19:33:54.487592Z",
                "addedby": "admin",
                "updatedby": null
            }
        },
        {...}.
        {...}
    ]

## Get Customer Info

### Request 

`GET /api/customer/{$id}/`

    Request : http://localhost:8000/api/customer/{$id}/

{$id} -> Customer ID

### Response

    {
        "id": "257b4678-92c0-4b44-8ead-5d818ce570d3",
        "route": "c08f63e5-a9a1-4a28-b794-ce85fabd5f01",
        "name": "Elon Musk",
        "rate": 50,
        "date_added": "2022-12-10T11:37:36.815049Z",
        "date_updated": "2022-12-10T11:37:36.815064Z",
        "addedby": "admin",
        "updatedby": "admin",
        "active": true
    }

## Update Customer

### Request

`PUT /api/customer/{$id}/`

    Request : http://localhost:8000/api/customer/{$id}/

    {
        "id": "257b4678-92c0-4b44-8ead-5d818ce570d3",
        "route": "c08f63e5-a9a1-4a28-b794-ce85fabd5f01",
        "name": "Elon Musk",
        "rate": 25
    }

### Response

    {
        "id": "257b4678-92c0-4b44-8ead-5d818ce570d3",
        "route": "c08f63e5-a9a1-4a28-b794-ce85fabd5f01",
        "name": "Elon Musk",
        "rate": 25,
        "date_added": "2022-12-10T11:37:36.815049Z",
        "date_updated": "2022-12-10T11:37:36.815064Z",
        "addedby": "admin",
        "updatedby": "admin",
        "active": true
    }

## Get one Customer detail

### Request

`GET /api/customer/detail/{$id}/`

    Request : http://localhost:8000/api/customer/detail/{$id}/

### Response

    {
        "customer_detail": {
            "id": "4d1c3916-70a8-4ae0-a87e-f71a29eca05d",
            "name": "Sunil Sharma",
            "rate": 20,
            "date_added": "2022-12-10T11:41:14.585339Z",
            "date_updated": "2022-12-10T11:41:14.585355Z",
            "addedby": "admin",
            "updatedby": "admin",
            "active": true,
            "route": {
                "id": "23bc6409-0a78-4f34-8192-62afa07269f2",
                "route_name": "Vasai",
                "date_added": "2022-12-09T19:37:46.908924Z",
                "date_updated": "2022-12-09T19:37:46.908939Z",
                "addedby": "admin",
                "updatedby": null
            }
        },
        "bills": [
            {
                "from_date": "2023-01-01",
                "to_date": "2023-02-28",
                "coolers": 30,
                "Total": 1800,
                "paid": true,
                "id": "ee46b4ed-a937-495e-99f5-a88d5287c46d"
            }
        ],
        "daily_entry": [
            {
                "cooler": 10,
                "date_added": "2023-02-05T12:26:58.905499Z"
            },
            {
                "cooler": 10,
                "date_added": "2023-02-05T12:32:36.087653Z"
            },
            {
                "cooler": 10,
                "date_added": "2023-02-05T13:38:34.443555Z"
            }
        ],
        "total_coolers": 30,
        "payments": [
            {
                "pending_amount": null,
                "paid_amount": 500,
                "date": "2023-02-05T13:51:32.874625Z",
                "addedby": "admin"
            },
            {
                "pending_amount": 1800,
                "paid_amount": 800,
                "date": "2023-02-05T14:02:53.983923Z",
                "addedby": "admin"
            }
        ],
        "total_payments": 1300,
        "due_payments": {
            "id": "0e661855-bc07-4962-88cd-f4fd285cbd8a",
            "due": 1000,
            "date": "2022-12-10T11:41:14.586242Z",
            "addedby": null,
            "updatedby": "admin",
            "customer_name": "4d1c3916-70a8-4ae0-a87e-f71a29eca05d"
        }
    }

## Get Customer Due

### Request 

`GET /api/customer/due/{$id}/`

    Request : http://localhost:8000/api/customer/due/{$id}/

{$id} -> Customer ID 

### Response

    {
        "customer_name": "Elon Musk",
        "due": 2000
    }

## List Customer by Route

### Request

`GET /api/customer/route/{$id}/`

    Request : http://localhost:8000/api/customer/route/{$id}/

{$id} -> Route ID

### Response

    [
        {
            "id": "257b4678-92c0-4b44-8ead-5d818ce570d3",
            "name": "Elon Musk",
            "rate": 25,
            "date_added": "2022-12-10T11:37:36.815049Z",
            "date_updated": "2022-12-10T11:37:36.815064Z",
            "addedby": "admin",
            "updatedby": "admin",
            "active": true,
            "route": {
                "id": "c08f63e5-a9a1-4a28-b794-ce85fabd5f01",
                "route_name": "Andheri",
                "date_added": "2022-12-09T19:33:54.487577Z",
                "date_updated": "2022-12-09T19:33:54.487592Z",
                "addedby": "admin",
                "updatedby": null
            }
        }
    ]

It will get all the customer which are in given in route.

## Add Daily Entry

### Request

`POST /api/daily-entry/`

    Request : http://localhost:8000/api/daily-entry/

    {
        "customer_name" : "9ca5b862-3e43-4e1e-a514-617ddf7242ca",
        "cooler" : 5
    }

customer_name will be the customer ID

### Response

    {
        "id": "08a9b000-1036-4d96-95f5-b8768a86d5b1",
        "cooler": 5,
        "date_added": "2023-02-09T14:18:17.313828Z",
        "addedby": "admin",
        "updatedby": null,
        "customer": "9ca5b862-3e43-4e1e-a514-617ddf7242ca"
    }

If today is the last day of the month then it will automatically generate the bill for that customer for this month and save it. With all the details and also update the customerAccount according to the bill.

## Update Daily Entry

### Request

`PUT /api/daily-entry/{$id}/`

    Request : http://localhost:8080/api/daily-entry/{$id}/

    {
        "id": "ffbcf7b1-3ffe-4580-95eb-b1cbff0cea9e",
        "cooler": 10
    }

In URL id willl be the daily entry Id and in data ID will be the daily entry ID.

### Response

    {
        "id": "ffbcf7b1-3ffe-4580-95eb-b1cbff0cea9e",
        "cooler": 10,
        "date_added": "2023-02-05T13:38:34.443555Z",
        "addedby": "admin",
        "updatedby": "admin",
        "customer": "4d1c3916-70a8-4ae0-a87e-f71a29eca05d"
    }

For the same like adding daily entry, If today is last date and we are updating the daily entry then it will automatically update the bill which is generated and the customerAccount also.

## Deleting Daily Entry

### Request

`DEL /api/daily-entry/{$id}/`

    Request : http://localhost:8080/api/daily-entry/{$id}/

{$id} will be the daily entry ID.

### Response

    {
        "message" : "Daily Entry Deleted ! "
    }

For the same like adding daily entry, If today is the last date and we are deleting this daily entry then it will automatically update the bill which is generated and update the customerAccount.