package com.radartrade.platform.service.exchangeprocessor.domain;

import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "price")
public class PriceUpdate {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String symbol;
    private String price;
    private long eventTime;
}
