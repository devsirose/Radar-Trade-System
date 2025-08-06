package com.radartrade.platform.service.payment.dto.request;

import lombok.Data;

@Data
public class SubscriptionRequest {
    private String userId;
    private String subsriptionPlanId;
}
