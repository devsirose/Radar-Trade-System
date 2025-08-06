package com.radartrade.platform.server.gateway.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping
public class ContextController {
    @GetMapping("/context")
    public ResponseEntity<Jwt> context(@AuthenticationPrincipal Jwt jwt) {
        return  ResponseEntity.ok(jwt);
    }
}
