package com.example.connections.adapter.out.neo4j;

import com.example.connections.application.port.out.CourseRepository;
import com.example.connections.domain.model.Course;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.data.neo4j.repository.query.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public class Neo4jCourseRepository implements CourseRepository {

    private final Delegate delegate;

    public Neo4jCourseRepository(Delegate delegate) {
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

    interface Delegate extends Neo4jRepository<Course, UUID> {

        @Query("""
                MATCH (u:User {id: $userId}), (c:Course {id: $courseId})
                MERGE (u)-[:ENROLLED_IN]->(c)
                """)
        void createEnrollment(UUID userId, UUID courseId);

        @Query("""
                MATCH (u:User {id: $userId})-[r:ENROLLED_IN]->(c:Course {id: $courseId})
                DELETE r
                """)
        void deleteEnrollment(UUID userId, UUID courseId);
    }
}
