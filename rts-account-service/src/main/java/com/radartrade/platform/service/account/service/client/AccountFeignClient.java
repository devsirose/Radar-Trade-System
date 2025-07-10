package com.radartrade.platform.service.account.service.client;

import com.radartrade.platform.service.common.dto.response.BaseResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient("${spring.application.name}")
public class AccountFeignClient {
    @GetMapping(value = "/api/v1/account", consumes = {MediaType.APPLICATION_JSON_VALUE})
    ResponseEntity<BaseResponse> getResponse(@RequestParam Long accountId) {
        return null;
    }
}
