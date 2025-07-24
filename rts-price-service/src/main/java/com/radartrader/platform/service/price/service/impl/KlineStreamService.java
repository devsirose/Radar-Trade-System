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
                .flatMapMany(klineUpdates -> {
                    if (klineUpdates.size() >= limit) {
                        return Flux.fromIterable(klineUpdates);
                    } else {
                        return klineConsumer.getFluxKlineUpdate(
                                symbol,
                                interval,
                                limit
                        );
                    }
                })
                .sort( (t1, t2) ->
                        t1.getCloseTime().compareTo(t2.getCloseTime())
                );
    }
}
