package com.radartrade.platform.service.payment;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication
@EnableDiscoveryClient
public class RTSPaymentServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(RTSPaymentServiceApplication.class, args);
    }
}
