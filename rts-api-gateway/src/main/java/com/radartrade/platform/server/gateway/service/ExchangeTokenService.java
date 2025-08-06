package com.radartrade.platform.server.gateway.service;

import com.radartrade.platform.server.gateway.dto.response.ResponseToken;
import org.springframework.stereotype.Service;

@Service
public interface ExchangeTokenService {
    ResponseToken exchangeToken(String code);
    ResponseToken refreshToken(String refreshToken);
}
