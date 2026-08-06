package com.example.connections.application.port.in;

import com.example.connections.domain.model.Connection;
import com.example.connections.domain.model.User;

import java.util.List;
import java.util.UUID;

public interface ConnectionUseCase {

    record CourseProjection(UUID courseId, String courseTitle, UUID enrolledUserId, String enrolledUserName) {}

    Connection sendRequest(UUID requesterId, UUID addresseeId);

    Connection respondToRequest(String connectionId, UUID actorId, boolean accept);

    List<User> listConnections(UUID userId);

    List<CourseProjection> listConnectionsCourses(UUID userId);
}
