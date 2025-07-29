package com.radartrader.platform.service.price.util;

public class KlineRedisKeyGenerator {

    private static final String KLINE_PREFIX = "kline";
    private static final String SEPARATOR = ":";

    public static String generateKlineKey(String symbol, String interval) {
        return KLINE_PREFIX + SEPARATOR +
                symbol.toUpperCase() + SEPARATOR +
                interval ;
    }

}