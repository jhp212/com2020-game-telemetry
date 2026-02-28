FROM python:3.14-slim

COPY . /database/

RUN pip install --no-cache-dir -r /database/requirements.txt

EXPOSE 10101

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "database.main:app", "--host", "0.0.0.0", "--port", "10101", "--reload"]