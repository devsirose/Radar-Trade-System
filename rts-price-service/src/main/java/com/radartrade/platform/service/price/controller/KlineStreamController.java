package com.radartrade.platform.service.price.controller;

import com.radartrade.platform.service.price.domain.KlineUpdate;
import com.radartrade.platform.service.price.service.impl.KlineStreamService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

@RestController
@RequestMapping("/api/v1/price/kline")
public class KlineStreamController {
    private final KlineStreamService klineStreamService;

    public KlineStreamController(KlineStreamService klineStreamService) {
        this.klineStreamService = klineStreamService;
    }

    @GetMapping(value = "/stream", produces = MediaType.APPLICATION_STREAM_JSON_VALUE)
    public Flux<KlineUpdate> streamKlineUpdate(@RequestParam String symbol,
                                               @RequestParam String interval,
                                               @RequestParam(defaultValue = "500") Integer limit) {
        return klineStreamService.consumeAndRetrieveKlineUpdate(symbol, interval, limit);
    }

    @GetMapping(value = "/stream/cacheable", produces = MediaType.APPLICATION_STREAM_JSON_VALUE)
    public Flux<KlineUpdate> streamAndCacheableKlineUpdate(@RequestParam String symbol,
                                                           @RequestParam String interval,
                                                           @RequestParam(defaultValue = "500") Integer limit) {
        return klineStreamService.consumeAndCacheKlineUpdate(symbol, interval)
                .take(limit);
    }

    // =================== ENDPOINT MỚI ĐÃ THÊM VÀO ===================
    /**
     * Cung cấp một luồng dữ liệu kline thời gian thực và không bao giờ kết thúc.
     * Endpoint này sẽ được frontend gọi để nhận các cập nhật liên tục.
     * @param symbol Cặp giao dịch, ví dụ: "BTCUSDT"
     * @param interval Khung thời gian, ví dụ: "1m"
     * @return một Flux<KlineUpdate> liên tục.
     */
    @GetMapping(value = "/stream/live", produces = MediaType.APPLICATION_STREAM_JSON_VALUE)
    public Flux<KlineUpdate> streamLiveKlineUpdate(@RequestParam String symbol,
                                                   @RequestParam String interval) {

        return klineStreamService.getLiveStream(symbol, interval);
    }
    // =================================================================
}
