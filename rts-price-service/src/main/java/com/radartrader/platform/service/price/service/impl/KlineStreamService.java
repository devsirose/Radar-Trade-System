package com.radartrader.platform.service.price.service.impl;

import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import com.radartrader.platform.service.price.repository.KlineReactiveRepository;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class KlineStreamService {
    private final KlineReactiveRepository klineReactiveRepository;

    public KlineStreamService(KlineReactiveRepository klineReactiveRepository) {
        this.klineReactiveRepository = klineReactiveRepository;
    }

    public Flux<KlineUpdate> consumeKlineUpdate(String symbol, String interval, Integer limit) {
        return klineReactiveRepository.getListPriceUpdate(symbol, interval, limit);
    }
}
