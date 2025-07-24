package com.radartrade.platform.service.exchangeprocessor.service.impl;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import com.radartrade.platform.service.exchangeprocessor.util.MapperUtil;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.data.redis.core.ReactiveRedisTemplate;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

@Service

public class PricePubService {
    private static final String CHANNEL = "price.updates";

    private final ReactiveRedisTemplate<String, String> redisTemplate;
    private final ObjectMapper objectMapper = MapperUtil.objectMapper();

    public PricePubService(@Qualifier("myReactiveRedisTemplate") ReactiveRedisTemplate<String, String> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public Mono<Long> publishPriceUpdate(PriceUpdate update) {
        try {
            String json = objectMapper.writeValueAsString(update);
            return redisTemplate.convertAndSend(CHANNEL, json);
        } catch (Exception e) {
            return Mono.error(e);
        }
    }
}
