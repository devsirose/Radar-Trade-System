package com.radartrade.platform.service.exchangeprocessor.service.impl;

import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import com.radartrade.platform.service.exchangeprocessor.repository.PriceRepository;
import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class PriceStreamService {
    private final PriceRepository priceRepository;

    public PriceStreamService(PriceRepository priceRepository) {
        this.priceRepository = priceRepository;
    }

    /**
     * fixed: use R2DBC save object to db
     * @param
     */
    public Flux<PriceUpdate> constructFluxPriceUpdates(PriceConsumer priceConsumer) {
        return priceConsumer.priceUpdatesStream()
                .flatMap(priceRepository::save);
    }
}
