package com.radartrade.platform.service.exchangeprocessor.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

@Component
@Scope(value = "singleton")
public class MapperUtil {
    @Bean
    public static ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}
