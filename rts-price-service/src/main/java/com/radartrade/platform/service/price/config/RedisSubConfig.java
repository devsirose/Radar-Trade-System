package com.radartrade.platform.service.price.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.radartrade.platform.service.price.domain.KlineUpdate;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.ReactiveRedisConnectionFactory;
import org.springframework.data.redis.core.ReactiveRedisOperations;
import org.springframework.data.redis.core.ReactiveRedisTemplate;
import org.springframework.data.redis.listener.ReactiveRedisMessageListenerContainer;
import org.springframework.data.redis.serializer.Jackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializationContext;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
public class RedisSubConfig {
    @Bean
    public ReactiveRedisMessageListenerContainer redisMessageListenerContainer(ReactiveRedisConnectionFactory factory) {
        return new ReactiveRedisMessageListenerContainer(factory);
    }
    @Bean
    public ReactiveRedisOperations<String, KlineUpdate>  reactiveRedisOperations(ReactiveRedisConnectionFactory factory) {
        return new ReactiveRedisTemplate<>(factory, redisSerializationContext());
    }

    private RedisSerializationContext<String, KlineUpdate> redisSerializationContext() {
        StringRedisSerializer keySerializer = new StringRedisSerializer();

        // Tạo ObjectMapper hỗ trợ Instant
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());
        objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

        // Sử dụng constructor mới không deprecated
        Jackson2JsonRedisSerializer<KlineUpdate> valueSerializer =
                new Jackson2JsonRedisSerializer<>(objectMapper, KlineUpdate.class);

        RedisSerializationContext.RedisSerializationContextBuilder<String, KlineUpdate> builder =
                RedisSerializationContext.newSerializationContext(keySerializer);

        return builder.value(valueSerializer).build();
    }


}
