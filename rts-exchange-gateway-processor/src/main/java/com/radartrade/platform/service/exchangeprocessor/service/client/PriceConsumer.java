package com.radartrade.platform.service.exchangeprocessor.service.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import com.radartrade.platform.service.common.domain.valueobject.Symbol;
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
import java.util.stream.Collectors;

@Slf4j
public class PriceConsumer {
    private String WS_URI = "wss://stream.binance.com:9443/stream?streams=";
    private static final String POST_FIX = "@trade";
    private List<Symbol> symbols;

    private ObjectMapper objectMapper = MapperUtil.objectMapper();
    private final Sinks.Many<PriceUpdate> sink = Sinks.many().multicast().onBackpressureBuffer();

    public PriceConsumer(List<Symbol> symbols) {
        this.symbols = symbols;
        connect();
    }

    public Flux<PriceUpdate> priceUpdatesStream() {
        return sink.asFlux();
    }

    @PostConstruct
    private void connect() {
        ReactorNettyWebSocketClient client = new ReactorNettyWebSocketClient();
        client.execute(
                URI.create(WS_URI + joinPriceStream()),
                session -> session.receive()
                        .map(WebSocketMessage::getPayloadAsText)
                        .map(this::parsePriceUpdate)
                        .doOnNext(update -> {
                            if (update != null) {
                                sink.tryEmitNext(update);
                            }
                        })
                        .doOnError(err -> log.error("WebSocket error: {}", err.getMessage()))
                        .then()
        ).subscribe();
    }

    private String joinPriceStream() {
        return symbols.stream()
                .map( symbol -> symbol.getName() + POST_FIX)
                .collect(Collectors.joining("/"));
    }

    private PriceUpdate parsePriceUpdate(String json) {
        try {
            var node = objectMapper.readTree(json);
            var dataNode = node.get("data");
            PriceUpdate update = new PriceUpdate();
            update.setSymbol(dataNode.get("s").asText());
            update.setPrice(dataNode.get("p").asDouble());
            update.setEventTime(Instant.ofEpochMilli(dataNode.get("E").asLong()));
            return update;
        } catch (Exception e) {
            log.error("Failed to parse message: {}", json, e);
            return null;
        }
    }
}
