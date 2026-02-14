FROM python:3.14-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r dashboard/requirements.txt

EXPOSE 10102

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# If the database API is not on 127.0.0.1:10101, uncomment and set the correct URL
# ENV API_URL=http://127.0.0.1:10101

CMD ["uvicorn", "dashboard.app:app", "--host", "0.0.0.0", "--port", "10102", "--reload"]