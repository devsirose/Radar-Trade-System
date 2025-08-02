package com.radartrade.platform.server.gateway.controller;

import com.radartrade.platform.server.gateway.dto.response.ResponseToken;
import com.radartrade.platform.server.gateway.service.ExchangeTokenService;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("auth")
public class AuthController {
    private final ExchangeTokenService exchangeTokenService;

    public AuthController(@Qualifier("KeycloakExchangeTokenService") ExchangeTokenService exchangeTokenService) {
        this.exchangeTokenService = exchangeTokenService;
    }

    @RequestMapping("/refresh_token")
    public ResponseEntity<ResponseToken> refreshToken(@RequestParam String refreshToken) {
        return ResponseEntity.ok(exchangeTokenService.refreshToken(refreshToken));
    }
}
