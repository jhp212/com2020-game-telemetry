# Database System

This directory contains the Database System that stores telemetry data and game parameter information.

---

## Usage

### Requirements

- Python 3.9 or newer
- All requirements specified in `requirements.txt`

To install all necessary requirements, run the following command:
`pip install -r requirements.txt`

### Running the server

To run the project, inside the database directory, run the following:
`uvicorn main:app --reload`

To verify it is running, in a web browser, visit:
`http://127.0.0.1:8000/docs`
If all is working, you should be brought to the documentation page where you can test the different endpoints.

---

## Database Schema

---

## Defined telemetry entries

None as of yet.

## Defined parameters

None as of yet.
