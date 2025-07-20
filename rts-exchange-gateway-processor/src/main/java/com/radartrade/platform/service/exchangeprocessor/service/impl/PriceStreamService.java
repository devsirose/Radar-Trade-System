package com.radartrade.platform.service.exchangeprocessor.service.impl;

import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import com.radartrade.platform.service.exchangeprocessor.repository.PriceRepository;
import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class PriceStreamService {
    private final PriceConsumer priceService;
    private final PriceRepository priceRepository;

    public PriceStreamService(PriceConsumer priceService, PriceRepository priceRepository) {
        this.priceService = priceService;
        this.priceRepository = priceRepository;
    }

    /**
     * fixed: use R2DBC save object to db
     * @param priceUpdates
     */
    public Flux<PriceUpdate> saveAllPriceUpdates(Flux<PriceUpdate> priceUpdates) {
        return priceService.priceUpdatesStream()
                .flatMap(priceRepository::save);
    }
}
