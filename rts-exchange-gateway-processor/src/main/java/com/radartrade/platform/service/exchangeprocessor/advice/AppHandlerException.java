package com.radartrade.platform.service.exchangeprocessor.advice;

import com.radartrade.platform.service.common.exception.AppException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import java.util.LinkedHashMap;
import java.util.Map;

@ControllerAdvice
@Slf4j
public class AppHandlerException extends ResponseEntityExceptionHandler {
    private static final String MESSAGE = "message";
    private static final String ERROR_KEY = "errorKey";

    @ExceptionHandler(AppException.class)
    public ResponseEntity<Object> notFound(Exception ex) {
        Map<String, Object> body = new LinkedHashMap<>();
        AppException appException = (AppException) ex;
        body.put(MESSAGE, StringUtils.hasLength(ex.getMessage())? appException.getErrorMessage(): appException.getErrorCode());
        body.put(ERROR_KEY, appException.getErrorCode());
        log.error(appException.getErrorMessage(), appException);
        return new ResponseEntity<>(body, HttpStatus.NOT_FOUND);
    }

}
