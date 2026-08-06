package com.example.connections.application.usecase;

import com.example.connections.domain.exception.AuthorizationException;
import com.example.connections.domain.exception.NotFoundException;
import com.example.connections.domain.exception.StateException;
import com.example.connections.domain.model.Connection;
import com.example.connections.domain.model.ConnectionStatus;
import com.example.connections.domain.model.User;
import com.example.connections.application.port.in.ConnectionUseCase;
import com.example.connections.application.port.out.ConnectionRepository;
import com.example.connections.application.port.out.UserRepository;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Service
public class ConnectionService implements ConnectionUseCase {

    private final ConnectionRepository connectionRepository;
    private final UserRepository userRepository;

    public ConnectionService(ConnectionRepository connectionRepository, UserRepository userRepository) {
        this.connectionRepository = connectionRepository;
        this.userRepository = userRepository;
    }

    @Override
    @Transactional
    public Connection sendRequest(UUID requesterId, UUID addresseeId) {
        if (requesterId.equals(addresseeId)) {
            throw new StateException("Cannot send a connection request to yourself");
        }

        User requester = userRepository.findById(requesterId)
                .orElseThrow(() -> new NotFoundException("User not found: " + requesterId));
        User addressee = userRepository.findById(addresseeId)
                .orElseThrow(() -> new NotFoundException("User not found: " + addresseeId));

        Connection connection = Connection.create(requesterId, addresseeId);
        connection.setRequester(requester);
        connection.setAddressee(addressee);

        try {
            return connectionRepository.save(connection);
        } catch (DataIntegrityViolationException e) {
            return connectionRepository.findById(connection.getId())
                    .orElseThrow(() -> new StateException("Connection conflict but record not found"));
        }
    }

    @Override
    @Transactional
    public Connection respondToRequest(String connectionId, UUID actorId, boolean accept) {
        Connection connection = connectionRepository.findById(connectionId)
                .orElseThrow(() -> new NotFoundException("Connection not found: " + connectionId));

        if (!connection.getAddressee().getId().equals(actorId)) {
            throw new AuthorizationException("Only the addressee may respond to this request");
        }

        if (connection.getStatus() != ConnectionStatus.PENDING) {
            throw new StateException("Connection is not in PENDING state: " + connection.getStatus());
        }

        connection.setStatus(accept ? ConnectionStatus.ACCEPTED : ConnectionStatus.REJECTED);
        connection.setUpdatedAt(Instant.now().toString());

        return connectionRepository.save(connection);
    }

    @Override
    @Transactional(readOnly = true)
    public List<User> listConnections(UUID userId) {
        List<Connection> connections = connectionRepository.findAcceptedByUserId(userId);
        return connections.stream()
                .map(c -> c.getRequester().getId().equals(userId) ? c.getAddressee() : c.getRequester())
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<CourseProjection> listConnectionsCourses(UUID userId) {
        return connectionRepository.findConnectionsCourses(userId);
    }
}
