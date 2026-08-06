package com.example.connections.adapter.in.http;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Value("${JWT_SECRET}")
    private String jwtSecret;

    @Value("${M2M_SECRET}")
    private String m2mSecret;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        JwtAuthenticationFilter userFilter = new JwtAuthenticationFilter(jwtSecret, m2mSecret);

        http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .addFilterBefore(userFilter, UsernamePasswordAuthenticationFilter.class)
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(HttpMethod.POST, "/users").hasRole("SERVICE")
                .requestMatchers(HttpMethod.POST, "/courses").hasRole("SERVICE")
                .requestMatchers(HttpMethod.POST, "/courses/*/enrollment").hasRole("SERVICE")
                .requestMatchers(HttpMethod.DELETE, "/courses/*/enrollment/*").hasRole("SERVICE")
                .anyRequest().hasRole("USER")
            );

        return http.build();
    }
}
