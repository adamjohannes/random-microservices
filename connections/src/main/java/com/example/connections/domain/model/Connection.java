package com.example.connections.domain.model;

import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;
import org.springframework.data.neo4j.core.schema.Relationship;

import java.time.Instant;
import java.util.Arrays;
import java.util.UUID;

@Node("Connection")
public class Connection {

    @Id
    private String id;
    private ConnectionStatus status;
    private String createdAt;
    private String updatedAt;

    @Relationship(type = "SENT_REQUEST", direction = Relationship.Direction.INCOMING)
    private User requester;

    @Relationship(type = "RECEIVED_REQUEST", direction = Relationship.Direction.INCOMING)
    private User addressee;

    public Connection() {}

    public static Connection create(UUID requesterId, UUID addresseeId) {
        String[] sorted = new String[]{requesterId.toString(), addresseeId.toString()};
        Arrays.sort(sorted);

        Connection c = new Connection();
        c.id = sorted[0] + "_" + sorted[1];
        c.status = ConnectionStatus.PENDING;
        String now = Instant.now().toString();
        c.createdAt = now;
        c.updatedAt = now;
        return c;
    }

    public String getId() { return id; }
    public ConnectionStatus getStatus() { return status; }
    public String getCreatedAt() { return createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public User getRequester() { return requester; }
    public User getAddressee() { return addressee; }

    public void setId(String id) { this.id = id; }
    public void setStatus(ConnectionStatus status) { this.status = status; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
    public void setRequester(User requester) { this.requester = requester; }
    public void setAddressee(User addressee) { this.addressee = addressee; }
}
