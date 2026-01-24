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
`uvicorn main:app --port 10101 --reload`

To verify it is running, in a web browser, visit:
`http://127.0.0.1:10101/docs`
If all is working, you should be brought to the documentation page where you can test the different endpoints.

To stop the server, press `Ctrl+C` in the terminal window in which the server is running.

### Docker

First, build the docker image by running:
`docker build --tag td_database .`
inside the database directory. Do not forget the `.` at the end

Once it has built the image, start the container with:
`docker run -p 10101:10101 td_database -d`
This runs the container detached so that it runs in the background.

To stop the container, first, run:
`docker ps`
to find the container ID and then run
`docker stop <container_id>`
to stop the container.

## Database Schema

[Link to the Google Doc containing the schema](https://docs.google.com/document/d/1bH9D6rqOORPg6F0HKWtgtwtgyDObWbTXG5sBDbqe-9g/edit?usp=sharing)

## Defined telemetry entries

- stage_start {}
- stage_end {}
- enemy_defeated {enemy_id: Integer}
- damage_taken {amount: Integer, remaining_health: Integer}
- tower_spawn {tower_id: Integer}
- tower_upgrade {tower_id: Integer, upgrade_id: Integer}
- money_spent {amount: Integer, remaining_amount: Integer}

## Defined parameters

- enemy_damage_multiplier {value: float}

## Balancing rules

- enemy_damage_stage_fail_rate {"If the death rate is greater than __%, reduce the enemy_damage_multipler"}
