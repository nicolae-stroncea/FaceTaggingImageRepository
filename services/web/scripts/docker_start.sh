#!/bin/bash

docker-compose build
# remove unused images
docker rmi $(docker images -f "dangling=true" -q)
docker-compose up