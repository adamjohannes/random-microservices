package com.example.connections.application.port.out;

import com.example.connections.application.port.in.ConnectionUseCase.CourseProjection;
import com.example.connections.domain.model.Connection;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface ConnectionRepository {

    Optional<Connection> findById(String id);

    Connection save(Connection connection);

    List<Connection> findAcceptedByUserId(UUID userId);

    List<Connection> findAllByUserId(UUID userId);

    List<CourseProjection> findConnectionsCourses(UUID userId);
}
