package com.radartrade.platform.service.common.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.NoArgsConstructor;

import java.io.Serializable;
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class BaseResponse <T> implements Serializable {
    private static final long serialVersionUID = 1L;
    private String status;
    private String errorMessage;
    private T data;

    public static BaseResponse empty() {
        return new BaseResponse();
    }
}
