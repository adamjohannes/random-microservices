package com.example.connections.adapter.in.http;

import com.example.connections.adapter.in.http.dto.SyncCourseRequest;
import com.example.connections.adapter.in.http.dto.SyncEnrollmentRequest;
import com.example.connections.application.port.in.CourseSyncUseCase;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/courses")
public class CourseSyncController {

    private final CourseSyncUseCase courseSyncUseCase;

    public CourseSyncController(CourseSyncUseCase courseSyncUseCase) {
        this.courseSyncUseCase = courseSyncUseCase;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.OK)
    void syncCourse(@RequestBody SyncCourseRequest body) {
        courseSyncUseCase.syncCourse(body.courseId(), body.title());
    }

    @PostMapping("/{courseId}/enrollment")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    void syncEnrollment(@PathVariable UUID courseId, @RequestBody SyncEnrollmentRequest body) {
        courseSyncUseCase.syncEnrollment(body.userId(), courseId);
    }

    @DeleteMapping("/{courseId}/enrollment/{userId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    void removeEnrollment(@PathVariable UUID courseId, @PathVariable UUID userId) {
        courseSyncUseCase.removeEnrollment(userId, courseId);
    }
}
