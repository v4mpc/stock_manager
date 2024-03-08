#!/usr/bin/env bash



docker-compose down
docker-compose up --build --force-recreate -d
docker network connect superset-itn-portal-net itn-portal_db_1