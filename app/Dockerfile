FROM python:3.8-buster

RUN apt-get update -y
RUN apt-get install python-pip -y

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements/base.txt
RUN pip install -r /app/requirements/base.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

CMD ["python","/app/app.py"]