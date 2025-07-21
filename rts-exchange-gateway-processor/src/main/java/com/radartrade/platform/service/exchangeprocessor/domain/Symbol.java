package com.radartrade.platform.service.exchangeprocessor.domain;

import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.experimental.FieldDefaults;

@AllArgsConstructor
@EqualsAndHashCode
@Getter
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Symbol {
    String name;
}
