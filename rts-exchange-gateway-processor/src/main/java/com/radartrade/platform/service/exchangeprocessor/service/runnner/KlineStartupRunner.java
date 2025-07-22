package com.radartrade.platform.service.exchangeprocessor.service.runnner;

import com.radartrade.platform.service.exchangeprocessor.domain.Symbol;
import com.radartrade.platform.service.exchangeprocessor.service.client.KlineConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.client.SymbolConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.impl.KlinePublisherStreamService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@Slf4j
public class KlineStartupRunner implements ApplicationRunner {

    private final SymbolConsumer symbolConsumer;
    private final int MAX_SUBSTREAM = 100;
    private final KlinePublisherStreamService klinePublisherStreamService;
    public KlineStartupRunner(SymbolConsumer symbolConsumer1, KlinePublisherStreamService klinePublisherStreamService) {
        this.symbolConsumer = symbolConsumer1;
        this.klinePublisherStreamService = klinePublisherStreamService;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        List<Symbol> symbols = symbolConsumer.getSymbols();

        for (int i = 0; i < symbols.size(); i += MAX_SUBSTREAM) {
            KlineConsumer klineConsumer = new KlineConsumer(
                    symbols.subList(i, Math.min((i + MAX_SUBSTREAM), symbols.size()))
            );

            klinePublisherStreamService.constructFluxKlineUpdates(klineConsumer)
                    .subscribe();
        }
    }
}
