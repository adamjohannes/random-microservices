package com.example.connections.application.port.out;

import com.example.connections.domain.model.User;

import java.util.Optional;
import java.util.UUID;

public interface UserRepository {

    Optional<User> findById(UUID id);

    User save(User user);
}
