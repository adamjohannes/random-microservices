package com.example.connections.adapter.in.http.dto;

import java.util.UUID;

public record SyncCourseRequest(UUID courseId, String title) {}
