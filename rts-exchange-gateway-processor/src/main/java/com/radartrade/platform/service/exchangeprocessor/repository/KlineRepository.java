package com.radartrade.platform.service.exchangeprocessor.repository;

import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import org.springframework.data.jpa.repository.JpaRepository;

public interface KlineRepository extends JpaRepository<KlineUpdate, Long> {
}
