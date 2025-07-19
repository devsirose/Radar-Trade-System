package com.radartrade.platform.service.exchangeprocessor.service.impl;

import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import com.radartrade.platform.service.exchangeprocessor.repository.PriceRepository;
import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class PriceService {
    private final PriceConsumer priceService;
    private final PriceRepository priceRepository;

    public PriceService(PriceConsumer priceService, PriceRepository priceRepository) {
        this.priceService = priceService;
        this.priceRepository = priceRepository;
    }

    /**
     * fixme: use R2DBC save object to db
     * @param priceUpdates
     */
    public void savePriceUpdate(Flux<PriceUpdate> priceUpdates) {
        priceService.priceUpdatesStream()
                .subscribe();
    }
}
