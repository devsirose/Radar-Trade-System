package com.radartrade.platform.service.exchangeprocessor.service.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.socket.WebSocketMessage;
import org.springframework.web.reactive.socket.client.ReactorNettyWebSocketClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Sinks;

import java.net.URI;
import java.time.Instant;

@Component
@Slf4j
public class PriceConsumer {
    @Value("${exchange.api.ws.base-url}")
    private String WS_URI ;
    private final ObjectMapper objectMapper;
    private final Sinks.Many<PriceUpdate> sink = Sinks.many().multicast().onBackpressureBuffer();

    public PriceConsumer(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public Flux<PriceUpdate> priceUpdatesStream() {
        return sink.asFlux();
    }

    @PostConstruct
    private void connect() {
        ReactorNettyWebSocketClient client = new ReactorNettyWebSocketClient();
        client.execute(
                URI.create(WS_URI),
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

    private PriceUpdate parsePriceUpdate(String json) {
        try {
            var node = objectMapper.readTree(json);
            PriceUpdate update = new PriceUpdate();
            update.setSymbol(node.get("s").asText());
            update.setPrice(node.get("p").asLong());
            update.setEventTime(Instant.ofEpochMilli(node.get("E").asLong()));
            return update;
        } catch (Exception e) {
            log.error("Failed to parse message: {}", json, e);
            return null;
        }
    }
}
