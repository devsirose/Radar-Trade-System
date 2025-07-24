package com.radartrader.platform.service.price.controller;

import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import com.radartrader.platform.service.price.service.impl.PriceSubService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

@RestController
@RequestMapping("/api/v1/price")
public class PriceStreamController {
    private final PriceSubService priceSubService;

    public PriceStreamController(PriceSubService priceSubService) {
        this.priceSubService = priceSubService;
    }

    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<PriceUpdate> streamPriceUpdate(@RequestParam("symbol")String symbol) {
        return priceSubService.consumePriceUpdateStream()
                .filter(priceUpdate -> priceUpdate
                        .getSymbol()
                        .equalsIgnoreCase(symbol)
                );
    }
}
