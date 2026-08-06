package com.example.connections.domain.model;

import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;

import java.util.UUID;

@Node("User")
public class User {

    @Id
    private UUID id;
    private String name;
    private String email;

    public User() {}

    public User(UUID id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }

    public UUID getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }

    public void setId(UUID id) { this.id = id; }
    public void setName(String name) { this.name = name; }
    public void setEmail(String email) { this.email = email; }
}
