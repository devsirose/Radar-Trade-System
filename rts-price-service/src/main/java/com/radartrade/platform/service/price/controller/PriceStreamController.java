package com.radartrade.platform.service.price.controller;


import com.radartrade.platform.service.price.domain.PriceUpdate;
import com.radartrade.platform.service.price.service.impl.PriceSubService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

import java.util.concurrent.atomic.AtomicInteger;

@Slf4j
@RestController
@RequestMapping("/api/v1/price")
public class PriceStreamController {
    private final PriceSubService priceSubService;
    private final AtomicInteger connections = new AtomicInteger(0);

    public PriceStreamController(PriceSubService priceSubService) {
        this.priceSubService = priceSubService;
    }

    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<PriceUpdate> streamPriceUpdate(@RequestParam("symbol")String symbol) {
        return priceSubService.consumePriceUpdateStream()
                .filter(priceUpdate -> priceUpdate
                        .getSymbol()
                        .equalsIgnoreCase(symbol)
                )
                .doOnSubscribe(s -> {
                    int cur = connections.incrementAndGet();
                    log.info("New connection. Open = {}", cur);
                })
                .doFinally(sig -> {
                    int cur = connections.decrementAndGet();
                    log.info("Connection closed ({}). Open = {}", sig, cur);
                });
    }
}
