package com.example.connections.domain.model;

import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;

import java.util.UUID;

@Node("Course")
public class Course {

    @Id
    private UUID id;
    private String title;

    public Course() {}

    public Course(UUID id, String title) {
        this.id = id;
        this.title = title;
    }

    public UUID getId() { return id; }
    public String getTitle() { return title; }

    public void setId(UUID id) { this.id = id; }
    public void setTitle(String title) { this.title = title; }
}
