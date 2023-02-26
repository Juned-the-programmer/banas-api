# Banas water API's

This project is dedicated to create a django rest framework API's for Mineral water billing and customer management application.

## Install
Go to the project folder and run this command.

    pip3 install -r requirements.txt

## Run the app

    python3 manage.py runserver

# REST API

The REST API which we have created and the usecase for this.

## Login

### Request

`POST /api/login/`

    Request : http://localhost:8000/api/login/

    {
        "username" : "admin",
        "password" : "admin"
    }

### Response

    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3NjE4NTk4MSwiaWF0IjoxNjc2MDk5NTgxLCJqdGkiOiI1MDBkNTM2ODcyNjU0MDdhOGNjNzY4ZTYzNTEyY2Q1MCIsInVzZXJfaWQiOjF9.J0wIl9Tj5WzBy69iAIQKIBHn5VwfsYHpfRfosAoHCCw",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc4NjkxNTgxLCJpYXQiOjE2NzYwOTk1ODEsImp0aSI6ImEwMmU4NmZhZjI3NzRiNTVhNjJlNzZhZTlkODI3ZjZkIiwidXNlcl9pZCI6MX0.mVSLFEUOuy8Dwd01RbySFlKnfvwgodrzFnWMwBzo0ik",
        "user": "admin",
        "id": 1,
        "first_name": "Aman",
        "last_name": "Davada",
        "full_name": "Aman Davada",
        "is_superuser": true,
        "email": "amandavda@gmail.com"
    }

## Get Profile for Logined User

### Request

`GET /api/user/get-profile/`

    Request : http://localhost:8000/api/user/get-profile/

### Response

    {
        "username": "admin",
        "id": 1,
        "first_name": "Aman",
        "last_name": "Davada",
        "full_name": "Aman Davada",
        "is_superuser": true,
        "email": "amandavda@gmail.com"
    }

## Dashboard 

### Request

`GET /api/dashboard/`

    Request : http://localhost:8000/api/dashboard/

### Response

    [
        {
            "date": "2023-02-11",
            "coolers": 0
        },
        {
            "date": "2023-02-10",
            "coolers": 0
        },
        {
            "date": "2023-02-09",
            "coolers": 0
        },
        {
            "date": "2023-02-08",
            "coolers": 0
        },
        {
            "date": "2023-02-07",
            "coolers": 0
        },
        {
            "date": "2023-02-06",
            "coolers": 0
        },
        {
            "date": "2023-02-05",
            "coolers": 0
        }
    ]

It will get the data of last 7 days. Here we are getting how many total coolers are sold on that particular day, Like that we are getting last 7 days of data.

## Customer Dashboard

### Request

`POST /api/dashboard`

    Request : http://localhost:8080/api/dashboard/

    {
        "start_date" : "2022-11-20",
        "end_date" : "2022-12-02"
    }

### Response

    [
        {
            "date": "2022-12-02 00:00:00",
            "coolers": 0
        },
        {...},
        {...},
        {...},
        {
            "date": "2022-11-21 00:00:00",
            "coolers": 0
        }
    ]

It will get the data for the custom dates. Here also the same thing we are getting the total coolers on that respective days. 

## Add Routes

### Request

`POST /api/route/`

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

    Request : http://localhost:8000/api/route/{$id}/
    
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

Here we are getting the complete details for that customer.Firstly it will get the customer detail with route info. 

After that it will get all the bill details. The bills which are generated for that customer.
The Daily Entry for this month. With the total coolers.
Total Payments done by that customer. And their total
Due for that customer.

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

## Make Payment

### Request

`POST /api/payment/`

    Request : http://localhost:8000/api/payment/

    {
        "customer_name" : "4d1c3916-70a8-4ae0-a87e-f71a29eca05d",
        "paid_amount" : 800
    }

### Response

    {
        "detail": "Bill Paid and Customer Account Updated"
    }

## Customer Payment List

### Request

`GET /api/customer/payment/{$id}/`

    Request : http://localhost:8000/api/customer/payment/{$id}/

{$id} -> Will be the customer ID

### Response

    {
        "data": [
            {
                "pending_amount": 1800,
                "paid_amount": 800,
                "date": "2023-02-05T14:02:53.983923Z",
                "addedby": "admin"
            },
            {....},
            {....}
        ],
        "total paid amount" : 3700
    }

It will get all the payments done by that customer from start. And at the end of data it will also give the total amount what they have paid to us.

## Current Month Payment List

### Request 

`GET /api/payment/`

    Request : http://localhost:8000/api/payment/

### Response

    {
        "data": [
            {
                "pending_amount": 1800,
                "paid_amount": 800,
                "date": "2023-02-05T14:02:53.983923Z",
                "addedby": "admin"
            },
            {...},
            {...}
        ],
        "total paid amount" : 3700
    }

It will give the data for the payments which are done in this current month. And the Total of paid amount.

## Route Wise Current Month Payment List

### Request

`GET /api/payment/route/{$id}/`

    Request : http://localhost:8000/api/payment/route/{$id}/

### Response

    {
        "data": [
            {
                "pending_amount": 1800,
                "paid_amount": 800,
                "date": "2023-02-05T14:02:53.983923Z",
                "addedby": "admin"
            },
            {...},
            {...}
        ],
        "total paid amount" : 3700
    }

## Bill detail

### Request

`GET /api/bill/{$id}/`

    Request : http://localhost:8000/api/bill/{$id}/

### Response

    {
        "bill" : {
            "id": "ee46b4ed-a937-495e-99f5-a88d5287c46d",
            "from_date": "2023-01-01",
            "to_date": "2023-01-31",
            "coolers": 30,
            "Rate": 20,
            "Amount": 600,
            "Pending_amount": 1200,
            "Advanced_amount": 0,
            "Total": 1800,
            "date": "2022-12-03T00:00:00Z",
            "paid": true,
            "addedby": "admin",
            "updatedby": "admin",
            "customer_name": {
                "id": "4d1c3916-70a8-4ae0-a87e-f71a29eca05d",
                "name": "Sunil Sharma",
                "rate": 20,
                "date_added": "2022-12-10T11:41:14.585339Z",
                "date_updated": "2022-12-10T11:41:14.585355Z",
                "addedby": "admin",
                "updatedby": "admin",
                "active": true,
                "route": "23bc6409-0a78-4f34-8192-62afa07269f2"
            }
        },
        "daily_entry" : [
            {
                "cooler" : 5,
                "date_added" : "2022-12-10T11:41:14.585339Z"
            },
            {...},
            {...}
        ]
    }

## Total Due List

### Request

`GET /api/due/`

    Request : http://localhost:8000/api/due/

### Response

    {
        "customer_due_list": [
            {
                "customer_name": "Elon Musk",
                "due": 2000
            },
            {...},
            {...}
        ],
        "due_total": 4000
    }

It will get all the customer data with there due amount and at the end it will show the due total for the same.

## Due List Route wise

### Request

`GET /api/due/route/{$id}/`

    Request : http://localhost:8000/api/due/route/{$id}/

### Response

    {
        "duelist_data": [
            {
                "customer_name": "Apple",
                "due": 0
            },
            {
                "customer_name": "Elon Musk",
                "due": 2000
            }
        ],
        "due_total": 2000
    }

Here also the same thing but instead of all the customer it will just show the route wise, Which customer are coming under that route.