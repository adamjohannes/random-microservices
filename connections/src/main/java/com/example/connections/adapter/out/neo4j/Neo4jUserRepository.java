package com.example.connections.adapter.out.neo4j;

import com.example.connections.application.port.out.UserRepository;
import com.example.connections.domain.model.User;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public class Neo4jUserRepository implements UserRepository {

    private final Neo4jUserDelegate delegate;

    public Neo4jUserRepository(Neo4jUserDelegate delegate) {
        this.delegate = delegate;
    }

    @Override
    public Optional<User> findById(UUID id) {
        return delegate.findById(id);
    }

    @Override
    public User save(User user) {
        return delegate.save(user);
    }
}
