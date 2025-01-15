#!/bin/bash

### 3225_system_services.sh
locust -f utils/locust/locust_talk.py --test-config testsuite/talk/3225_system_services.json -H sv-grpc.wispirit.raysengine.com:9443 --web-port 9998 --web-host 0.0.0.0 --processes 5
### 3222_objective_oriented_open_domain.json
locust -f utils/locust/locust_talk.py --test-config testsuite/talk/3222_objective_oriented_open_domain.json -H sv-grpc.wispirit.raysengine.com:9443 --web-port 9998 --web-host 0.0.0.0 --processes 5
### 3222_subjective_oriented_open_domain.json
locust -f utils/locust/locust_talk.py --test-config testsuite/talk/3222_subjective_oriented_open_domain.json -H sv-grpc.wispirit.raysengine.com:9443 --web-port 9998 --web-host 0.0.0.0 --processes 5
### 3226_ali.json
locust -f utils/locust/locust_talk.py --test-config testsuite/talk/3226_ali.json -H sv-grpc.wispirit.raysengine.com:9443 --web-port 9998 --web-host 0.0.0.0 --processes 5
