package com.radartrader.platform.service.price.controller;

import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import com.radartrader.platform.service.price.service.impl.KlineStreamService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

import java.util.Locale;

@RestController
@RequestMapping("/api/v1/kline")
public class KlineStreamController {
    private final KlineStreamService klineStreamService;

    public KlineStreamController(KlineStreamService klineStreamService) {
        this.klineStreamService = klineStreamService;
    }

    @GetMapping(value = "/stream", produces = MediaType.APPLICATION_STREAM_JSON_VALUE)
    public Flux<KlineUpdate> getKline(@RequestParam String symbol,
                                      @RequestParam String interval,
                                      @RequestParam(defaultValue = "500") Integer limit) {
        return klineStreamService.consumeKlineUpdate(symbol.toUpperCase(Locale.ROOT),
                                                     interval,
                                                     limit);
    }
}

