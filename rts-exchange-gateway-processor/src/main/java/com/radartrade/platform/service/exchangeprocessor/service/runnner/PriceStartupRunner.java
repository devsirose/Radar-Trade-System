package com.radartrade.platform.service.exchangeprocessor.service.runnner;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.exchangeprocessor.domain.Symbol;
import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.client.SymbolConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.impl.PriceStreamProcessor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@Slf4j
@ConditionalOnProperty(name = "my.runner.enabled", havingValue = "true")
public class PriceStartupRunner implements ApplicationRunner {

    private final PriceStreamProcessor priceStreamService;
    private final SymbolConsumer symbolConsumer;
    private final int MAX_SUBSTREAM = 100;
    public PriceStartupRunner(
            PriceStreamProcessor priceStreamService,
            SymbolConsumer symbolConsumer, ObjectMapper objectMapper) {
        this.priceStreamService = priceStreamService;
        this.symbolConsumer = symbolConsumer;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        List<Symbol> symbols = symbolConsumer.getSymbols();

        for (int i = 0; i < symbols.size(); i += MAX_SUBSTREAM) {
            PriceConsumer priceConsumer = new PriceConsumer(
                    symbols.subList(i, Math.min((i + MAX_SUBSTREAM), symbols.size()))
            );
            priceStreamService.consumeAndSavePriceUpdates(priceConsumer.priceUpdatesStream())
                    .subscribe();
        }

    }
}
