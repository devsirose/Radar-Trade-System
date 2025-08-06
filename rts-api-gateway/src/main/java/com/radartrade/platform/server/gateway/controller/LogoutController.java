package com.radartrade.platform.server.gateway.controller;

import com.radartrade.platform.server.gateway.service.client.KeycloakLogoutService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/auth/logout")
public class LogoutController {

    private final KeycloakLogoutService keycloakLogoutService;

    public LogoutController(KeycloakLogoutService keycloakLogoutService) {
        this.keycloakLogoutService = keycloakLogoutService;
    }

    @PostMapping(consumes = {MediaType.APPLICATION_JSON_VALUE})
    public ResponseEntity<?> logout(@RequestBody Map<String, String> body)  {
        keycloakLogoutService.logout(body.get("id_token"));

        HttpHeaders headers = new HttpHeaders();
        headers.setLocation(java.net.URI.create(body.get("redirect_uri")));
        return new ResponseEntity<>(headers, HttpStatus.SEE_OTHER);
    }
}
