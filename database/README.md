# Database System

This directory contains the Database System that stores telemetry data and game parameter information.

## Requirements

If running on bare metal:

- Python 3.9 or newer
- All requirements specified in `requirements.txt`
To install all necessary requirements, run the following command:
`pip install -r requirements.txt`

If running through docker:

- CPU supporting virtualisation
- Docker
[Guide to installing Docker Desktop](https://docs.docker.com/desktop/)
[Docker Engine for Linux](https://docs.docker.com/engine/install/)

## Running the server

There are 2 ways to run this server:

### Bare metal

To run the project, inside the database directory, run the following in a terminal window:
`uvicorn main:app --reload`

To verify it is running, in a web browser, visit:
`http://127.0.0.1:8000/docs`
If all is working, you should be brought to the documentation page where you can test the different endpoints.

To stop the server, press `Ctrl+C` in the terminal window in which the server is running.

### Docker

First, build the docker image by running:
`docker build --tag td_database .`

Once it has built the image, start the container with:
`docker run -p 8000:8000 td_database -d`
This runs the container detached so that it runs in the background.

To stop the container, first, run:
`docker ps`
to find the container ID and then run
`docker stop <container_id>`
to stop the container.

## Database Schema

## Defined telemetry entries

None as of yet.

## Defined parameters

None as of yet.
