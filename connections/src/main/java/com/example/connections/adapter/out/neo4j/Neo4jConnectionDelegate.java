package com.example.connections.adapter.out.neo4j;

import com.example.connections.domain.model.Connection;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.data.neo4j.repository.query.Query;

import java.util.List;
import java.util.UUID;

public interface Neo4jConnectionDelegate extends Neo4jRepository<Connection, String> {

    @Query("""
            MATCH (requester:User)-[:SENT_REQUEST]->(c:Connection)<-[:RECEIVED_REQUEST]-(addressee:User)
            WHERE requester.id = $userId OR addressee.id = $userId
            RETURN c, collect(requester) AS sentRequests, collect(addressee) AS receivedRequests
            """)
    List<Connection> findAllByUserId(UUID userId);

    @Query("""
            MATCH (requester:User)-[:SENT_REQUEST]->(c:Connection {status:'ACCEPTED'})<-[:RECEIVED_REQUEST]-(addressee:User)
            WHERE requester.id = $userId OR addressee.id = $userId
            RETURN c, collect(requester) AS sentRequests, collect(addressee) AS receivedRequests
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
