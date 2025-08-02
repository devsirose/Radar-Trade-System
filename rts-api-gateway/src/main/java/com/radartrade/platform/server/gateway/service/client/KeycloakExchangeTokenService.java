package com.radartrade.platform.server.gateway.service.client;

import com.radartrade.platform.server.gateway.dto.response.ResponseToken;
import com.radartrade.platform.server.gateway.service.ExchangeTokenService;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;

import java.util.Map;

@Service("KeycloakExchangeTokenService")
public class KeycloakExchangeTokenService implements ExchangeTokenService {

    private RestClient restClient = RestClient.create();

    @Value("${token.exchange.provider.keycloak.endpoint}")
    private String tokenEndpoint;
    @Value("${token.exchange.provider.keycloak.client-secret}")
    private String CLIENT_SECRET;
    @Value("${token.exchange.provider.keycloak.client-id}")
    private String CLIENT_ID;

    @PostConstruct
    public void onConnect() {
        restClient = RestClient.create(tokenEndpoint);
    }

    public ResponseToken exchangeToken(String code) {
        MultiValueMap<String, String> body = buildBaseRequestBody();
        body.add("code", code);

        Map<String, String> tokenResponse = restClient
                .post()
                .uri(tokenEndpoint)
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body(body)
                .retrieve()
                .body(Map.class);

        return buildReponseToken(tokenResponse);

    }

    @Override
    public ResponseToken refreshToken(String refreshToken) {
        MultiValueMap<String, String> body = buildBaseRequestBody();
        body.add("refresh_token", refreshToken);

        Map<String, String> tokenResponse = restClient
                .post()
                .uri(tokenEndpoint)
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body(body)
                .retrieve()
                .body(Map.class);

        return buildReponseToken(tokenResponse);
    }

    private ResponseToken buildReponseToken(Map<String, String> tokenResponse) {
        return ResponseToken.builder()
                .token(tokenResponse.get("access_token"))
                .refreshToken(tokenResponse.get("refresh_token"))
                .idToken(tokenResponse.get("id_token"))
                .build();
    }

    private MultiValueMap<String, String> buildBaseRequestBody() {
        MultiValueMap<String, String> formData = new LinkedMultiValueMap<>();
        formData.add("grant_type", "authorization_code");
        formData.add("client_id", CLIENT_ID);
        formData.add("client_secret", CLIENT_SECRET);
        formData.add("redirect_uri", "http://localhost:8080/callback");
        
        return formData;
    }
}
