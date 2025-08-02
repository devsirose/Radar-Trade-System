package com.radartrade.platform.server.gateway.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping
public class ContextController {
    @GetMapping("/context")
    public ResponseEntity<?> context() {
        return  ResponseEntity.ok().build();
    }
}
