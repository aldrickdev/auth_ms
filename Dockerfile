FROM python:3.10.0
WORKDIR /app/auth_ms
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt
COPY auth_ms .
WORKDIR /app