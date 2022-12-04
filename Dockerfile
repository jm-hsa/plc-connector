# syntax=docker/dockerfile:1
FROM python:3-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt
COPY ./app/ /app/

EXPOSE 102

CMD ["python3", "main.py"]