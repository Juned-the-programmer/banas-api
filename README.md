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

    Request : http"//localhost:8000/api/route/
    
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

`PUT /api/route/`