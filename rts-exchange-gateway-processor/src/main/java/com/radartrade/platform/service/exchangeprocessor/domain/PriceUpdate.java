package com.radartrade.platform.service.exchangeprocessor.domain;


import lombok.Data;
import org.springframework.data.relational.core.mapping.Table;

import java.time.Instant;

@Data
@Table(name = "price")
public class PriceUpdate {
    private String symbol;
    private Double price;
    private Instant eventTime;

}
