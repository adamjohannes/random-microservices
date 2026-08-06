package rabbitmq

import "time"

type UserRegisteredEvent struct {
	EventType  string    `json:"event_type"`
	OccurredAt time.Time `json:"occurred_at"`
	AccountID  string    `json:"account_id"`
	Name       string    `json:"name"`
	Email      string    `json:"email"`
}
