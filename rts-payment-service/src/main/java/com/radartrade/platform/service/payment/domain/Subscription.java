package com.radartrade.platform.service.payment.domain;

import com.radartrade.platform.service.payment.domain.valueobject.SubscriptionStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "subscriptions")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Subscription {

    @Id
    @GeneratedValue
    private UUID id;

    @Column(name = "user_id")
    private UUID user;

    @ManyToOne
    @JoinColumn(name = "plan_id", nullable = false)
    private SubscriptionPlan plan;

    @Enumerated(EnumType.STRING)
    private SubscriptionStatus status = SubscriptionStatus.ACTIVE;

    private Instant currentPeriodStart;
    private Instant currentPeriodEnd;
    private Instant cancelledAt;

    private Instant createdAt = Instant.now();
    private Instant updatedAt = Instant.now();
}
