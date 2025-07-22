package com.radartrade.platform.service.exchangeprocessor.service.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.exchangeprocessor.domain.KlineInterval;
import com.radartrade.platform.service.exchangeprocessor.domain.KlineUpdate;
import com.radartrade.platform.service.exchangeprocessor.domain.Symbol;
import com.radartrade.platform.service.exchangeprocessor.util.MapperUtil;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.reactive.socket.WebSocketMessage;
import org.springframework.web.reactive.socket.client.ReactorNettyWebSocketClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Sinks;

import java.net.URI;
import java.time.Instant;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

@Slf4j
public class KlineConsumer {
    private String WS_URI = "wss://stream.binance.com:9443/stream?streams=";
    private static final String POST_FIX = "@kline";
    private List<Symbol> symbols;

    private ObjectMapper objectMapper = MapperUtil.objectMapper();
    private final Sinks.Many<KlineUpdate> sink = Sinks.many().multicast().onBackpressureBuffer();

    public KlineConsumer(List<Symbol> symbols) {
        this.symbols = symbols;
        connect();
    }

    public Flux<KlineUpdate> klineUpdateStream() {
        return sink.asFlux();
    }

    @PostConstruct
    private void connect() {
        ReactorNettyWebSocketClient client = new ReactorNettyWebSocketClient();
        client.execute(
                URI.create(WS_URI + joinKlineStreams()),
                session -> session.receive()
                        .map(WebSocketMessage::getPayloadAsText)
                        .map(this::parseKlineUpdate)
                        .doOnNext(update -> {
                            if (update != null) {
                                sink.tryEmitNext(update);
                            }
                        })
                        .doOnError(err -> log.error("WebSocket error: {}", err.getMessage()))
                        .then()
        ).subscribe();
    }

    private String joinKlineStreams() {
        return symbols.stream()
                .flatMap(symbol ->
                       KlineInterval.allIntervals().stream()
                               .map(interval ->
                                       symbol.getName().toLowerCase(Locale.ROOT) + POST_FIX + "_" + interval.getCode()
                               )
                ).collect(Collectors.joining("/"));
    }

    private  KlineUpdate parseKlineUpdate(String json) {
        try {
            JsonNode root = objectMapper.readTree(json);
            JsonNode data = root.get("data");
            JsonNode k    = data.get("k");

            return KlineUpdate.builder()
                    .symbol(data.get("s").asText())
                    .interval(k.get("i").asText())
                    .openTime(Instant.ofEpochMilli(k.get("t").asLong()))
                    .closeTime(Instant.ofEpochMilli(k.get("T").asLong()))
                    .open(k.get("o").asDouble())
                    .high(k.get("h").asDouble())
                    .low(k.get("l").asDouble())
                    .close(k.get("c").asDouble())
                    .volume(k.get("v").asDouble())
                    .tradesCount(k.get("n").asInt())
                    .closed(k.get("x").asBoolean())
                    .build();

        } catch (Exception e) {
            log.error("Failed to parse Kline update: {}", json, e);
            return null;
        }
    }
}
