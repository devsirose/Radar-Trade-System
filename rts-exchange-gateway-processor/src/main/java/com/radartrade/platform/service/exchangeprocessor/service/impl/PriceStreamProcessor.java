package com.radartrade.platform.service.exchangeprocessor.service.impl;

import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import com.radartrade.platform.service.exchangeprocessor.repository.PriceReactiveRepository;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class PriceStreamProcessor {
    private final PriceReactiveRepository priceReactiveRepository;

    public PriceStreamProcessor(PriceReactiveRepository priceReactiveRepository) {
        this.priceReactiveRepository = priceReactiveRepository;
    }

    /**
     * fixed: use R2DBC save object to db
     * @param
     */
    public Flux<PriceUpdate> consumeAndSavePriceUpdates(Flux<PriceUpdate> priceUpdateFlux) {
        return priceUpdateFlux
                .flatMap(priceReactiveRepository::save);
    }
}
