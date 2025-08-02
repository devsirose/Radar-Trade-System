package com.radartrade.platform.server.gateway.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Map;

@RestController
@RequestMapping("/")
public class OAuth2Controller {

    private final WebClient webClient;

    @Value("${oauth2.client.id}")
    private String clientId;

    @Value("${oauth2.client.secret}")
    private String clientSecret;

    @Value("${oauth2.redirect.uri}")
    private String redirectUri;

    @Value("${oauth2.token.uri}")
    private String tokenUri;

    public OAuth2Controller(WebClient webClient) {
        this.webClient = webClient;
    }

    @GetMapping("/callback")
    public ResponseEntity<?> handleCallback(@RequestParam String code) {
        try {
            // Exchange code for token
            MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
            formData.add("grant_type", "authorization_code");
            formData.add("code", code);
            formData.add("redirect_uri", redirectUri);
            formData.add("client_id", clientId);
            formData.add("client_secret", clientSecret);

            // Sử dụng Map thay vì TokenResponse từ nimbus
            Map<String, Object> tokenResponse = webClient.post()
                    .uri(tokenUri)
                    .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                    .body(BodyInserters.fromFormData(formData))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();

            // Xử lý token response
            if (tokenResponse != null && tokenResponse.containsKey("access_token")) {
                // Lưu token vào session/database
                // Redirect user to dashboard
                return ResponseEntity.ok()
                        .body(Map.of(
                                "status", "success",
                                "message", "Authentication successful",
                                "access_token", tokenResponse.get("access_token")
                        ));
            } else {
                return ResponseEntity.badRequest()
                        .body(Map.of("error", "Failed to get access token"));
            }

        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(Map.of("error", "OAuth2 exchange failed: " + e.getMessage()));
        }
    }

    @GetMapping("/login")
    public ResponseEntity<?> initiateLogin() {
        String authUrl = "https://accounts.google.com/o/oauth2/auth" +
                "?client_id=" + clientId +
                "&redirect_uri=" + redirectUri +
                "&scope=openid profile email" +
                "&response_type=code" +
                "&state=random_state_value";

        return ResponseEntity.ok(Map.of("auth_url", authUrl));
    }
}