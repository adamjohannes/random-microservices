package com.example.connections.application;

import com.example.connections.adapter.out.messaging.EventPublisher;
import com.example.connections.application.port.out.ConnectionRepository;
import com.example.connections.application.port.out.UserRepository;
import com.example.connections.application.usecase.ConnectionService;
import com.example.connections.domain.exception.AuthorizationException;
import com.example.connections.domain.exception.NotFoundException;
import com.example.connections.domain.exception.StateException;
import com.example.connections.domain.model.Connection;
import com.example.connections.domain.model.ConnectionStatus;
import com.example.connections.domain.model.User;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ConnectionServiceTest {

    @Mock
    private ConnectionRepository connectionRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private EventPublisher eventPublisher;

    private ConnectionService service;

    private final UUID requesterId = UUID.randomUUID();
    private final UUID addresseeId = UUID.randomUUID();
    private final User requester   = new User(requesterId, "Alice", "alice@example.com");
    private final User addressee   = new User(addresseeId, "Bob",   "bob@example.com");

    @BeforeEach
    void setUp() {
        service = new ConnectionService(connectionRepository, userRepository, eventPublisher);
    }

    // ── sendRequest ──────────────────────────────────────────────────────────

    @Test
    void sendRequest_succeedsForTwoExistingUsers() {
        when(userRepository.findById(requesterId)).thenReturn(Optional.of(requester));
        when(userRepository.findById(addresseeId)).thenReturn(Optional.of(addressee));

        Connection pending = Connection.create(requesterId, addresseeId);
        pending.setRequester(requester);
        pending.setAddressee(addressee);
        when(connectionRepository.save(any())).thenReturn(pending);

        Connection result = service.sendRequest(requesterId, addresseeId);

        assertThat(result.getStatus()).isEqualTo(ConnectionStatus.PENDING);
    }

    @Test
    void sendRequest_throwsNotFoundForUnknownRequester() {
        when(userRepository.findById(requesterId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.sendRequest(requesterId, addresseeId))
                .isInstanceOf(NotFoundException.class);
    }

    @Test
    void sendRequest_throwsNotFoundForUnknownAddressee() {
        when(userRepository.findById(requesterId)).thenReturn(Optional.of(requester));
        when(userRepository.findById(addresseeId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.sendRequest(requesterId, addresseeId))
                .isInstanceOf(NotFoundException.class);
    }

    @Test
    void sendRequest_throwsStateExceptionForSelfRequest() {
        assertThatThrownBy(() -> service.sendRequest(requesterId, requesterId))
                .isInstanceOf(StateException.class);
    }

    // ── respondToRequest ─────────────────────────────────────────────────────

    @Test
    void respondToRequest_accept_setsStatusAccepted() {
        Connection pending = pendingConnection();
        when(connectionRepository.findById(pending.getId())).thenReturn(Optional.of(pending));

        ArgumentCaptor<Connection> saved = ArgumentCaptor.forClass(Connection.class);
        when(connectionRepository.save(saved.capture())).thenAnswer(inv -> inv.getArgument(0));

        service.respondToRequest(pending.getId(), addresseeId, true);

        assertThat(saved.getValue().getStatus()).isEqualTo(ConnectionStatus.ACCEPTED);
    }

    @Test
    void respondToRequest_reject_setsStatusRejected() {
        Connection pending = pendingConnection();
        when(connectionRepository.findById(pending.getId())).thenReturn(Optional.of(pending));

        ArgumentCaptor<Connection> saved = ArgumentCaptor.forClass(Connection.class);
        when(connectionRepository.save(saved.capture())).thenAnswer(inv -> inv.getArgument(0));

        service.respondToRequest(pending.getId(), addresseeId, false);

        assertThat(saved.getValue().getStatus()).isEqualTo(ConnectionStatus.REJECTED);
    }

    @Test
    void respondToRequest_throwsAuthorizationExceptionWhenActorIsNotAddressee() {
        Connection pending = pendingConnection();
        when(connectionRepository.findById(pending.getId())).thenReturn(Optional.of(pending));

        UUID outsider = UUID.randomUUID();

        assertThatThrownBy(() -> service.respondToRequest(pending.getId(), outsider, true))
                .isInstanceOf(AuthorizationException.class);
    }

    @Test
    void respondToRequest_throwsStateExceptionWhenAlreadyAccepted() {
        Connection accepted = pendingConnection();
        accepted.setStatus(ConnectionStatus.ACCEPTED);
        when(connectionRepository.findById(accepted.getId())).thenReturn(Optional.of(accepted));

        assertThatThrownBy(() -> service.respondToRequest(accepted.getId(), addresseeId, true))
                .isInstanceOf(StateException.class);
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private Connection pendingConnection() {
        Connection c = Connection.create(requesterId, addresseeId);
        c.setRequester(requester);
        c.setAddressee(addressee);
        return c;
    }
}
