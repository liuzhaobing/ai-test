#!/bin/bash
export PROJECT_DIR=`pwd`
docker-compose down -rmi all
docker-compose up -d