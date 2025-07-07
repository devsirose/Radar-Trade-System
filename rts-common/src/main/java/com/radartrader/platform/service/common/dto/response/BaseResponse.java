package com.radartrader.platform.service.common.dto.response;

import java.io.Serializable;

public class BaseResponse <T> implements Serializable {
    private static final long serialVersionUID = 1L;
    private String status;
    private String errorMessage;
    private T data;
}
