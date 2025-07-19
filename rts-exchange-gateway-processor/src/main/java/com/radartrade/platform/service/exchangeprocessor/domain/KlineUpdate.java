package com.radartrade.platform.service.exchangeprocessor.domain;

import jakarta.persistence.*;
import lombok.Data;

import java.math.BigDecimal;
@Data
@Entity
@Table(name = "kline")
public class KlineUpdate {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String symbol;       // BTCUSDT
    private String interval;     // "1m", "5m", "1h", v.v.
    private long openTime;       // Timestamp mở nến (milliseconds)
    private long closeTime;      // Timestamp đóng nến (milliseconds)

    private BigDecimal open;     // Giá mở cửa
    private BigDecimal high;     // Giá cao nhất
    private BigDecimal low;      // Giá thấp nhất
    private BigDecimal close;    // Giá đóng cửa

    private BigDecimal volume;   // Volume (base asset)
    private int tradesCount;     // Số lượng giao dịch trong nến

    private boolean closed;      // Đánh dấu đã khép nến (true nếu nến đã kết thúc)
}