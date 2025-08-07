package com.radartrade.platform.service.price.service.impl;

import com.radartrade.platform.service.common.domain.valueobject.KlineInterval;
import com.radartrade.platform.service.price.config.KlineCacheProperties;
import com.radartrade.platform.service.price.domain.KlineUpdate;
import com.radartrade.platform.service.price.service.client.KlineRestConsumer;
import com.radartrade.platform.service.price.util.KlineRedisKeyGenerator;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.ReactiveListOperations;
import org.springframework.data.redis.core.ReactiveRedisOperations;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import java.time.Duration;

@Service
@Slf4j
public class KlineStreamService {
    private final KlineRestConsumer klineRestConsumer;
    private final ReactiveRedisOperations<String, KlineUpdate> redisOperations;

    public KlineStreamService(KlineRestConsumer klineRestConsumer,
                              ReactiveRedisOperations<String, KlineUpdate> redisOperations) {
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
        String key = KlineRedisKeyGenerator.generateKlineKey(symbol, interval);

        ReactiveListOperations<String, KlineUpdate> redisListOps = redisOperations.opsForList();

        return redisListOps.size(key)
                .flatMapMany(size -> {
                    if (size != null && size > 0) {
                        log.info("Cache hit for key: {}", key);
                        return redisListOps.range(key, 0, -1);
                    }

                    log.info("Cache miss for key: {}, fetching from source...", key);
                    return cacheConsumer(symbol, interval, key);
                });
    }

    private Flux<KlineUpdate> cacheConsumer(String symbol, String interval, String key) {
        ReactiveListOperations<String, KlineUpdate> redisListOps = redisOperations.opsForList();
        Duration ttl = KlineInterval.getvalueOf(interval);
        return klineRestConsumer.getFluxKlineUpdate(symbol, interval, KlineCacheProperties.MAX_LIST_VALUE_SIZE)
                .switchIfEmpty(Flux.defer(() -> {
                    log.warn("No data from KlineRestConsumer for {}:{}", symbol, interval);
                    return Flux.empty();
                }))
//                .sort(Comparator.comparing(KlineUpdate::getCloseTime))
                .collectList()
                .flatMapMany(klineList -> {
                    if (klineList.isEmpty()) {
                        return Flux.empty();
                    }
                    return redisListOps.rightPushAll(key, klineList)
                            .then(redisOperations.expire(key, ttl))
                            .thenMany(Flux.fromIterable(klineList));
                });
    }

    // =================== PHƯƠNG THỨC MỚI ĐÃ THÊM VÀO ===================
    /**
     * Lắng nghe một channel trên Redis để nhận các cập nhật kline thời gian thực.
     * @param symbol Cặp giao dịch, ví dụ: "BTCUSDT"
     * @param interval Khung thời gian, ví dụ: "1m"
     * @return một Flux<KlineUpdate> liên tục từ Redis Pub/Sub.
     */
    public Flux<KlineUpdate> getLiveStream(String symbol, String interval) {
        // Tạo tên channel dựa trên symbol và interval, ví dụ: "kline:update:BTCUSDT:1m"
        String channelName = KlineRedisKeyGenerator.generateKlineTopic(symbol, interval);
        log.info("Subscribing to real-time kline updates on channel: {}", channelName);

        return redisOperations.listenToChannel(channelName)
                .map(message -> {
                    log.debug("Received real-time message on channel {}: {}", channelName, message.getMessage());
                    return message.getMessage(); // Lấy đối tượng KlineUpdate từ tin nhắn
                });
    }
    // =================================================================
}
