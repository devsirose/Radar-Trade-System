package com.radartrade.platform.service.common.exception;

import com.radartrade.platform.service.common.constant.ErrorCode;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.experimental.FieldDefaults;

@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@AllArgsConstructor
@Getter
public class AppException extends RuntimeException {
    ErrorCode errorCode;
    String errorMessage;
}
