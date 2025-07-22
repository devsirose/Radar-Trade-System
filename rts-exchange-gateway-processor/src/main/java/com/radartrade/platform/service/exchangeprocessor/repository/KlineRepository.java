package com.radartrade.platform.service.exchangeprocessor.repository;


import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface KlineRepository extends ReactiveCrudRepository<KlineUpdate, Long> {
}
