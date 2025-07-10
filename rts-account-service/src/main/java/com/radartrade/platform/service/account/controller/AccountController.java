package com.radartrade.platform.service.account.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/accounts")
public class AccountController {
    @GetMapping
    ResponseEntity<String> getAccounts() {
        return ResponseEntity.ok()
                .body(new String("Hello world!"));
    }
}
