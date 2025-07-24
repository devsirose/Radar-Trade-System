import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '10s', target: 150 },  // tăng lên 150 connections
        { duration: '10s', target: 300 },  // tăng lên 500 connections
        { duration: '10s', target: 150 },
        { duration: '10s', target: 0 }
        // giảm về 0 (graceful shutdown)
    ],
};

const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT'];

export default function () {
    const symbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
    const url = `http://localhost:8083/api/v1/price/stream?symbol=${symbol}`;

    const res = http.get(url, {
        headers: {
            Accept: 'text/event-stream',
        },
        timeout: '60s', // thời gian nghe stream
    });

    check(res, {
        'status 200': (r) => r.status === 200,
        'body received': (r) => r.body && r.body.length > 0,
    });

    // Giữ kết nối 5s để mô phỏng stream đang diễn ra
    sleep(5);
}
