package com.example.connections.adapter.in.http;

import com.example.connections.adapter.in.http.dto.SyncUserRequest;
import com.example.connections.adapter.in.http.dto.UserResponse;
import com.example.connections.application.port.in.UserSyncUseCase;
import com.example.connections.domain.model.User;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/users")
public class UserSyncController {

    private final UserSyncUseCase userSyncUseCase;

    public UserSyncController(UserSyncUseCase userSyncUseCase) {
        this.userSyncUseCase = userSyncUseCase;
    }

    @PostMapping
    UserResponse syncUser(@RequestBody SyncUserRequest body) {
        User user = userSyncUseCase.syncUser(body.accountId(), body.name(), body.email());
        return new UserResponse(user.getId(), user.getName(), user.getEmail());
    }
}
