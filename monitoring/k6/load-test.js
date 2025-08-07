import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export const errorRate = new Rate('errors');

export const options = {
    stages: [
        { duration: '2m', target: 10 },   // Ramp up to 10 users
        { duration: '5m', target: 10 },   // Stay at 10 users
        { duration: '2m', target: 20 },   // Ramp up to 20 users
        { duration: '5m', target: 20 },   // Stay at 20 users
        { duration: '2m', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s
        http_req_failed: ['rate<0.05'],    // Error rate should be less than 5%
        errors: ['rate<0.05'],
    },
};

const BASE_URL = 'http://host.docker.internal:8080'; // Adjust to your app

export default function () {
    // Test different endpoints
    let responses = http.batch({
        'GET /': http.get(`${BASE_URL}/`),
        'GET /health': http.get(`${BASE_URL}/actuator/health`),
        'GET /metrics': http.get(`${BASE_URL}/actuator/prometheus`),
    });

    // Check responses
    for (let key in responses) {
        check(responses[key], {
            [`${key} status is 200`]: (r) => r.status === 200,
            [`${key} response time < 2000ms`]: (r) => r.timings.duration < 2000,
        }) || errorRate.add(1);
    }

    // Simulate user think time
    sleep(Math.random() * 3 + 1); // 1-4 seconds
}