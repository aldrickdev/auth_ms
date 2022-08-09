FROM python:3.10.0
WORKDIR /app/auth_ms
COPY requirements/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
WORKDIR /app
