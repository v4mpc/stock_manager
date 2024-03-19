#!/usr/bin/env sh


git pull
docker-compose -f docker-compose-dev.yml up -d --no-deps --force-recreate --build  web
