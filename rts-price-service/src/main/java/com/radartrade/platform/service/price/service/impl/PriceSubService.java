package com.radartrade.platform.service.price.service.impl;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.price.util.MapperUtil;
import com.radartrade.platform.service.price.domain.PriceUpdate;
import org.springframework.data.redis.connection.ReactiveSubscription;
import org.springframework.data.redis.listener.ChannelTopic;
import org.springframework.data.redis.listener.ReactiveRedisMessageListenerContainer;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Service
public class PriceSubService {
    private static final String CHANNEL = "price.updates";

    private final ReactiveRedisMessageListenerContainer container;
    private final ObjectMapper objectMapper =  MapperUtil.objectMapper();

    public PriceSubService(ReactiveRedisMessageListenerContainer container) {
        this.container = container;
    }


    public Flux<PriceUpdate> consumePriceUpdateStream() {
        return container.receive(ChannelTopic.of(CHANNEL))
                .map(ReactiveSubscription.Message::getMessage)
                .flatMap(this::deserialize);
    }

    private Mono<PriceUpdate> deserialize(String json) {
        try {
            PriceUpdate update = objectMapper.readValue(json, PriceUpdate.class);
            return Mono.just(update);
        } catch (Exception e) {
            return Mono.error(e);
        }
    }
}
