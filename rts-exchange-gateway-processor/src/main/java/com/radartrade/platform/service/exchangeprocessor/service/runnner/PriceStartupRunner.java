package com.radartrade.platform.service.exchangeprocessor.service.runnner;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.exchangeprocessor.domain.Symbol;
import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.client.SymbolConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.impl.PriceStreamService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@Slf4j
public class PriceStartupRunner implements ApplicationRunner {

    private final PriceStreamService priceStreamService;
    private final SymbolConsumer symbolConsumer;
    private final int MAX_SUBSTREAM = 1000;
    public PriceStartupRunner(
            PriceStreamService priceStreamService,
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
            priceStreamService.constructFluxPriceUpdates(priceConsumer)
                    .subscribe();
        }

    }
}
