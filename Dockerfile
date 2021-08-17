FROM tiangolo/uvicorn-gunicorn-fastapi:python3

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./api /app
