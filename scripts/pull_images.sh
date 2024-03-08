#!/usr/bin/env bash


docker-compose pull reverse-proxy
docker-compose pull db
docker-compose pull redis
docker-compose pull nginx

# $1 is the parameter passed in
docker-compose pull $1
