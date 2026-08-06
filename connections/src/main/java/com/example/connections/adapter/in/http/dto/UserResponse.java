package com.example.connections.adapter.in.http.dto;

import java.util.UUID;

public record UserResponse(UUID id, String name, String email) {}
