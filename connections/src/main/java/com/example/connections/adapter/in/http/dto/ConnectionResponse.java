package com.example.connections.adapter.in.http.dto;

public record ConnectionResponse(
    String id,
    String status,
    UserResponse requester,
    UserResponse addressee,
    String createdAt,
    String updatedAt
) {}
