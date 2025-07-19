package com.radartrade.platform.service.exchangeprocessor.repository;


import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PriceRepository extends JpaRepository<PriceUpdate, Long> {
}
