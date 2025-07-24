package com.radartrade.platform.service.exchangeprocessor.repository;


import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;

@Repository
public interface KlineReactiveRepository extends ReactiveCrudRepository<KlineUpdate, Long> {
    @Query("SELECT * FROM kline WHERE symbol = :symbol " +
            "AND interval = :interval " +
            "ORDER BY open_time DESC " +
            "LIMIT :limit")
    Flux<KlineUpdate> getListPriceUpdate(String symbol, String interval, Integer limit);

}
