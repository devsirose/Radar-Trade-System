package com.radartrade.platform.server.gateway.service.client;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
@Slf4j
public class KeycloakLogoutService {
    private RestClient restClient = RestClient.create();

    @Value("${token.exchange.provider.keycloak.logout-url}")
    private String logoutEndpoint;


    public void logout(String idToken) {
        HttpStatusCode status = restClient.post()
                .uri(logoutEndpoint)
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                .body("id_token_hint=" + idToken)
                .retrieve()
                .toBodilessEntity()
                .getStatusCode();

        log.info("Logout request response with status: {}", status);
    }

}
