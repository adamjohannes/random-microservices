package domain_test

import (
	"account/internal/domain"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewName(t *testing.T) {
	tests := []struct {
		name          string
		input         string
		expectedError error
		expectedValue string
	}{
		{"Valid name", "John", nil, "John"},
		{"Valid name with spaces", "John Doe", nil, "John Doe"},
		{"Trims surrounding whitespace", "  John  ", nil, "John"},
		{"Minimum length", "Jo", nil, "Jo"},
		{"Maximum length", strings.Repeat("a", 50), nil, strings.Repeat("a", 50)},
		{"Too short", "J", domain.ErrInvalidNameLength, ""},
		{"Empty after trim", "   ", domain.ErrInvalidNameLength, ""},
		{"Too long", strings.Repeat("a", 51), domain.ErrInvalidNameLength, ""},
		{"Contains digits", "John3", domain.ErrInvalidNameCharacter, ""},
		{"Contains special characters", "John!", domain.ErrInvalidNameCharacter, ""},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			name, err := domain.NewName(tt.input)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expectedValue, name.String())
			}
		})
	}
}
