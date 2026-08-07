package com.example.connections.adapter.out.neo4j;

import com.example.connections.domain.model.Course;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.data.neo4j.repository.query.Query;

import java.util.UUID;

public interface Neo4jCourseDelegate extends Neo4jRepository<Course, UUID> {

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
