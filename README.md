# Simple Tower Defence Game with Telemetry and Balancing Toolkit

A simple tower defence game that records user telemetry data in order to facilitate the balancing of the game.

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

First, clone the git repository into a new directory. Then, in the root directory of the project, run:<br>
`docker compose up --build -d`<br>
This will download, build, and deploy every container. To verify it is working, visit:

- `http://localhost:10102` You should see the dashboard.
- `http://localhost:10103` You should see the game.

### Individual Services (Not Recommended)

Please refer to the README files in each service's folder for information on how to run that service individually.