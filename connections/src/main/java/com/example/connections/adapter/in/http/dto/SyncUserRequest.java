package com.example.connections.adapter.in.http.dto;

import java.util.UUID;

public record SyncUserRequest(UUID accountId, String name, String email) {}
