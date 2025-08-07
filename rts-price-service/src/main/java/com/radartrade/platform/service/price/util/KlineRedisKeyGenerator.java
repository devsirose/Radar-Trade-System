package com.radartrade.platform.service.price.util;

public class KlineRedisKeyGenerator {

    private static final String KLINE_PREFIX = "kline";
    private static final String SEPARATOR = ":";
    private static final String TOPIC_PREFIX = "kline:topic";

    public static String generateKlineKey(String symbol, String interval) {
        return KLINE_PREFIX + SEPARATOR +
                symbol.toUpperCase() + SEPARATOR +
                interval ;
    }
    public static String generateKlineTopic(String symbol, String interval) {
        return TOPIC_PREFIX + SEPARATOR +
                symbol.toUpperCase() + SEPARATOR +
                interval;
    }

}