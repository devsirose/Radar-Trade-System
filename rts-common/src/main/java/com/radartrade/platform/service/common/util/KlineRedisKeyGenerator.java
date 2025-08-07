package com.radartrade.platform.service.common.util;

/**
 * Lớp tiện ích để tạo các key và topic liên quan đến kline trên Redis.
 * Được đặt trong module common để tất cả các service có thể sử dụng.
 */
public class KlineRedisKeyGenerator {

    private static final String KLINE_PREFIX = "kline";
    private static final String TOPIC_PREFIX = "kline:topic";
    private static final String SEPARATOR = ":";

    /**
     * Tạo key cho việc lưu trữ cache trong Redis.
     * Ví dụ: "kline:BTCUSDT:1m"
     */
    public static String generateKlineKey(String symbol, String interval) {
        return KLINE_PREFIX + SEPARATOR +
                symbol.toUpperCase() + SEPARATOR +
                interval;
    }

    /**
     * Tạo tên channel cho Redis Pub/Sub để stream real-time.
     * Ví dụ: "kline:topic:BTCUSDT:1m"
     */
    public static String generateKlineTopic(String symbol, String interval) {
        return TOPIC_PREFIX + SEPARATOR +
                symbol.toUpperCase() + SEPARATOR +
                interval;
    }
}
