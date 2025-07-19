package com.radartrade.platform.service.exchangeprocessor;

import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class RTSExchangeProcessorApplication {
    public static void main(String[] args) {
        SpringApplication.run(RTSExchangeProcessorApplication.class, args);
//        PriceConsumer client = new PriceConsumer();
//
//        client.priceUpdatesStream()
//                .subscribe(update -> System.out.printf("Symbol: %s, Price: %s, Time: %d%n",
//                        update.getSymbol(), update.getPrice(), update.getEventTime()));

    }
}
