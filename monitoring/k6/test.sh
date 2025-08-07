# Run load test
docker-compose --profile load-test run --rm k6 run /scripts/load-test.js

# Run stress test
docker-compose --profile load-test run --rm k6 run /scripts/stress-test.js

# Run spike test
docker-compose --profile load-test run --rm k6 run /scripts/spike-test.js