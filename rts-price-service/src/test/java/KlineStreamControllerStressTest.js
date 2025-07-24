import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    vus: 50,               // 50 virtual users
    duration: '30s',       // test for 30 seconds
};

export default function () {
    const url = 'http://localhost:8083/api/v1/price/kline/stream?symbol=BTCUSDT&interval=1h&limit=500';

    const params = {
        headers: {
            Accept: 'application/stream+json',
        },
        timeout: '60s',
    };

    const res = http.get(url, params);

    check(res, {
        'status is 200': (r) => r.status === 200,
        'body is not empty': (r) => r.body && r.body.length > 0,
    });

    sleep(1); // optional
}
