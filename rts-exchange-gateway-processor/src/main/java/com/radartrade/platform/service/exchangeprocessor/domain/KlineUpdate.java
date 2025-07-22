package com.radartrade.platform.service.exchangeprocessor.domain;

import lombok.*;
import org.springframework.data.relational.core.mapping.Table;

import java.time.Instant;

@Data
@Table(name = "kline")
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Getter
public class KlineUpdate {

    private String symbol;       // BTCUSDT
    private String interval;     // "1m", "5m", "1h", v.v.
    private Instant openTime;       // Timestamp mở nến (milliseconds)
    private Instant closeTime;      // Timestamp đóng nến (milliseconds)

    private Double open;     // Giá mở cửa
    private Double high;     // Giá cao nhất
    private Double low;      // Giá thấp nhất
    private Double close;    // Giá đóng cửa

    private Double volume;   // Volume (base asset)
    private int tradesCount;     // Số lượng giao dịch trong nến

    private boolean closed;// Đánh dấu đã khép nến (true nếu nến đã kết thúc)

    public boolean isClosed() {
        return closed;
    }
}