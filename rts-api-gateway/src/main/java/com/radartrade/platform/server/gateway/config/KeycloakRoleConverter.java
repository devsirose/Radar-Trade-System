package com.radartrade.platform.server.gateway.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.core.convert.converter.Converter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
public class KeycloakRoleConverter  implements Converter<Jwt, Collection<GrantedAuthority>> {

    @Override
    public Collection<GrantedAuthority> convert(Jwt source) {
        Map<String, Object> realmAccess = (Map<String, Object>) source.getClaims().get("realm_access");
        if (realmAccess == null || realmAccess.isEmpty()) {
            return new ArrayList<>();
        }
        Collection<GrantedAuthority> grantedAuthorities = ((List<String>) realmAccess.get("roles"))
                .stream().map(this::normalizeRoleName)
                .map(SimpleGrantedAuthority::new)
                .collect(Collectors.toList());
        return grantedAuthorities;
    }

    private String normalizeRoleName(String role) {
        role = role.toLowerCase();
        log.trace("Normalizing role: {}", role);
        if (role.startsWith("ROLE_"))
            return role;
        return new StringBuilder().append("ROLE_").append(role).toString();
    }

}