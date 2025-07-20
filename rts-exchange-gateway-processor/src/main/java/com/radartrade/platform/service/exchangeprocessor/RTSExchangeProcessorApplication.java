package com.radartrade.platform.service.exchangeprocessor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class RTSExchangeProcessorApplication {
    public static void main(String[] args) {
        var context = SpringApplication.run(RTSExchangeProcessorApplication.class, args);
    }
}
