package com.radartrade.platform.service.exchangeprocessor.service.runnner;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.exchangeprocessor.domain.Symbol;
import com.radartrade.platform.service.exchangeprocessor.service.client.PriceConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.client.SymbolConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.impl.PriceStreamService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@Slf4j
public class PriceStartupRunner implements ApplicationRunner {

    private final PriceStreamService priceStreamService;
    private final SymbolConsumer symbolConsumer;
    private final ObjectMapper objectMapper;
    public PriceStartupRunner(
            ObjectProvider<PriceConsumer> consumerFactory,
            PriceStreamService priceStreamService,
            SymbolConsumer symbolConsumer, ObjectMapper objectMapper) {
        this.priceStreamService = priceStreamService;
        this.symbolConsumer = symbolConsumer;
        this.objectMapper = objectMapper;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        List<Symbol> symbols = symbolConsumer.getSymbols();
        symbols.forEach(symbol -> {
            PriceConsumer priceConsumer = new PriceConsumer(symbol.getName());
            priceStreamService.constructFluxPriceUpdates(priceConsumer)
                    .subscribe();
        });
    }
}
