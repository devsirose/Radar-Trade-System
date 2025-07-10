package com.radartrade.platform.server.gateway.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ApiGatewayConfig {
    /**
     * Định nghĩa các route cho Spring Cloud Gateway bằng Java code.
     *
     * Phương thức này sử dụng {@link RouteLocatorBuilder} để cấu hình các route thủ công
     * thay vì qua file cấu hình YAML. Mỗi route định nghĩa đường dẫn đầu vào (predicate)
     * và địa chỉ dịch vụ backend tương ứng (URI), có thể là HTTP tĩnh hoặc dịch vụ đã đăng ký
     * với service registry (Eureka, Consul) thông qua `lb://<service-name>`.
     *
     * Ví dụ:
     * - Route với path "/account/**" sẽ được định tuyến đến service "account-service".
     * - Route với path "/order/**" sẽ được định tuyến đến service "order-service".
     *
     * @param builder đối tượng hỗ trợ xây dựng RouteLocator, được Spring tiêm tự động.
     * @return RouteLocator chứa danh sách các route đã cấu hình.
     *
     * Code:
     * return builder.routes()
     *         .route("account-service", r -> r
     *             .path("/account/**")
     *             .uri("lb://account-service"))
     *         .route("order-service", r -> r
     *             .path("/order/**")
     *             .uri("lb://order-service"))
     *         .build();
     */
    @Bean
    public RouteLocator routes(RouteLocatorBuilder builder) {
        return builder.routes().build();
    }

}
