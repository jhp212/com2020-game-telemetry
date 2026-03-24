# Simple Tower Defence Game with Telemetry and Balancing Toolkit

A simple tower defence game that records user telemetry data in order to facilitate the balancing of the game. Actions that the user takes in game and any other events that may happen, are recorded and sent to a dashboard, where admin users can change game parameters. Admins can use the simulation mode to see if their changes have made a difference.

## System Architecture

- 3 components
  - The Game: Godot based project exported to a web build, running through a FastAPI/Python server.
  - The Dashboard: FastAPI based web dashboard, incorporating HTML, CSS, JavaScript, and ChartJS.
  - The Database: FastAPI based API connecting to a SQLite database, facilitating the communication between Game and Dashboard.
- Each component runs in a separate docker container, with a docker compose script to deploy them all.

## Key Features

- User Authentication using JSON Web Tokens.
- Argon2 password hashing.
- Role based security. 2 user types: Player and Admin
- Separate services so they can be run on separate machines.

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
- Decision log to show when parameters were changed, by who, and why.
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

### Configuration

You will need to configure a .env file with two keys: SECRET_KEY, and HTTPS_ONLY. The first is used for JSON Web Token encoding. Keeping this key secure is vital, as if someone finds what it is, they can generate valid tokens for your installation without being authorised. The second key dictates whether cookies from the dashboard should only be stored if the user is connected through an HTTPS connection. This value can either be true or false. An example configuration is shown:

SECRET_KEY=*insert secure key here*<br>
HTTPS_ONLY=true

If the .env file is not created, the default keys are

SECRET_KEY=SUPER_SECRET_DEV_KEY_CHANGE_IN_PRODUCTION<br>
HTTPS_ONLY=false

### Deploying the containers

First, run Docker Desktop if you have it installed. Then, clone the git repository into a new directory. In the root directory of the project, on the same level as `docker-compose.yaml` run:

```bash
docker compose up --build -d
```

Or, if you are using an older Docker version, run:

```bash
docker-compose up --build -d
```

This will download, build, and deploy every container. To verify it is working, visit:

- `http://localhost:10102` You should see the dashboard.
- `http://localhost:10103` You should see the game.

  *Note: the game requires an HTTPS connection to access it on any other device that isn't the one that's running Docker. Consider using reverse proxies such as nginx or Caddy*

### Individual READMEs

Each directory contains its own README.md file containing extra information pertaining to that specific section of the project

## Links

[GitHub Link](https://github.com/jhp212/com2020-game-telemetry)<br>
[Scrum Board](https://trello.com/b/XYXJPd5i/team-project)

[Game URL](https://gamev2.mm25564.uk)<br>
[Dashboard URL](https://dashboardv2.mm25564.uk)
