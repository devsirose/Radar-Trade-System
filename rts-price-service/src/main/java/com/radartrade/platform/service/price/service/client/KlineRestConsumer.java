package com.radartrade.platform.service.price.service.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.price.domain.KlineUpdate;
import com.radartrade.platform.service.price.util.MapperUtil;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import reactor.core.publisher.Flux;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Service
@Slf4j
public class KlineRestConsumer {

    @Value("${exchange.api.rest.base-url}")
    private String BASE_URL;

    private static final String KLINE_URI = "/api/v3/klines";

    private RestClient client;
    private final ObjectMapper objectMapper = MapperUtil.objectMapper();

    public KlineRestConsumer() {
    }

    @PostConstruct
    private void connect() {
        client = RestClient.builder()
                .baseUrl(BASE_URL)
                .build();
    }

    public Flux<KlineUpdate> getFluxKlineUpdate(String symbol, String interval, Integer limit) {
        symbol = symbol.toUpperCase();
        return Flux.fromIterable(
                getListKlineUpdates(symbol, interval, limit)
        );
    }

    private List<KlineUpdate> getListKlineUpdates(String symbol, String interval, Integer limit) {
        try {
            String response = client
                    .get()
                    .uri(uriBuilder -> uriBuilder
                            .path(KLINE_URI)
                            .queryParam("symbol", symbol)
                            .queryParam("interval", interval)
                            .queryParam("limit", limit)
                            .build()
                    )
                    .accept(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .body(String.class);

            return parseListKlineUpdate(response, symbol, interval);

        } catch (Exception e) {
            log.error("Failed to fetch Kline data from exchange: {}", e.getMessage(), e);
            return List.of(); // fallback rỗng
        }
    }

    private List<KlineUpdate> parseListKlineUpdate(String response, String symbol, String interval) {
        List<KlineUpdate> result = new ArrayList<>();

        try {
            List<List<Object>> rawList = objectMapper.readValue(response, List.class);

            for (List<Object> k : rawList) {
                KlineUpdate kline = KlineUpdate.builder()
                        .symbol(symbol)
                        .interval(interval)
                        .openTime(Instant.ofEpochMilli(((Number) k.get(0)).longValue()))
                        .open(Double.parseDouble(k.get(1).toString()))
                        .high(Double.parseDouble(k.get(2).toString()))
                        .low(Double.parseDouble(k.get(3).toString()))
                        .close(Double.parseDouble(k.get(4).toString()))
                        .volume(Double.parseDouble(k.get(5).toString()))
                        .closeTime(Instant.ofEpochMilli(((Number) k.get(6)).longValue()))
                        .tradesCount(((Number) k.get(8)).intValue())
                        .closed(true)
                        .build();

                result.add(kline);
            }

        } catch (Exception e) {
            log.error("Failed to parse Kline response: {}", e.getMessage(), e);
        }

        return result;
    }
}
