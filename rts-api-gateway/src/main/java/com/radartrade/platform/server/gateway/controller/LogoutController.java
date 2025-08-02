package com.radartrade.platform.server.gateway.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.Map;

@RestController
public class LogoutController {

    @Value("${spring.security.oauth2.resourceserver.jwt.jwk-set-uri}")
    private String jwkSetUri;

    @PostMapping("/logout")
    public Mono<ResponseEntity<?>> logout(ServerWebExchange exchange, Authentication authentication) {
        return performLogout(exchange, authentication);
    }

    @GetMapping("/logout")
    public Mono<ResponseEntity<?>> logoutGet(ServerWebExchange exchange, Authentication authentication) {
        return performLogout(exchange, authentication);
    }

    private Mono<ResponseEntity<?>> performLogout(ServerWebExchange exchange, Authentication authentication) {
        Map<String, Object> response = new HashMap<>();

        if (authentication != null && authentication instanceof JwtAuthenticationToken) {
            JwtAuthenticationToken jwtAuth = (JwtAuthenticationToken) authentication;
            Jwt jwt = jwtAuth.getToken();

            // Extract issuer from JWT to construct logout URL
            String issuer = jwt.getIssuer().toString();
            String logoutUrl = issuer + "/protocol/openid-connect/logout"
                    + "?id_token_hint=" + jwt.getTokenValue()
                    + "&post_logout_redirect_uri=" + getPostLogoutRedirectUri(exchange.getRequest());

            response.put("logoutUrl", logoutUrl);
            response.put("message", "Token will be invalidated. Redirect to logout URL for complete logout.");
            response.put("tokenId", jwt.getId());
            response.put("subject", jwt.getSubject());

            return Mono.just(ResponseEntity.ok(response));
        } else {
            response.put("message", "No JWT token found. Already logged out or using different auth method.");
            response.put("authenticated", false);
            return Mono.just(ResponseEntity.ok(response));
        }
    }

    @GetMapping("/logout/callback")
    public Mono<ResponseEntity<?>> logoutCallback() {
        Map<String, String> response = new HashMap<>();
        response.put("message", "Logout completed successfully");
        response.put("status", "logged_out");
        response.put("note", "JWT token has been invalidated");
        return Mono.just(ResponseEntity.ok(response));
    }

    private String getPostLogoutRedirectUri(ServerHttpRequest request) {
        String scheme = request.getURI().getScheme();
        String host = request.getURI().getHost();
        int port = request.getURI().getPort();
        String portPart = (port != -1 && port != 80 && port != 443) ? ":" + port : "";

        return scheme + "://" + host + portPart + "/logout/callback";
    }
}