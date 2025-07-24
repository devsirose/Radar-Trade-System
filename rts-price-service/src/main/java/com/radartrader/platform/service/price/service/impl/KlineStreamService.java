package com.radartrader.platform.service.price.service.impl;

import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import com.radartrade.platform.service.exchangeprocessor.repository.KlineReactiveRepository;
import com.radartrade.platform.service.exchangeprocessor.service.client.KlineConsumer;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
public class KlineStreamService {
    private final KlineReactiveRepository klineReactiveRepository;
    private final KlineConsumer klineConsumer;

    public KlineStreamService(KlineReactiveRepository klineReactiveRepository,
                              KlineConsumer klineConsumer) {
        this.klineReactiveRepository = klineReactiveRepository;
        this.klineConsumer = klineConsumer;
    }

    public Flux<KlineUpdate> consumeKlineUpdate(String symbol, String interval, Integer limit) {
        Flux<KlineUpdate> klineUpdateFlux = klineReactiveRepository.getListPriceUpdate(
                symbol,
                interval,
                limit
        );
        //fallback method
        return klineUpdateFlux.collectList()
                .flatMapMany(dbList -> {
                    if (dbList.size() >= limit) {
                        return Flux.fromIterable(dbList);
                    } else {
                        return klineConsumer.getFluxKlineUpdate(
                                symbol,
                                interval,
                                limit
                        );
                    }
                });
    }
}
