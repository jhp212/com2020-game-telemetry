# Database System

This directory contains the Database System that stores telemetry data and game parameter information.

## Main Contributors

- Jake Phillips

## Database Schema

[Link to the Google Doc containing the schema](https://docs.google.com/document/d/1bH9D6rqOORPg6F0HKWtgtwtgyDObWbTXG5sBDbqe-9g/edit?usp=sharing)

## Defined telemetry entries

- stage_start {}
- stage_end {}
- stage_fail {}
- stage_quit {}
- enemy_defeated {enemy_id: Integer}
- damage_taken {amount: Integer, remaining_health: Integer}
- tower_spawn {tower_id: Integer}
- tower_upgrade {tower_id: Integer, upgrade_id: Integer}
- money_spent {amount: Integer, remaining_amount: Integer}
- boss_start {}
- boss_fail {}
- boss_defeated {}

## Defined parameters

- enemy_damage_multiplier {value: float}
- enemy_speed_multiplier {value: float}
- money_earned_multiplier {value: float}
- easy_health_multiplier {value: float}
- medium_health_multiplier {value: float}
- hard_health_multiplier {value: float}
- triangle_radius_multiplier {value: float}
- star_radius_multiplier {value: float}

## Balancing rules

- enemy_damage_stage_fail_rate {"If the death rate is greater than __%, reduce the enemy_damage_multipler"}

## Endpoints

### Authentication

Manage user registration, login, and admin access.

**Register User**

- Method: POST
- URL: `/auth/register`
- Creates a new user account

JSON Request Body:

| Field     | Type   | Required | Description                                       |
| --------- | ------ | -------- | ------------------------------------------------- |
| `username`| String | Yes      | Username (3-20 chars, alphanumeric + _)           |
| `password`| String | Yes      | Password (8+ chars, upper, lower, digit, special) |

**Login**

- Method: POST
- URL: `/auth/token`
- Authenticates user and returns JWT token

Form Data:

| Field     | Type   | Required | Description |
| --------- | ------ | -------- | ----------- |
| `username`| String | Yes      | Username    |
| `password`| String | Yes      | Password    |

**Request Admin Access**

- Method: POST
- URL: `/auth/request_admin`
- Allows current user to request admin privileges

**Promote User to Admin** (Admin only)

- Method: POST
- URL: `/auth/promote/{username}`
- Grants admin access to specified user

**Reject Admin Request** (Admin only)

- Method: POST
- URL: `/auth/reject_admin/{username}`
- Rejects admin request for specified user

**Delete Account**

- Method: DELETE
- URL: `/auth/delete_account`
- Deletes current user's account and all associated data

### Users

Manage user accounts (Admin only).

**Get All Users**

- Method: GET
- URL: `/users`
- Retrieves all users

**Delete User**

- Method: DELETE
- URL: `/users/{username}`
- Deletes specified user (cannot delete admins)

**Get Admin Requests**

- Method: GET
- URL: `/users/admin_requests`
- Retrieves users requesting admin access

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

**Read Telemetry** (Admin only)

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

**Delete Telemetry** (Admin only)

- Method: DELETE
- URL: `/telemetry/{telemetry_id}`
- Deletes specified telemetry entry

### Parameters

Manage global configuration parameters.

**Create or Update Parameter** (Admin only)

- Method: POST
- URL: `/parameters/`
- Creates or updates a configuration parameter

JSON Request Body:

| Field   | Type    | Required | Description                        |
| ------- | ------- | -------- | ---------------------------------- |
| `name`  | String  | Yes      | The name of the parameter          |
| `value` | Float   | Yes      | The numeric value of the parameter |

**Read Parameters**

- Method: GET
- URL: `/parameters/`
- Retrieves parameters, optionally filtering by name

Query Parameters:

| Field            | Type   | Required | Description                    |
| ---------------- | ------ | -------- | ------------------------------ |
| `parameter_name` | String | No       | Filter by exact parameter name |

### Balancing Rules

Manage rules for system balancing logic (Admin only).

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

### Decision Logs

Manage logs regarding system decisions and rationale (Admin only).

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

### Anomalies

Manage anomaly detection and resolution (Admin only).

**Create Anomaly**

- Method: POST
- URL: `/anomalies/`
- Creates a new anomaly and associates it with telemetry entries

JSON Request Body:

| Field            | Type         | Required | Description                          |
| ---------------- | ------------ | -------- | ------------------------------------ |
| `telemetry_ids`  | Array[Int]   | Yes      | List of telemetry entry IDs          |
| `anomaly_type`   | String       | Yes      | Type of anomaly                      |
| `resolution`     | String       | No       | Resolution description               |

**Read Anomalies**

- Method: GET
- URL: `/anomalies/`
- Retrieves anomalies with optional filters

Query Parameters:

| Field          | Type    | Required | Description                 |
| -------------- | ------- | -------- | --------------------------- |
| `anomaly_id`   | Integer | No       | Filter by Anomaly ID        |
| `telemetry_id` | Integer | No       | Filter by Telemetry ID      |
| `anomaly_type` | String  | No       | Filter by Anomaly Type      |

**Get Telemetry for Anomaly**

- Method: GET
- URL: `/anomalies/{anomaly_id}/telemetry`
- Retrieves all telemetry entries associated with an anomaly

**Resolve Anomaly**

- Method: POST
- URL: `/anomalies/{anomaly_id}/resolve`
- Marks an anomaly as resolved

JSON Request Body:

| Field        | Type   | Required | Description            |
| ------------ | ------ | -------- | ---------------------- |
| `resolution` | String | Yes      | Resolution description |

**Clear All Anomalies**

- Method: DELETE
- URL: `/anomalies/clear-all`
- Deletes all anomalies and linked telemetry entries
