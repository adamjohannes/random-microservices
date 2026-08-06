package com.example.connections.adapter.in.http.dto;

import java.util.UUID;

public record CourseEnrollmentResponse(
    UUID courseId,
    String courseTitle,
    UUID enrolledUserId,
    String enrolledUserName
) {}
