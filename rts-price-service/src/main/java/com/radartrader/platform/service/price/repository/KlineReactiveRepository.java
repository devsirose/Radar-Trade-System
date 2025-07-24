package com.radartrader.platform.service.price.repository;

import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;

@Repository
public interface KlineReactiveRepository extends ReactiveCrudRepository<KlineUpdate, String> {
    @Query("SELECT * FROM kline WHERE symbol = :symbol " +
            "AND interval = :interval " +
            "ORDER BY open_time DESC " +
            "LIMIT :limit")
    Flux<KlineUpdate> getListPriceUpdate(String symbol, String interval, Integer limit);

}
