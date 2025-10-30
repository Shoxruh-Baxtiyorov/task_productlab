# FROM python:3.11
FROM public.ecr.aws/sam/build-python3.11:latest

WORKDIR /backend

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
