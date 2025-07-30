package com.radartrade.platform.service.price.service.runner;

import com.radartrade.platform.service.price.service.impl.PriceSubService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@ConditionalOnProperty(name = "my.runner.enabled", havingValue = "true")
public class PriceSubStartupRunner implements ApplicationRunner {
    private final PriceSubService priceSubService;

    public PriceSubStartupRunner(PriceSubService priceSubService) {
        this.priceSubService = priceSubService;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        priceSubService.consumePriceUpdateStream()
                .subscribe(
//                        priceUpdate -> {
//                            log.info(
//                                    "price updated: {}", priceUpdate
//                            );
//                        }
                );
    }
}
