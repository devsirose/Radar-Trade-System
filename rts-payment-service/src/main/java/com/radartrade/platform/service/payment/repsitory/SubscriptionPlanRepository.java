package com.radartrade.platform.service.payment.repsitory;

import com.radartrade.platform.service.payment.domain.SubscriptionPlan;
import com.radartrade.platform.service.payment.domain.valueobject.PlanStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface SubscriptionPlanRepository extends JpaRepository<SubscriptionPlan, UUID> {
    List<SubscriptionPlan> findByStatus(PlanStatus status);
}

