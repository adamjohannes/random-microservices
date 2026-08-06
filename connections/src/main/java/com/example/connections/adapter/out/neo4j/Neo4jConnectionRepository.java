package com.example.connections.adapter.out.neo4j;

import com.example.connections.application.port.in.ConnectionUseCase.CourseProjection;
import com.example.connections.application.port.out.ConnectionRepository;
import com.example.connections.domain.model.Connection;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.data.neo4j.repository.query.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public class Neo4jConnectionRepository implements ConnectionRepository {

    private final Delegate delegate;

    public Neo4jConnectionRepository(Delegate delegate) {
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
    public List<CourseProjection> findConnectionsCourses(UUID userId) {
        return delegate.findConnectionsCourses(userId).stream()
                .map(r -> new CourseProjection(r.courseId, r.courseTitle, r.enrolledUserId, r.enrolledUserName))
                .toList();
    }

    interface Delegate extends Neo4jRepository<Connection, String> {

        @Query("""
                MATCH (me:User {id: $userId})-[:SENT_REQUEST|RECEIVED_REQUEST]-(c:Connection {status:'ACCEPTED'})
                      -[:SENT_REQUEST|RECEIVED_REQUEST]-(friend:User)
                WHERE me.id <> friend.id
                RETURN c
                """)
        List<Connection> findAcceptedByUserId(UUID userId);

        @Query("""
                MATCH (me:User {id: $userId})-[:SENT_REQUEST|RECEIVED_REQUEST]-(c:Connection {status:'ACCEPTED'})
                      -[:SENT_REQUEST|RECEIVED_REQUEST]-(friend:User)
                WHERE me.id <> friend.id
                MATCH (friend)-[:ENROLLED_IN]->(course:Course)
                RETURN course.id AS courseId, course.title AS courseTitle,
                       friend.id AS enrolledUserId, friend.name AS enrolledUserName
                """)
        List<CourseEnrollmentResult> findConnectionsCourses(UUID userId);
    }
}
