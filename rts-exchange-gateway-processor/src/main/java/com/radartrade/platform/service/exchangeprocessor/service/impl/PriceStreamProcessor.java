package com.radartrade.platform.service.exchangeprocessor.service.impl;

import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import com.radartrade.platform.service.exchangeprocessor.repository.PriceRepository;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class PriceStreamProcessor {
    private final PriceRepository priceRepository;

    public PriceStreamProcessor(PriceRepository priceRepository) {
        this.priceRepository = priceRepository;
    }

    /**
     * fixed: use R2DBC save object to db
     * @param
     */
    public Flux<PriceUpdate> consumeAndSavePriceUpdates(Flux<PriceUpdate> priceUpdateFlux) {
        return priceUpdateFlux
                .flatMap(priceRepository::save);
    }
}
