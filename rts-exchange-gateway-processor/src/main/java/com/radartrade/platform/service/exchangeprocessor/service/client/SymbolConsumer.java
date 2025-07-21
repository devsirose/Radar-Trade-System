package com.radartrade.platform.service.exchangeprocessor.service.client;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.common.constant.ErrorCode;
import com.radartrade.platform.service.common.exception.AppException;
import com.radartrade.platform.service.exchangeprocessor.domain.Symbol;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Component
public class SymbolConsumer {
    @Value("${exchange.api.rest.base-url}")
    private String EXCHANGE_BASE_URL;
    private String EXCHANGE_INFO_URI = "/api/v3/exchangeInfo";
    private RestClient symbolConsumerClient;
    private List<Symbol> symbols;
    private final ObjectMapper objectMapper;

    public SymbolConsumer(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    private void connect() {
        symbolConsumerClient = RestClient.create(EXCHANGE_BASE_URL);
        symbols = getListSymbol(symbolConsumerClient);
    }

    private List<Symbol> getListSymbol(RestClient client) {
        String response = client
                .get()
                .uri(EXCHANGE_INFO_URI)
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(String.class);
        return parseSymbols(response);
    }

    private List<Symbol> parseSymbols(String json){
        try {
            var node = objectMapper.readTree(json);
            var symbolsNode = node.get("symbols");
            var symbolsString = symbolsNode.toString();
            List<LinkedHashMap<String, Object>> symbolsList  = objectMapper.readValue(symbolsString, List.class);
            List<Symbol> result =  symbolsList.stream()
                    .map(e ->
                            new Symbol(e.get("symbol").toString())
                    )
                    .collect(Collectors.toList());
            return result;
        } catch (JsonProcessingException ex) {
            throw new AppException(ErrorCode.RTS_JSON_CANNOT_PARSE, ex.getMessage());
        }
    }
}
