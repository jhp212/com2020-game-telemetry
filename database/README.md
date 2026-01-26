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
`docker run -p 10101:10101 -d td_database`
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

## Endpoints

<details>
<summary><strong>Click to expand API Endpoint Documentation</strong></summary>

### Telemetry

Manage user and stage telemetry data.

**Create Telemetry**

- Method: POST
- URL: `/telemetry/`
- Creates a new telemetry entry

JSON Request Body:

| Field            | Type               | Required | Description                  |
| ---------------- | ------------------ | -------- | ---------------------------- |
| `user_id`        | Integer            | Yes      | The ID of the user           |
| `stage_id`       | Integer            | Yes      | The ID of the current stage  |
| `telemetry_type` | String             | Yes      | The telemetry category       |
| `dateTime`       | String (date-time) | Yes      | The timestamp of the event   |
| `data`           | Object             | Yes      | Additional JSON data payload |

**Read Telemetry**

- Method: GET
- URL: `/telemetry/`
- Retrieves a list of telemetry entries based on filter criteria

Query Parameters:

| Field          | Type               | Required | Description                     |
| -------------- | ------------------ | -------- | ------------------------------- |
| `telemetry_id` | Integer            | No       | Filter by specific Telemetry ID |
| `user_id`      | Integer            | No       | Filter by User ID               |
| `stage_id`     | Integer            | No       | Filter by Stage ID              |
| `start_time`   | String (date-time) | No       | Filter by start range           |
| `end_time`     | String (date-time) | No       | Filter by end range             |

---

### Parameters

Manage global configuration parameters.

**Create Parameter**

- Method: POST
- URL: `/parameters/`
- Creates a new configuration parameter

JSON Request Body:

| Field   | Type    | Required | Description                        |
| ------- | ------- | -------- | ---------------------------------- |
| `name`  | String  | Yes      | The name of the parameter          |
| `value` | Integer | Yes      | The numeric value of the parameter |

**Read Parameters**

- Method: GET
- URL: `/parameters/`
- Retrieves parameters, optionally filtering by name

Query Parameters:

| Field            | Type   | Required | Description                    |
| ---------------- | ------ | -------- | ------------------------------ |
| `parameter_name` | String | No       | Filter by exact parameter name |

---

### Balancing Rules

Manage rules for system balancing logic.

**Create Balancing Rule**

- Method: POST
- URL: `/balancing_rules/`
- Creates a new balancing rule

JSON Request Body:

| Field               | Type   | Required | Description                          |
| ------------------- | ------ | -------- | ------------------------------------ |
| `trigger_condition` | String | Yes      | The condition that triggers the rule |
| `suggested_change`  | String | Yes      | The change proposed by this rule     |
| `explanation`       | String | No       | Optional explanation for the rule    |

**Read Balancing Rules**

- Method: GET
- URL: `/balancing_rules/`
- Retrieves balancing rules

Query Parameters:

| Field     | Type    | Required | Description       |
| --------- | ------- | -------- | ----------------- |
| `rule_id` | Integer | No       | Filter by Rule ID |

---

### Decision Logs

Manage logs regarding system decisions and rationale.

**Create Decision Log**

- Method: POST
- URL: `/decision_logs/`
- Creates a new log entry for a decision made

JSON Request Body:

| Field            | Type               | Required | Description                    |
| ---------------- | ------------------ | -------- | ------------------------------ |
| `parameter_name` | String             | Yes      | Name of the parameter affected |
| `stage_id`       | Integer            | No       | Related Stage ID               |
| `change`         | String             | Yes      | Description of the change made |
| `rationale`      | String             | Yes      | Reasoning behind the decision  |
| `evidence`       | String             | No       | Supporting evidence            |
| `dateTime`       | String (date-time) | Yes      | Timestamp of the decision      |

**Read Decision Logs**

- Method: GET
- URL: `/decision_logs/`
- Retrieves decision logs based on filter criteria

Query Parameters:

| Field            | Type               | Required | Description              |
| ---------------- | ------------------ | -------- | ------------------------ |
| `decision_id`    | Integer            | No       | Filter by Decision ID    |
| `parameter_name` | String             | No       | Filter by Parameter Name |
| `stage_id`       | Integer            | No       | Filter by Stage ID       |
| `start_time`     | String (date-time) | No       | Filter by start range    |
| `end_time`       | String (date-time) | No       | Filter by end range      |

</details>
