package com.radartrade.platform.service.exchangeprocessor.service.runnner;

import com.radartrade.platform.service.common.domain.valueobject.Symbol;
import com.radartrade.platform.service.exchangeprocessor.repository.KlineReactiveRepository;
import com.radartrade.platform.service.exchangeprocessor.service.client.KlineStreamConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.client.SymbolConsumer;
import com.radartrade.platform.service.exchangeprocessor.service.impl.KlinePubService;
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
    private final int MAX_KLINE_LIMIT = 1000;
    private final KlineReactiveRepository klineReactiveRepository;
    private final KlinePubService klinePubService;
    public KlineStartupRunner(SymbolConsumer symbolConsumer,
                              KlineReactiveRepository klineReactiveRepository,
                              KlinePubService klinePubService) {
        this.symbolConsumer = symbolConsumer;
        this.klineReactiveRepository = klineReactiveRepository;
        this.klinePubService = klinePubService;
    }
    @PostConstruct
    public void streamKlineUpdatesToDb() {
        List<Symbol> symbols = symbolConsumer.getSymbols();
        KlineStreamConsumer klineStreamConsumer =  new KlineStreamConsumer(symbols);
        klineStreamConsumer.klineUpdateStream()
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
                .flatMap(klinePubService::publishKlineUpdate)
                .subscribe();
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        //do nothing
    }
}
