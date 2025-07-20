package com.radartrade.platform.service.exchangeprocessor.repository;


import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;

import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PriceRepository extends ReactiveCrudRepository<PriceUpdate, Long> {
}
