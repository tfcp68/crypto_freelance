#!/bin/bash

docker compose -f docker-compose.yaml up -d redis js_api ganache_network

docker compose -f docker-compose.yaml up -d web
