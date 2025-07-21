package com.radartrade.platform.service.exchangeprocessor.domain;

import jakarta.persistence.*;
import lombok.Data;
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

    private Double open;     // Giá mở cửa
    private Double high;     // Giá cao nhất
    private Double low;      // Giá thấp nhất
    private Double close;    // Giá đóng cửa

    private Double volume;   // Volume (base asset)
    private int tradesCount;     // Số lượng giao dịch trong nến

    private boolean closed;      // Đánh dấu đã khép nến (true nếu nến đã kết thúc)
}