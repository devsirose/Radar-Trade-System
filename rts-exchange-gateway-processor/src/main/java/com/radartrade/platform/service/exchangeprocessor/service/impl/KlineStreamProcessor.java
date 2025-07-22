package com.radartrade.platform.service.exchangeprocessor.service.impl;

import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import com.radartrade.platform.service.exchangeprocessor.repository.KlineRepository;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class KlineStreamProcessor {

    private final KlineRepository klineRepository;

    public KlineStreamProcessor(KlineRepository klineRepository) {
        this.klineRepository = klineRepository;
    }


    public Flux<KlineUpdate> constructFluxKlineUpdates(Flux<KlineUpdate> klineUpdatesStream) {
        return klineUpdatesStream
                .distinct(k -> k.getSymbol() + "_" + k.getInterval() + "_" + k.getOpenTime())
                .flatMap(klineRepository::save);
    }
}
