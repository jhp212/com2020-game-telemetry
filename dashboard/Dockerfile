FROM python:3.14-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10102

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10102", "--reload"]