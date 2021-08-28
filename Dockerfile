FROM tiangolo/uvicorn-gunicorn-fastapi
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./api /app
