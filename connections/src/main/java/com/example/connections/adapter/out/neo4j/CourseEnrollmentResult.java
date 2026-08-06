package com.example.connections.adapter.out.neo4j;

import org.springframework.data.neo4j.core.schema.QueryResult;

import java.util.UUID;

@QueryResult
public class CourseEnrollmentResult {

    public UUID courseId;
    public String courseTitle;
    public UUID enrolledUserId;
    public String enrolledUserName;
}
