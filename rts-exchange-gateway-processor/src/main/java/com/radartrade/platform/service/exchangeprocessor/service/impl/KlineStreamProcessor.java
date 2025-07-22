package com.radartrade.platform.service.exchangeprocessor.service.impl;

import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import com.radartrade.platform.service.exchangeprocessor.repository.KlineRepository;
import com.radartrade.platform.service.exchangeprocessor.service.client.KlineConsumer;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class KlineStreamProcessor {

    private final KlineRepository klineRepository;

    public KlineStreamProcessor(KlineRepository klineRepository) {
        this.klineRepository = klineRepository;
    }


    public Flux<KlineUpdate> constructFluxKlineUpdates(KlineConsumer klineConsumer) {
        return klineConsumer.klineUpdateStream()
                .distinct(k -> k.getSymbol() + "_" + k.getInterval() + "_" + k.getOpenTime())
                .flatMap(klineRepository::save);
    }
}
