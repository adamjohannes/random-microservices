package com.example.connections.application.usecase;

import com.example.connections.application.port.in.UserSyncUseCase;
import com.example.connections.application.port.out.UserRepository;
import com.example.connections.domain.model.User;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
public class UserSyncService implements UserSyncUseCase {

    private final UserRepository userRepository;

    public UserSyncService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    @Transactional
    public User syncUser(UUID id, String name, String email) {
        User user = userRepository.findById(id).orElseGet(() -> new User(id, name, email));

        if (!user.getName().equals(name) || !user.getEmail().equals(email)) {
            user.setName(name);
            user.setEmail(email);
        }

        return userRepository.save(user);
    }
}
