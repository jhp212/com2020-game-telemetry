# Simple Tower Defence Game with Telemetry and Balancing Toolkit

A simple tower defence game that records user telemetry data in order to facilitate the balancing of the game. Actions that the user takes in game and any other events that may happen, are recorded and sent to a dashboard, where admin users can change game parameters. Admins can use the simulation mode to see if their changes have made a difference.

## System Architecture

- 3 components
  - The Game: Godot based project exported to a web build, running through a FastAPI/Python server.
  - The Dashboard: FastAPI based web dashboard, incorporating HTML, CSS, JavaScript, and ChartJS.
  - The Database: FastAPI based API connecting to a SQLite database, facilitating the communication between Game and Dashboard.
- Each component runs in a seperate docker container, with a docker compose script to deploy them all.

## Key Features

- User Authentication using JSON Web Tokens.
- Argon2 password hashing.
- Role based security. 2 user types: Player and Admin
- Seperate services so they can be run on seperate machines.

### Game

- 10 levels, each with their own waves
- 3 difficulty levels
- 3 enemy types
- Boss Battles
- 3 Towers with upgrade paths

### Dashboard

- 5 graphs, giving a visual representation for the data.
- Page to view all telemetry events.
- Parameter editor to tweak the balancing of the game.
- Decision log to show when parameters where changed, by who, and why.
- Balancing rules to automatically suggest changes.
- Simulation mode: simulated agents playing the game. Gives a success percentage for a specific level on a specific difficulty.
- Telemetry anomalies: Dashboard detects anomalies in the telemetry, such as impossible ordering of events.
- Unauthenticated accounts can request access to the dashboard. Must be approved by an existing admin.

## Group Members

- Jake Phillips (Project Owner - Data Lead)
- Oliver Robson (Scrum Master - Documentation)
- Doruk Aksu (Dev team - Tech lead)
- Dylan Davies (Dev team - Software dev)
- Bela Rothfuss Moore (Dev team - QA & Testing)
- Thomas Wilkin-Jones (Dev team - Game dev)
- Zak Salmon (Dev team - Dashboard dev)

## Usage

To run the entire project, we use Docker Compose to deploy 3 containers:
- Database API Server on port 10101
- Dashboard Server on port 10102
- Game Web Server on port 10103

### Requirements

- CPU supporting virtualisation
- Docker

[Guide to installing Docker Desktop](https://docs.docker.com/desktop/)<br>
[Docker Engine for Linux](https://docs.docker.com/engine/install/)

### Deploying the containers

First, run Docker Desktop if you have it installed. Then, clone the git repository into a new directory. In the root directory of the project, on the same level as `docker-compose.yaml` run:<br>
`docker compose up --build -d`<br>
This will download, build, and deploy every container. To verify it is working, visit:

- `http://localhost:10102` You should see the dashboard.
- `http://localhost:10103` You should see the game.

  *Note: the game requires an HTTPS connection to access it on any other device that isn't the one that's running Docker. Consider using reverse proxies such as nginx or Caddy*

### Individual READMEs

Each directory contains its own README.md file containing extra information pertaining to that specific section of the project
