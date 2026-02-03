# Telemetry Dashboard with Balancing Toolkit

This directory contains the Telemetry Dashboard implementation built with FastAPI and Jinja2.
It is designed to display telemetry data from a database in structured tables.

## Tech Stack

    * Python 3.10
    * FastAPI
    * Jinja2
    * Uvicorn
    * HTML + CSS

## Usage

**NOTE: This service requires an implementation of the database API.**<br>
By default, the app assumes it is running on `http://127.0.0.1:10101`. If this is not the case, set the API_URL environment variable to the correct URL. If you are using docker, you can change this in the Dockerfile.

There are 2 ways to run this service, either on bare metal or inside a docker container

### Requirements

If running on bare metal:

- Python 3.10 or newer
- All requirements specified in `requirements.txt`
To install all necessary requirements, run the following command:
`pip install -r requirements.txt`

If running through docker:

- CPU supporting virtualisation
- Docker<br>
[Guide to installing Docker Desktop](https://docs.docker.com/desktop/)<br>
[Docker Engine for Linux](https://docs.docker.com/engine/install/)

### Bare metal

To run the project, inside the dashboard directory, run the following in a terminal window:
`uvicorn app:app --port 10102 --reload`

To verify it is running, in a web browser, visit:
`http://127.0.0.1:10102/`
If all is working, you should be brought to the dashboard.

To stop the server, press `Ctrl+C` in the terminal window in which the server is running.

### Docker

First, build the docker image by running:
`docker build --tag td_dashboard .`
inside the dashboard directory. Do not forget the `.` at the end

Once it has built the image, start the container with:
`docker run -p 10102:10102 -d td_dashboard`
This runs the container detached so that it runs in the background.

To stop the container, first, run:
`docker ps`
to find the container ID and then run
`docker stop <container_id>`
to stop the container.
