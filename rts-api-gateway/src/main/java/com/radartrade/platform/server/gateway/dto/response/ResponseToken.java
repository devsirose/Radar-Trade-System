package com.radartrade.platform.server.gateway.dto.response;

import lombok.Builder;

import java.io.Serializable;

/**
 * ResponseToken is a Data Transfer Object (DTO) that encapsulates the set of tokens
 * issued during the OpenID Connect authentication and authorization process.
 * <p>
 * This object is typically returned after a successful login or token refresh operation.
 * It contains the three key types of tokens:
 * </p>
 *
 * @param token        The access token (JWT) used to access protected resources (APIs).
 * @param refreshToken The refresh token used to obtain a new access token without requiring re-authentication.
 * @param idToken      The ID token containing user identity information, such as email, username, etc.
 *
 * @author [Your Name]
 */
@Builder
public record ResponseToken(String token, String refreshToken, String idToken) implements Serializable {}
