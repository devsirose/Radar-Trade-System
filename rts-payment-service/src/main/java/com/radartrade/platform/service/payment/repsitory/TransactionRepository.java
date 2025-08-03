package com.radartrade.platform.service.payment.repsitory;

import com.radartrade.platform.service.payment.domain.Transaction;
import com.radartrade.platform.service.payment.domain.valueobject.TransactionStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, UUID> {
    List<Transaction> findByUserId(UUID userId);

    List<Transaction> findBySubscriptionId(UUID subscriptionId);

    List<Transaction> findByStatus(TransactionStatus status);

    List<Transaction> findByProcessedAtBetween(Instant start, Instant end);
}

