# Test Suite 

This directory contains the automated test suite for the db and FastAPI backend 

Currently, tests verify API endpoints, datebase models and relationships


## Requirements 

Assumes the `database/` directory is located at the same level as the `tests/` directory

- Python 3.9 or newer
- All requirements specified in `requirements.txt` To install all necessary requirements, run the following command from the `tests/` directory: `pip install -r requirements.txt`

## Running Tests

Run tests from the **project root directory**

To run all tests:
- `pytest`

To run specific tests:
- `pytest tests/api`
- `pytest tests/db`
