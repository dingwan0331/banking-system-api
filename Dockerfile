FROM python:3.8

RUN mkdir /code

WORKDIR /code

ADD ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

ADD . /code

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "config.wsgi:application" ]