package com.example.connections.adapter.in.http;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.UUID;

public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final SecretKey userKey;
    private final SecretKey m2mKey;

    public JwtAuthenticationFilter(String jwtSecret, String m2mSecret) {
        this.userKey = new SecretKeySpec(jwtSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
        this.m2mKey = new SecretKeySpec(m2mSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            String token = header.substring(7);
            trySetAuthentication(token);
        }
        chain.doFilter(request, response);
    }

    private void trySetAuthentication(String token) {
        if (tryUserJwt(token)) return;
        tryM2mJwt(token);
    }

    private boolean tryUserJwt(String token) {
        try {
            Claims claims = Jwts.parser()
                .verifyWith(userKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();

            String sub = claims.getSubject();
            if (sub == null) return false;

            UUID userId = UUID.fromString(sub);
            UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                userId, null, List.of(new SimpleGrantedAuthority("ROLE_USER"))
            );
            SecurityContextHolder.getContext().setAuthentication(auth);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    private boolean tryM2mJwt(String token) {
        try {
            Claims claims = Jwts.parser()
                .verifyWith(m2mKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();

            String service = claims.get("service", String.class);
            if (service == null) return false;

            UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                service, null, List.of(new SimpleGrantedAuthority("ROLE_SERVICE"))
            );
            SecurityContextHolder.getContext().setAuthentication(auth);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }
}
