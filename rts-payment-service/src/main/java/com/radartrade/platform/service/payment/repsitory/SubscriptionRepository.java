package com.radartrade.platform.service.payment.repsitory;

import com.radartrade.platform.service.payment.domain.Subscription;
import com.radartrade.platform.service.payment.domain.valueobject.SubscriptionStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface SubscriptionRepository extends JpaRepository<Subscription, UUID> {
    List<Subscription> findByUserId(UUID userId);

    Optional<Subscription> findByUserIdAndStatus(UUID userId, SubscriptionStatus status);
}
