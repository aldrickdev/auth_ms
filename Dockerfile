FROM python:3.10.0
WORKDIR /app
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt
COPY auth_ms /app