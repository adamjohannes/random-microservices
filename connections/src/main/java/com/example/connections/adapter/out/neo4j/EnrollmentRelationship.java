package com.example.connections.adapter.out.neo4j;

import com.example.connections.domain.model.Course;
import org.springframework.data.neo4j.core.schema.RelationshipId;
import org.springframework.data.neo4j.core.schema.RelationshipProperties;
import org.springframework.data.neo4j.core.schema.TargetNode;

@RelationshipProperties
public class EnrollmentRelationship {

    @RelationshipId
    private Long id;

    @TargetNode
    private Course course;

    public EnrollmentRelationship() {}

    public EnrollmentRelationship(Course course) {
        this.course = course;
    }

    public Long getId() { return id; }
    public Course getCourse() { return course; }
    public void setCourse(Course course) { this.course = course; }
}
