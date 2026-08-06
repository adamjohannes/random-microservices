package com.example.connections.application.port.out;

import com.example.connections.domain.model.Course;

import java.util.Optional;
import java.util.UUID;

public interface CourseRepository {

    Optional<Course> findById(UUID id);

    Course save(Course course);

    void createEnrollment(UUID userId, UUID courseId);

    void deleteEnrollment(UUID userId, UUID courseId);
}
