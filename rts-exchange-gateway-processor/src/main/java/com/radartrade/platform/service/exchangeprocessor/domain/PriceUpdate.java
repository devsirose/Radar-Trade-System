package com.radartrade.platform.service.exchangeprocessor.domain;


import jakarta.persistence.*;
import lombok.Data;
import org.springframework.data.relational.core.mapping.Table;

import java.time.Instant;

@Data
@Entity
@Table(name = "price")
public class PriceUpdate {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String symbol;
    private Double price;
    @Column(name = "event_time", nullable = false)
    private Instant eventTime;

}
