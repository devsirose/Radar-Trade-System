package com.radartrade.platform.service.exchangeprocessor.service.runnner;

import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.impl.PriceStreamService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class PriceStartupRunner implements ApplicationRunner {
    private final PriceConsumer priceConsumer;
    private final PriceStreamService priceStreamService;

    public PriceStartupRunner(PriceConsumer priceConsumer, PriceStreamService priceStreamService) {
        this.priceConsumer = priceConsumer;
        this.priceStreamService = priceStreamService;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        priceStreamService.saveAllPriceUpdates(priceConsumer.priceUpdatesStream())
                .subscribe();

    }
}
