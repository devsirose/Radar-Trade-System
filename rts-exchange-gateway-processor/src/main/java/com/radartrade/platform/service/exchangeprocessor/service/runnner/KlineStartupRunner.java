package com.radartrade.platform.service.exchangeprocessor.service.runnner;

import com.radartrade.platform.service.exchangeprocessor.domain.Symbol;
import com.radartrade.platform.service.exchangeprocessor.service.client.KlineStreamConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.client.SymbolConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.impl.KlineStreamProcessor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@Slf4j
@ConditionalOnProperty(name = "my.runner.enabled", havingValue = "true")
public class KlineStartupRunner implements ApplicationRunner {

    private final SymbolConsumer symbolConsumer;
    private final int MAX_SUBSTREAM = 100;
    private final KlineStreamProcessor klineStreamProcessor;
    public KlineStartupRunner(SymbolConsumer symbolConsumer1, KlineStreamProcessor klineStreamProcessor) {
        this.symbolConsumer = symbolConsumer1;
        this.klineStreamProcessor = klineStreamProcessor;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        List<Symbol> symbols = symbolConsumer.getSymbols();

        for (int i = 0; i < symbols.size(); i += MAX_SUBSTREAM) {
            KlineStreamConsumer klineStreamConsumer = new KlineStreamConsumer(
                    symbols.subList(i, Math.min((i + MAX_SUBSTREAM), symbols.size()))
            );

            klineStreamProcessor.constructFluxKlineUpdates(klineStreamConsumer.klineUpdateStream())
                    .subscribe();
        }
    }
}
