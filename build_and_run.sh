#!/bin/bash

docker-compose down
docker-compose build --no-cache 
docker-compose up -d

sleep 10s

docker-compose logs --no-color
