package com.radartrade.platform.server.gateway.controller;

import com.radartrade.platform.server.gateway.dto.response.ResponseToken;
import com.radartrade.platform.server.gateway.service.ExchangeTokenService;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CallbackController {

    private final ExchangeTokenService exchangeTokenService;

    public CallbackController(@Qualifier("KeycloakExchangeTokenService") ExchangeTokenService exchangeTokenService) {
        this.exchangeTokenService = exchangeTokenService;
    }

    /**
     * @fixme: check state == state stored in session follow oauth2 flow aspect of security
     * @param code
     * @param state
     * @return
     */
    @GetMapping("/callback")
    public ResponseEntity<ResponseToken> callback(@RequestParam String code, @RequestParam String state) {
        return ResponseEntity.ok(
                exchangeTokenService.exchangeToken(code)
        );
    }
}

