package domain_test

import (
	"account/internal/domain"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestBuildAccountID(t *testing.T) {
	valid := uuid.NewString()

	tests := []struct {
		name          string
		input         string
		expectedError error
		expectedValue string
	}{
		{"Valid UUID", valid, nil, valid},
		{"Empty string", "", domain.ErrInvalidAccountID, ""},
		{"Malformed UUID", "not-a-uuid", domain.ErrInvalidAccountID, ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			id, err := domain.BuildAccountID(tt.input)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expectedValue, id.String())
			}
		})
	}
}

func TestNewAccountID(t *testing.T) {
	id := domain.NewAccountID()

	assert.NotEmpty(t, id.String())
	_, err := uuid.Parse(id.String())
	assert.NoError(t, err)
}
