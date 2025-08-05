package com.radartrade.platform.service.payment.service.impl;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PaymentService {
    @Transactional(rollbackFor = Exception.class)
    public String createPaymentUrl(String userId, String subscriptionPlanId) {
       return "";
    }
}
