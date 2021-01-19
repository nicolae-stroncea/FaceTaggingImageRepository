
# pull official base image
FROM python:3.8.1-slim-buster

# set work directory
WORKDIR /usr/src/detector

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/detector/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/detector

EXPOSE 5001

ENTRYPOINT ["/usr/src/detector/entrypoint.sh"]
