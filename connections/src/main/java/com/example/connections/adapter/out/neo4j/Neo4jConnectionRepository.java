package com.example.connections.adapter.out.neo4j;

import com.example.connections.application.port.in.ConnectionUseCase.CourseProjection;
import com.example.connections.application.port.out.ConnectionRepository;
import com.example.connections.domain.model.Connection;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public class Neo4jConnectionRepository implements ConnectionRepository {

    private final Neo4jConnectionDelegate delegate;

    public Neo4jConnectionRepository(Neo4jConnectionDelegate delegate) {
        this.delegate = delegate;
    }

    @Override
    public Optional<Connection> findById(String id) {
        return delegate.findById(id);
    }

    @Override
    public Connection save(Connection connection) {
        return delegate.save(connection);
    }

    @Override
    public List<Connection> findAcceptedByUserId(UUID userId) {
        return delegate.findAcceptedByUserId(userId);
    }

    @Override
    public List<Connection> findAllByUserId(UUID userId) {
        return delegate.findAllByUserId(userId);
    }

    @Override
    public List<CourseProjection> findConnectionsCourses(UUID userId) {
        return delegate.findConnectionsCourses(userId).stream()
                .map(r -> new CourseProjection(r.courseId, r.courseTitle, r.enrolledUserId, r.enrolledUserName))
                .toList();
    }
}
