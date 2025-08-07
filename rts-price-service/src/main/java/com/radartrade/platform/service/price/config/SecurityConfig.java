package com.radartrade.platform.service.price.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.web.server.SecurityWebFilterChain;

@Configuration
@EnableWebFluxSecurity
public class SecurityConfig {

    @Bean
    public SecurityWebFilterChain securityWebFilterChain(ServerHttpSecurity http) {
        http
                // Vô hiệu hóa CSRF
                .csrf(ServerHttpSecurity.CsrfSpec::disable)
                // Cấu hình quyền truy cập
                .authorizeExchange(exchange -> exchange
                        // Cho phép tất cả các yêu cầu đến đường dẫn này đi qua mà không cần xác thực
                        .pathMatchers("/api/v1/price/kline/stream/**").permitAll()
                        // Yêu cầu xác thực cho tất cả các đường dẫn còn lại
                        .anyExchange().authenticated()
                );
        return http.build();
    }

}
