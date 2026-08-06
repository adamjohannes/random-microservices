package com.example.connections.adapter.out.messaging.events;

import com.fasterxml.jackson.annotation.JsonProperty;

public record RequestReceivedEvent(
    @JsonProperty("event_type")    String eventType,
    @JsonProperty("occurred_at")   String occurredAt,
    @JsonProperty("connection_id") String connectionId,
    @JsonProperty("requester_id")  String requesterId,
    @JsonProperty("requester_name") String requesterName,
    @JsonProperty("addressee_id")  String addresseeId,
    @JsonProperty("addressee_name") String addresseeName,
    @JsonProperty("addressee_email") String addresseeEmail
) {}
