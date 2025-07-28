package com.radartrade.platform.service.common.domain.valueobject;

import lombok.Getter;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * Enum representing supported Kline (candlestick) intervals.
 */
@Getter
public enum KlineInterval {
    ONE_MINUTE("1m", Duration.ofMinutes(1)),
    ONE_HOUR("1h", Duration.ofHours(1)),
    ONE_DAY("1d", Duration.ofDays(1)),
    ONE_WEEK("1w", Duration.ofDays(7)),
    ONE_MONTH("1M", Duration.ofDays(30));

    private final String code;
    private final Duration duration;


    KlineInterval(String code, Duration duration) {
        this.code = code;
        this.duration = duration;
    }

    @Override
    public String toString() {
        return code;
    }

    public static List<KlineInterval> allIntervals() {
        List<KlineInterval> intervals = new ArrayList<>();
        for (KlineInterval interval : KlineInterval.values()) {
            intervals.add(interval);
        }
        return intervals;
    }
}
