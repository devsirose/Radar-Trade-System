package com.radartrade.platform.service.payment.repsitory;

import com.radartrade.platform.service.payment.domain.Invoice;
import com.radartrade.platform.service.payment.domain.valueobject.InvoiceStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface InvoiceRepository extends JpaRepository<Invoice, UUID> {
    List<Invoice> findBySubscriptionId(UUID subscriptionId);

    Optional<Invoice> findByInvoiceNumber(String invoiceNumber);

    List<Invoice> findByStatus(InvoiceStatus status);

    List<Invoice> findByDueDateBefore(LocalDate dueDate);
}
