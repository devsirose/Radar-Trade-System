package com.radartrade.platform.service.exchangeprocessor.service.impl;


import com.radartrade.platform.service.common.util.KlineRedisKeyGenerator;
import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.data.redis.core.ReactiveRedisOperations;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

@Service
@Slf4j
public class KlinePubService {

    private final ReactiveRedisOperations<String, KlineUpdate> redisOperations;

    // Sử dụng Qualifier để inject đúng Bean sẽ được tạo ở Bước 2
    public KlinePubService(@Qualifier("klineRedisOperations") ReactiveRedisOperations<String, KlineUpdate> redisOperations) {
        this.redisOperations = redisOperations;
    }

    public Mono<Long> publishKlineUpdate(KlineUpdate update) {
        // Lấy tên channel từ rts-common
        KlineRedisKeyGenerator KlineRedisKeyGenerator = new KlineRedisKeyGenerator();
        String channel = KlineRedisKeyGenerator.generateKlineTopic(update.getSymbol(), update.getInterval());
        log.debug("Publishing kline update to channel {}: {}", channel, update);
        return redisOperations.convertAndSend(channel, update);
    }
}
