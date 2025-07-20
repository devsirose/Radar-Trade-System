package com.radartrade.platform.service.exchangeprocessor;

import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.impl.PriceStreamService;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class RTSExchangeProcessorApplication {
    public static void main(String[] args) {
        var context = SpringApplication.run(RTSExchangeProcessorApplication.class, args);
        PriceStreamService client = context.getBean(PriceStreamService.class);
        PriceConsumer consumer = context.getBean(PriceConsumer.class);
        client.saveAllPriceUpdates(consumer.priceUpdatesStream())
                .subscribe();

    }
}
