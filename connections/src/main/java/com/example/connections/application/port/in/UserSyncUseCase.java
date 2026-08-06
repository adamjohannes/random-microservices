package com.example.connections.application.port.in;

import com.example.connections.domain.model.User;

import java.util.UUID;

public interface UserSyncUseCase {

    User syncUser(UUID accountId, String name, String email);
}
