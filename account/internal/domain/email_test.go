package domain_test

import (
	"account/internal/domain"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewEmail(t *testing.T) {
	tests := []struct {
		name          string
		input         string
		expectedError error
		expectedValue string
	}{
		{"Valid e-mail", "test@example.com", nil, "test@example.com"},
		{"Valid e-mail with uppercase", "Test@example.com", nil, "test@example.com"},
		{"Empty e-mail", "    ", domain.ErrEmailEmpty, ""},
		{"Invalid TLD", "test@example.c", domain.ErrInvalidEmail, ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			email, err := domain.NewEmail(tt.input)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expectedValue, email.String())
			}
		})
	}
}
