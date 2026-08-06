package com.example.connections.application.port.in;

import com.example.connections.domain.model.Course;

import java.util.UUID;

public interface CourseSyncUseCase {

    Course syncCourse(UUID courseId, String title);

    void syncEnrollment(UUID userId, UUID courseId);

    void removeEnrollment(UUID userId, UUID courseId);
}
