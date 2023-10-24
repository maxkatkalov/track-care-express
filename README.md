# Care Express

Care Express is a comprehensive service provided at train stations designed to enhance the overall passenger experience and ensure the safety, convenience, and satisfaction of travelers.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [DB scheme](https://monosnap.com/file/rLG56LIZWY1h6Rsa29PjaRvvL2Jrqc)
- [Online demo](#online-demo)
- [User permissions](#user-permissions)

## Getting Started

These instructions will help you get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3 must be installed on your machine.
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Online demo

- You can access the online project demo [here](https://care-express-api.techone.pp.ua/api/care-express/).

- For [login](https://care-express-api.techone.pp.ua/api/station-user/token/login/) (admin with prepared order data), you can use the following credits:

   **Email:** admin@gmail.com

   **Password:** admin@gmail.com

   Or you can [register](https://care-express-api.techone.pp.ua/api/station-user/register/) a new user.

- For exploring the API endpoints, access the documentation:

  - [Swagger](https://care-express-api.techone.pp.ua/api/doc/swagger/)
  - [Redoc](https://care-express-api.techone.pp.ua/api/doc/redoc/)

### Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/maxkatkalov/track-care-express-api.git

2. Clone the repository:

   ```shell
   cd track-care-express-api

3. Create a .env file and configure the environment variables required by your project. You can use the provided .env.example as a starting point.

   ```shell
   cp .env.example .env

4. Start the Docker daemon on your machine. Build and start the Docker containers:

   ```shell
   docker-compose up --build

5. Create SU:
   ```shell	
   docker ps

Connect to your Docker container: ```docker exec -it <your Docker image id> bash```

Then: ```python manage.py createsuperuser```
6. Access the application in your web browser at http://127.0.0.1:8000/api/care-express/

7. To have access in browser or to send requests to all API endpoints you need to send Authorization header along with your request:
   
   - For browsers you can use [ModHeader](https://modheader.com/?ref=me&product=ModHeader&version=5.0.7&browser=chrome).
   - [Postman](https://monosnap.com/file/yX9vn5LwypObGy1nRNBC6NLlGaSdBj).
   - Default lifetime of JWT: 60 minutes. You can change this value in settings.py.

8. You also can install prepared fixtures after creating the SU. Run commands in following order (alter: use [button](https://monosnap.com/file/VRBg2gl0IFtfI3btNB7GatqTqjpKVQ) in PyCharm):

   ```shell
   python3 manage.py loaddata stations.json
   python3 manage.py loaddata routes.json
   python3 manage.py loaddata train_types.json
   python3 manage.py loaddata trains.json
   python3 manage.py loaddata crew.json
   python3 manage.py loaddata tickets.json
   python3 manage.py loaddata orders.json

### User permissions

- Unauthorised users can access only Api Root endpoint;

- Authorised users can make List and Retrieve actions on all endpoints; Create, Update, List and Retrieve on the Order's endpoint.

- Admin can make all actions on every API endpoint besides Delete on Order's one.


