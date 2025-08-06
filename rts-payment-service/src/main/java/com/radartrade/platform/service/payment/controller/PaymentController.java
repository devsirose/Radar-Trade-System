package com.radartrade.platform.service.payment.controller;

import com.radartrade.platform.service.payment.dto.request.SubscriptionRequest;
import com.radartrade.platform.service.payment.service.impl.PaymentService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/payment")
public class PaymentController {
    private final PaymentService paymentService;

    public PaymentController(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    /**
     * Receive request,process subscription then redirect with params to payment gateway
     * @param request
     * @return ResponseEntity<redirectUrl_with_params></>
     * params according to: https://sandbox.vnpayment.vn/apis/docs/thanh-toan-pay/pay.html#danh-s%C3%A1ch-tham-s%E1%BB%91
     * redirectUrl : https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
     */
     @PostMapping
     public ResponseEntity<?> createPayment(@RequestBody SubscriptionRequest request) {
         HttpHeaders headers = new HttpHeaders();
         headers.add("Location", paymentService.createPaymentUrl(request.getUserId(), request.getSubsriptionPlanId()));
         return new ResponseEntity<>(headers, HttpStatus.CREATED);
     }

    /**
     * Instant Payment Notification (IPN) callback endpoint (whether success or failure)
     * This endpoint is called by the payment gateway to notify about the payment status.
     * It should handle the notification and update the subscription status accordingly.
     * @param vnpParams according to (https://sandbox.vnpayment.vn/apis/docs/thanh-toan-pay/pay.html#danh-s%C3%A1ch-tham-s%E1%BB%91-1)
     * requirement: IPN URL must have SSL certificate (https) and domain must be registered with the payment gateway.
     * action: update subscription status in database, send notification to user, etc.
     * Note: This endpoint should be secured and validate the request to ensure it comes from the payment gateway.
     * @return
     */

    @GetMapping
    public ResponseEntity<?> callbackIPN(@RequestParam Map<String, String> vnpParams) {

        return ResponseEntity.ok().build();
    }
}
