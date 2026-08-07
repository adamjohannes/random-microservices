package com.example.connections.adapter.out.neo4j;

import com.example.connections.application.port.out.CourseRepository;
import com.example.connections.domain.model.Course;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public class Neo4jCourseRepository implements CourseRepository {

    private final Neo4jCourseDelegate delegate;

    public Neo4jCourseRepository(Neo4jCourseDelegate delegate) {
        this.delegate = delegate;
    }

    @Override
    public Optional<Course> findById(UUID id) {
        return delegate.findById(id);
    }

    @Override
    public Course save(Course course) {
        return delegate.save(course);
    }

    @Override
    public void createEnrollment(UUID userId, UUID courseId) {
        delegate.createEnrollment(userId, courseId);
    }

    @Override
    public void deleteEnrollment(UUID userId, UUID courseId) {
        delegate.deleteEnrollment(userId, courseId);
    }
}
