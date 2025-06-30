FROM python:3.13.2-slim-bullseye

COPY . /code

WORKDIR /code

RUN apt update
RUN apt upgrade -y
RUN apt install python3-dev default-libmysqlclient-dev build-essential pkg-config nginx -y
RUN pip install -r requirements.txt
RUN chmod +x launch.sh

RUN python manage.py collectstatic

COPY nginx.conf /etc/nginx/sites-available/default

ENV MYSQL_DATABASE=dpelos
ENV MYSQL_USER=admin
ENV MYSQL_PASSWORD=1234
ENV MYSQL_HOST=localhost
ENV MYSQL_PORT=3306

CMD python manage.py migrate && nginx && gunicorn dpelos.wsgi