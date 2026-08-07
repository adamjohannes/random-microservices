package com.example.connections.adapter.out.neo4j;

import com.example.connections.domain.model.User;
import org.springframework.data.neo4j.repository.Neo4jRepository;

import java.util.UUID;

public interface Neo4jUserDelegate extends Neo4jRepository<User, UUID> {}
