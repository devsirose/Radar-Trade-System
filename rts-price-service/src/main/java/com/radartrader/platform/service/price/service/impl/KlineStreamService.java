package com.radartrader.platform.service.price.service.impl;

import com.radartrade.platform.service.common.domain.valueobject.KlineInterval;
import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import com.radartrade.platform.service.exchangeprocessor.repository.KlineReactiveRepository;
import com.radartrade.platform.service.exchangeprocessor.service.client.KlineRestConsumer;
import com.radartrader.platform.service.price.config.KlineCacheProperties;
import com.radartrader.platform.service.price.util.KlineRedisKeyGenerator;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.ReactiveListOperations;
import org.springframework.data.redis.core.ReactiveRedisOperations;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.util.Comparator;

@Service
@Slf4j
public class KlineStreamService {
    private final KlineReactiveRepository klineReactiveRepository;
    private final KlineRestConsumer klineRestConsumer;
    private final ReactiveRedisOperations<String, KlineUpdate> redisOperations;

    public KlineStreamService(KlineReactiveRepository klineReactiveRepository,
                              KlineRestConsumer klineRestConsumer,
                              ReactiveRedisOperations<String, KlineUpdate> redisOperations) {
        this.klineReactiveRepository = klineReactiveRepository;
        this.klineRestConsumer = klineRestConsumer;
        this.redisOperations = redisOperations;
    }


    public Flux<KlineUpdate> consumeAndRetrieveKlineUpdate(String symbol, String interval, Integer limit) {
        return klineRestConsumer.getFluxKlineUpdate(symbol, interval, limit);
    }

    /**
     * Consume KlineUpdate and read cache aside
     * @param symbol
     * @param interval
     * @return Flux<KlineUpdate>
     */
    public Flux<KlineUpdate> consumeAndCacheKlineUpdate(String symbol, String interval) {
        ReactiveListOperations<String, KlineUpdate> redisListOps = redisOperations.opsForList();
        String key = KlineRedisKeyGenerator.generateKlineKey(symbol, interval);

        return klineRestConsumer.getFluxKlineUpdate(symbol, interval, KlineCacheProperties.MAX_LIST_VALUE_SIZE)
                .switchIfEmpty(Flux.defer(() -> {
                    log.warn("No data from getFluxKlineUpdate for {}-{}", symbol, interval);
                    return Flux.empty();
                }))
                .doOnNext(k -> log.debug("Fetched Kline: {}", k))
                .sort(Comparator.comparing(KlineUpdate::getCloseTime))
                .collectList()
                .doOnNext(list -> log.debug("Collected list size: {}", list.size()))
                .flatMapMany(klineList -> {
                    if (klineList.isEmpty()) {
                        return Flux.empty();
                    }
                    return redisListOps.rightPushAll(key, klineList)
                            .then(redisOperations.expire(key, KlineInterval.getvalueOf(interval)))
                            .thenMany(Flux.fromIterable(klineList));
                });

    }


}
