package com.radartrade.platform.service.payment.repsitory;

import com.radartrade.platform.service.payment.domain.PaymentMethod;
import com.radartrade.platform.service.payment.domain.valueobject.PaymentMethodType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface PaymentMethodRepository extends JpaRepository<PaymentMethod, UUID> {
    List<PaymentMethod> findByUserId(UUID userId);

    Optional<PaymentMethod> findByUserIdAndType(UUID userId, PaymentMethodType type);
}

