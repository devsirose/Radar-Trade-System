package com.radartrade.platform.service.payment.domain;

import com.radartrade.platform.service.payment.domain.valueobject.PaymentMethodType;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "payment_methods")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PaymentMethod {

    @Id
    @GeneratedValue
    private UUID id;

    @Enumerated(EnumType.STRING)
    private PaymentMethodType type;

    private String provider;
    private String providerId;
    private String last4;
    private Integer expiryMonth;
    private Integer expiryYear;

    private Instant createdAt = Instant.now();
}
