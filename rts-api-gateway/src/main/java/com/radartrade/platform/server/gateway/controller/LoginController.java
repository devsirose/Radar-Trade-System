package com.radartrade.platform.server.gateway.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/auth/login")
public class LoginController {
    @Value("${token.exchange.provider.keycloak.login-url}")
    private String keycloakLoginUrl;
    @Value("${token.exchange.provider.keycloak.client-id}")
    private String clientId;

    @GetMapping
    public ResponseEntity<?> login(@RequestParam String state,
                                   @RequestParam("redirect_uri") String redirectUri,
                                   @RequestParam("scope")  List<String> scope)  {
        HttpHeaders headers = new HttpHeaders();
        headers.setLocation(java.net.URI.create(buildRedirectLoginUrl(state, redirectUri, scope)));
        return new ResponseEntity<>(headers, HttpStatus.SEE_OTHER);
    }

    private String buildRedirectLoginUrl(String state, String redirectUri, List<String> scope) {
        return new StringBuilder()
                .append(keycloakLoginUrl)
                .append("?").append("response_type=code")
                .append("&").append("client_id=").append(clientId)
                .append("&").append("redirect_uri=").append(redirectUri)
                .append("&").append("state=").append(state)
                .append("&").append("scope=").append(scope.stream().collect(Collectors.joining("%20")))
                .toString();
    }
}
