package com.example.connections.adapter.in.http;

import com.example.connections.adapter.in.http.dto.ConnectionResponse;
import com.example.connections.adapter.in.http.dto.CourseEnrollmentResponse;
import com.example.connections.adapter.in.http.dto.SendConnectionRequest;
import com.example.connections.adapter.in.http.dto.UserResponse;
import com.example.connections.application.port.in.ConnectionUseCase;
import com.example.connections.domain.model.Connection;
import com.example.connections.domain.model.User;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/connections")
public class ConnectionController {

    private final ConnectionUseCase connectionUseCase;

    public ConnectionController(ConnectionUseCase connectionUseCase) {
        this.connectionUseCase = connectionUseCase;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    ConnectionResponse sendRequest(@AuthenticationPrincipal UUID requesterId,
                                   @RequestBody SendConnectionRequest body) {
        Connection conn = connectionUseCase.sendRequest(requesterId, body.addresseeId());
        return toResponse(conn);
    }

    @PatchMapping("/{connectionId}/accept")
    ConnectionResponse accept(@AuthenticationPrincipal UUID actorId,
                               @PathVariable String connectionId) {
        Connection conn = connectionUseCase.respondToRequest(connectionId, actorId, true);
        return toResponse(conn);
    }

    @PatchMapping("/{connectionId}/reject")
    ConnectionResponse reject(@AuthenticationPrincipal UUID actorId,
                               @PathVariable String connectionId) {
        Connection conn = connectionUseCase.respondToRequest(connectionId, actorId, false);
        return toResponse(conn);
    }

    @GetMapping
    List<UserResponse> listConnections(@AuthenticationPrincipal UUID userId) {
        return connectionUseCase.listConnections(userId).stream()
            .map(this::toUserResponse)
            .toList();
    }

    @GetMapping("/courses")
    List<CourseEnrollmentResponse> listConnectionsCourses(@AuthenticationPrincipal UUID userId) {
        return connectionUseCase.listConnectionsCourses(userId).stream()
            .map(p -> new CourseEnrollmentResponse(p.courseId(), p.courseTitle(), p.enrolledUserId(), p.enrolledUserName()))
            .toList();
    }

    private ConnectionResponse toResponse(Connection conn) {
        return new ConnectionResponse(
            conn.getId(),
            conn.getStatus().name(),
            conn.getRequester() != null ? toUserResponse(conn.getRequester()) : null,
            conn.getAddressee() != null ? toUserResponse(conn.getAddressee()) : null,
            conn.getCreatedAt(),
            conn.getUpdatedAt()
        );
    }

    private UserResponse toUserResponse(User user) {
        return new UserResponse(user.getId(), user.getName(), user.getEmail());
    }
}
