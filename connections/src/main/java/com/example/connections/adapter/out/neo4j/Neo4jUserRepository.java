package com.example.connections.adapter.out.neo4j;

import com.example.connections.application.port.out.UserRepository;
import com.example.connections.domain.model.User;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public class Neo4jUserRepository implements UserRepository {

    private final Delegate delegate;

    public Neo4jUserRepository(Delegate delegate) {
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

    interface Delegate extends Neo4jRepository<User, UUID> {}
}
