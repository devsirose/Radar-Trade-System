import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '1m', target: 50 },   // Fast ramp up
        { duration: '2m', target: 50 },   // Stay at 50 users
        { duration: '1m', target: 100 },  // Spike to 100 users
        { duration: '2m', target: 100 },  // Stay at 100 users
        { duration: '1m', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<5000'], // Allow higher response times
        http_req_failed: ['rate<0.10'],    // Allow 10% error rate
    },
};

const BASE_URL = 'http://host.docker.internal:8080';

export default function () {
    // Mix of endpoints with different load patterns
    const endpoints = [
        '/',
        '/api/users',
        '/api/users/1',
        '/api/users/999', // This might cause 404s
        '/load',          // CPU intensive endpoint if available
    ];

    const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];

    let response = http.get(`${BASE_URL}${endpoint}`);

    check(response, {
        'status is 200 or 404': (r) => [200, 404].includes(r.status),
        'response time < 5000ms': (r) => r.timings.duration < 5000,
    });

    sleep(0.5); // Aggressive load
}