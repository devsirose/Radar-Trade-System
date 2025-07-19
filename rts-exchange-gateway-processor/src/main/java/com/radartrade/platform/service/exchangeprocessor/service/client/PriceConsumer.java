package com.radartrade.platform.service.exchangeprocessor.service.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.radartrade.platform.service.exchangeprocessor.domain.PriceUpdate;
import lombok.AccessLevel;

import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.socket.WebSocketMessage;
import org.springframework.web.reactive.socket.client.ReactorNettyWebSocketClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Sinks;

import java.net.URI;

@Service
@Slf4j
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class PriceConsumer {
    @Value("${ws.binance.api.uri}")
    private static String WS_URI ;

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Sinks.Many<PriceUpdate> sink = Sinks.many().multicast().onBackpressureBuffer();

    public PriceConsumer() {
        connect();
    }

    public Flux<PriceUpdate> priceUpdatesStream() {
        return sink.asFlux();
    }

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
            update.setPrice(node.get("p").asText());
            update.setEventTime(node.get("E").asLong());
            return update;
        } catch (Exception e) {
            log.error("Failed to parse message: {}", json, e);
            return null;
        }
    }
}
