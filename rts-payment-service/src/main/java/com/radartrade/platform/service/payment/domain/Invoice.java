package com.radartrade.platform.service.payment.domain;

import com.radartrade.platform.service.payment.domain.valueobject.InvoiceStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "invoices")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Invoice {

    @Id
    @GeneratedValue
    private UUID id;

    @ManyToOne
    @JoinColumn(name = "subscription_id", nullable = false)
    private Subscription subscription;

    @Column(unique = true, nullable = false)
    private String invoiceNumber;

    private BigDecimal amountSubtotal;
    private BigDecimal taxAmount;
    private BigDecimal amountTotal;

    @Column(length = 3)
    private String currency;

    @Enumerated(EnumType.STRING)
    private InvoiceStatus status = InvoiceStatus.DRAFT;

    private LocalDate dueDate;
    private Instant paidAt;

    private Instant createdAt = Instant.now();
}

