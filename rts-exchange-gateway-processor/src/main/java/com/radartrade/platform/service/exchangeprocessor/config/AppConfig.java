package com.radartrade.platform.service.exchangeprocessor.config;

import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {
    @Bean
    public PriceConsumer priceConsumer() {
        return new PriceConsumer();
    }
}
