# Authentication

This project is a simple API that provides basic Authentication and Authorization.

## How to run the application

### Running directly on your host machine

This project uses Python version 3.10 so this should be the minimum Python version needed to run 
the application. 

After confirming that you have an adequate version of Python, create a virtual environment with 
your prefered virtual environment tools and install all of the packages in the `requirements.txt`. 
To do this change your directory to `auth/backend` run `pip install -r requirements.txt`. 

Once all of the required Python packages are installed you will need to make a copy of the 
`.env.example` file located in the directory `auth/backend` and call it `.env` and place it in the 
same directory. Once you create this file you will need to fill out the environment variables with 
the values found in the `Auth .env file` tab in 
[This Google Sheet](https://docs.google.com/spreadsheets/d/16vIzIN_jM-lJo98UN8C_sggKuOpwblIcs3CBbEVUUwg/edit?usp=sharing). 

Now that your virtual environment has all of the packages installed and your environment variables 
are setup, you should be able to run the application locally without any issues, except for the 
Database. To start the application go to the directory `auth/backend/app` and run the command 
`python main.py`. The application should run but if you get a timeout error due to not being able 
to connect to MongoDB, go to the 
**Connecting the local application to the remote MongoDB Instance** section as this shows how to 
solve this problem. 

To stop the application press `CTRL + C`.

### Running in a docker container

To run the application using Docker you need to have Docker installed. If you don't have it 
installed, you can follow the instructions at [Docker Docs | Get Docker](https://docs.docker.com/get-docker/). 

Once it is installed go to the directory `auth/backend` and run 
`docker build -f docker/app.Dockerfile -t greymint_auth:0.0.1 .` this command will build the Docker 
image that will be used to run the container. 

Once the image has been created you can create a container based on that image. To start the 
container run the command `docker compose -f docker/compose.yaml --env-file .env up`. This command 
should start up the application in a Docker container. To stop the container, you can use 
`CTRL + C`. 


## Connecting the local application to the remote MongoDB Instance

If you tried running the application for the first time either locally or via Docker, you might've 
encountered the issue where the application hangs and then fails with an issue stating that it 
wasn't able to connect to MongoDB. This happens because the MongoDB instance needs to have your IP 
address in the allowlist. 

For this you will need to login to [Atlas MongoDB](https://account.mongodb.com) using the 
credentials found in the `Account Services` tab in 
[This Google Sheet](https://docs.google.com/spreadsheets/d/16vIzIN_jM-lJo98UN8C_sggKuOpwblIcs3CBbEVUUwg/edit?usp=sharing). 

Once you have logged in, select the `test_one` Project then on the left, select `Network Access` 
then click `ADD IP ADDRESS`. This will allow your IP Address to access the Database, which then 
allows the application to access the Database. Note that if your IP Address changes often you will 
need to do this everytime your IP Address changes.

Run the application again using one of the methods above and it should successfully start up.

## Using the Application

When the application is running, you can access it via port `3000`. To see the application in the 
browser go to [localhost:3000/docs](http://localhost:3000/docs), there you will see the endpoints 
that the application exposes that can be used to interact with it. An example of the page you 
should see is below.

![Image of the exposed endpoints](https://p95.f4.n0.cdn.getcloudapp.com/items/ApuDdG05/31bc6f08-6f59-4b78-99c8-1c5a493eee33.jpg?v=2883e9ff4af1bd03b9018a4ed7b16b80)

## Endpoints

<table>
<tr>
<th>Method</th>
<th>URL</th>
<th>Description</th>
<th>Curl Example</th>
</tr>

<tr>
<td>GET</td>
<td>/api/v1/user/details</td>
<td>Endpoint used to get the current users details</td>
<td>

``` bash
curl -X 'GET' \
'http://<DOMAIN>/api/v1/user/details/' \
-H 'accept: application/json' \
-H 'Authorization: Bearer <TOKEN>'
```

</td>
</tr>

<tr>
<td>POST</td>
<td>/api/v1/user/new-email/?provided_email={EMAIL}</td>
<td>Endpoint used to begin the sign up process</td>
<td>

``` bash
curl -X 'POST' \
'http://<DOMAIN>/api/v1/user/new-email/?provided_email=<EMAIL>' \
-H 'accept: application/json' \
-d ''
```

</td>
</tr>

<tr>
<td>POST</td>
<td>/api/v1/user/new-user/{UUID}</td>
<td>Endpoint used to complete the sign up process</td>
<td>

``` bash
curl -X 'POST' \
'http://<DOMAIN>/api/v1/user/new-user/<UUID>' \
-H 'accept: application' \
-H 'Content-Type: application/json' \
-d '{"username": "<USERNAME>", "password": "<PASSWORD>"}'
```

</td>
</tr>

<tr>
<td>POST</td>
<td>/api/v1/user/token</td>
<td>Endpoint used to get a token for a user based on their email and password</td>
<td>

``` bash
curl -X 'POST' \
'http://<DOMAIN>/api/v1/user/token/' \
-H 'accept: application/json' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'grant_type=&username=<EMAIL>&password=<PASSWORD>&scope=&client_id=&client_secret='
```

</td>
</tr>

<tr>
<td>POST</td>
<td>/api/v1/user/forgot-password</td>
<td>Endpoint used to begin the process to update their password that a user forgot</td>
<td>

``` bash
curl -X 'POST' \
'http://<DOMAIN>/api/v1/user/forgot-password' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{"email": "<EMAIL>"}'
```

</td>
</tr>

<tr>
<td>POST</td>
<td>/api/v1/user/reset-password/{UUID}</td>
<td>Endpoint used to complete the process our resetting a users password</td>
<td>

``` bash
curl -X 'POST' \
'http://<DOMAIN>/api/v1/user/reset-password/<UUID>' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{"password": "<PASSWORD>"}'
```

</td>
</tr>
<tr>
<td>PUT</td>
<td>/api/v1/user/edit</td>
<td>Endpoint used to edit the email and/or role of a user</td>
<td>

``` bash
curl -X 'PUT' \
'http://<DOMAIN>/api/v1/user/edit' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer <TOKEN>' \
-d '{"email": "<EMAIL>", "role": "<ROLE>"}'
```

</td>
</tr>
<tr>
<td>PUT</td>
<td>/api/v1/user/disable</td>
<td>Endpoint used to disable a user</td>
<td>

``` bash
curl -X 'POST' \
'http://<DOMAIN>/api/v1/user/disable' \
-H 'accept: application/json' \
-H 'Authorization: Bearer <TOKEN>'
```

</td>
</tr>
<tr>
<td>PUT</td>
<td>/api/v1/user/update-password</td>
<td>Endpoint used to update the password of a user that is logged in</td>
<td>

``` bash
curl -X 'POST' \
'http://<DOMAIN>/api/v1/user/update-password' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer <TOKEN>' \
-d '{"password":"<PASSWORD>"}'
```

</td>
</tr>
</table>
