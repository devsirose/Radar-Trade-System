package com.radartrade.platform.service.exchangeprocessor.service.runnner;

import com.radartrade.platform.service.exchangeprocessor.domain.KlineInterval;
import com.radartrade.platform.service.exchangeprocessor.domain.Symbol;
import com.radartrade.platform.service.exchangeprocessor.repository.KlineReactiveRepository;
import com.radartrade.platform.service.exchangeprocessor.service.client.KlineConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.client.SymbolConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.impl.KlineStreamProcessor;
import jakarta.annotation.PostConstruct;
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
    private final KlineConsumer klineConsumer;
    private final int MAX_KLINE_LIMIT = 1000;
    private final KlineReactiveRepository klineReactiveRepository;

    public KlineStartupRunner(SymbolConsumer symbolConsumer1, KlineStreamProcessor klineStreamProcessor, KlineConsumer klineConsumer, KlineReactiveRepository klineReactiveRepository) {
        this.symbolConsumer = symbolConsumer1;
        this.klineStreamProcessor = klineStreamProcessor;
        this.klineConsumer = klineConsumer;
        this.klineReactiveRepository = klineReactiveRepository;
    }

    @PostConstruct
    public void persistKlineUpdatesToDb() {
        List<Symbol> symbols = symbolConsumer.getSymbols();
        List<KlineInterval> intervals = KlineInterval.allIntervals();

        for (Symbol symbol : symbols) {
            for (KlineInterval interval : intervals) {
                klineConsumer.getFluxKlineUpdate(
                                symbol.getName(),
                                interval.getCode(),
                                MAX_KLINE_LIMIT
                        )
                        .filterWhen(klineUpdate ->
                                klineReactiveRepository
                                        .existsKlineUpdatesBySymbolAndIntervalAndOpenTime(
                                                klineUpdate.getSymbol(),
                                                klineUpdate.getInterval(),
                                                klineUpdate.getOpenTime()
                                        )
                                        .map(numberOfRow ->
                                                numberOfRow > 0 ? false : true)
                        )
                        .flatMap(klineReactiveRepository::save)
                        .subscribe();
            }
        }
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        //do nothing
    }
}
