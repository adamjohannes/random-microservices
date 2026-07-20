package domain

import (
	"errors"
	"fmt"

	"github.com/google/uuid"
)

var ErrInvalidAccountID = errors.New("invalid account ID format")

// AccountID is a Value Object for e-mail creation and validation.
type AccountID struct {
	value string
}

// BuildAccountID reconstructs an AccountID from a string.
func BuildAccountID(value string) (AccountID, error) {
	parsedUUID, err := uuid.Parse(value)
	if err != nil {
		return AccountID{}, fmt.Errorf("%w: %w", ErrInvalidAccountID, err)
	}

	return AccountID{value: parsedUUID.String()}, nil
}

// NewAccountID factory for the AccountID value object.
func NewAccountID() AccountID {
	return AccountID{value: uuid.NewString()}
}
