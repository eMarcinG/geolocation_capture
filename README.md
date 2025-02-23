#
# Geolocation capture app
#

# Geolocation capture app

This project implements a simple RESTful API for storing and retrieving geolocation data.  It uses the ipstack.com / ipinfo.io service to enrich IP addresses and URLs with geolocation information.  The API allows for adding, deleting, and retrieving geolocation data based on IP address or URL.  The application is designed to handle various error conditions, such as database or ipstack.com service unavailability.  It includes basic test coverage and can be easily deployed using Docker.  

## Features

Dockerized: 
The application is packaged and runs within a Docker container, ensuring consistent execution across different environments and simplifying deployment.

Automated Superuser Creation: 
The application automatically creates a superuser account upon initialization, streamlining initial setup and administration.

Role-Based Access Control: 
Different user roles are implemented, each with specific access levels and permissions, enhancing security and data management.

Database Replication: 
The database is replicated to ensure data availability and redundancy. In case of issues with the primary database, the application seamlessly switches to the replica.

Database Failover: 
The application is designed to automatically switch to a replica database in the event of a failure or unavailability of the primary database, minimizing downtime.

Dual URL Data Ingestion: 
The application fetches data from two distinct URLs, providing a comprehensive and diverse dataset for processing.

Asynchronous Task Processing: 
Celery is used to handle data processing asynchronously, improving performance and responsiveness by offloading tasks to a queue.

Comprehensive Unit Tests:
Unit tests are implemented for all endpoints, ensuring code quality, reliability, and maintainability.

## Requirements

- Docker
- Docker Compose

## Installation

### Step 1: Clone the repository

git clone https://github.com/eMarcinG/geolocation_capture.git

### Step 2: Copy a .env file included into email.

Copy attached .env file into the base project ( added to email )

### Step 3:  Build and run Docker containers

Build and run the Docker containers using Docker Compose:

docker-compose up --build

please note: 
* superuser account will be created automatically based on .env data

#### Usage

# Accessing the Admin Panel

Accessing the Admin Panel
You can access the Django admin panel by navigating to http://localhost:8000/admin 
and logging in with the superuser credentials.
please note: 
* use admin panel to create user

# Accessing the API

The API endpoints are available at http://localhost:8000/api/.

please note:
It is highly recommended to instal REST Client extension (for Visual Studio Code) 
and simply use the file "new.http" with all available endpoints.


POST http://localhost:8002/api/token/

 Obtain an access and refresh token by providing your username and password in the request body

POST http://localhost:8002/api/geolocations/fetch/ 

Fetch geolocation data for a given IP address or URL and store it asynchronously.  Provide either ip or url in the request body

{
    "ip": "1.1.1.1", | "url": "google.com"
}

GET http://localhost:8002/api/geolocations/search/?url=www.interia.pl

Search for geolocation data by IP address or URL. Provide either ip or url as query parameters

GET http://localhost:8002/api/geolocations/

( endpoint reseved only for admin )

GET /geolocations/{id}/: Retrieve a specific geolocation entry by its ID.

PUT /geolocations/{id}/: Update a specific geolocation entry. Requires admin privileges. Provide the updated data in the request body (JSON format).

PATCH /geolocations/{id}/: Partially update a specific geolocation entry. Requires admin privileges. Provide the data to be updated in the request body (JSON format).

DELETE /geolocations/{id}/: Delete a specific geolocation entry. Requires admin privileges.

POST /geolocations/fetch/: Fetch geolocation data for a given IP address or URL and store it asynchronously.  Provide either ip or url (or both) in the request body (JSON format).


# Development
Running Tests
To run tests, use the following command:

docker-compose exec web_gc python manage.py test

# Contributing
Contributions are welcome! 
Please create a pull request or open an issue for any improvements or bugs.

# License
This project is licensed under the MIT License. 