package com.radartrade.platform.service.exchangeprocessor.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {
    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
    @Bean
    public PriceConsumer priceConsumer() {
        return new PriceConsumer(objectMapper());
    }
}
