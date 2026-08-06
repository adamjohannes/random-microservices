package com.example.connections.application.usecase;

import com.example.connections.application.port.in.CourseSyncUseCase;
import com.example.connections.application.port.out.CourseRepository;
import com.example.connections.application.port.out.UserRepository;
import com.example.connections.domain.exception.NotFoundException;
import com.example.connections.domain.model.Course;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
public class CourseSyncService implements CourseSyncUseCase {

    private final CourseRepository courseRepository;
    private final UserRepository userRepository;

    public CourseSyncService(CourseRepository courseRepository, UserRepository userRepository) {
        this.courseRepository = courseRepository;
        this.userRepository = userRepository;
    }

    @Override
    @Transactional
    public Course syncCourse(UUID id, String title) {
        Course course = courseRepository.findById(id).orElseGet(() -> new Course(id, title));

        if (!course.getTitle().equals(title)) {
            course.setTitle(title);
        }

        return courseRepository.save(course);
    }

    @Override
    @Transactional
    public void syncEnrollment(UUID userId, UUID courseId) {
        userRepository.findById(userId)
                .orElseThrow(() -> new NotFoundException("User not found: " + userId));
        if (courseRepository.findById(courseId).isEmpty()) {
            throw new NotFoundException("Course not found: " + courseId);
        }
        courseRepository.createEnrollment(userId, courseId);
    }

    @Override
    @Transactional
    public void removeEnrollment(UUID userId, UUID courseId) {
        courseRepository.deleteEnrollment(userId, courseId);
    }
}
