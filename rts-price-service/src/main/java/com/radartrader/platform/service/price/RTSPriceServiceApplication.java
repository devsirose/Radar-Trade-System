package com.radartrader.platform.service.price;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = {
        "com.radartrader.platform.service.price",
        "com.radartrade.platform.service.exchangeprocessor"
})
public class RTSPriceServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(RTSPriceServiceApplication.class, args);
    }
}
