# Shapes TD 26 - Tower Defence Game

This directory contains the game files for our Tower Defence Game implementation. This project can be run using the Godot Editor or through a FastAPI web server. Please note that the web server

## Requirements

If running on bare metal:

- Python 3.10 or newer
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
`uvicorn app:app --port 10103 --reload`

To verify it is running, in a web browser, visit:
`http://127.0.0.1:10103`
If all is working, you should be brought to the game.

To stop the server, press `Ctrl+C` in the terminal window in which the server is running.

### Docker

First, build the docker image by running:
`docker build --tag td_game .`
inside the database directory. Do not forget the `.` at the end

Once it has built the image, start the container with:
`docker run -p 10103:10103 -d td_game`
This runs the container detached so that it runs in the background.

To stop the container, first, run:
`docker ps`
to find the container ID and then run
`docker stop <container_id>`
to stop the container.
