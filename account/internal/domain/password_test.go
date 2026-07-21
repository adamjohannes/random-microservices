package domain_test

import (
	"account/internal/domain"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewPassword(t *testing.T) {
	tests := []struct {
		name          string
		input         string
		expectedError error
	}{
		{"Valid password", "Str0ng!Pass", nil},
		{"Too short", "Ab1!de", domain.ErrPasswordTooShort},
		{"Missing lowercase", "STR0NG!PASS", domain.ErrPasswordTooWeak},
		{"Missing uppercase", "str0ng!pass", domain.ErrPasswordTooWeak},
		{"Missing number", "Strong!Pass", domain.ErrPasswordTooWeak},
		{"Missing special character", "Str0ngPass1", domain.ErrPasswordTooWeak},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			password, err := domain.NewPassword(tt.input)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
			} else {
				assert.NoError(t, err)
				assert.NotEmpty(t, password.Hash())
				assert.NotEqual(t, tt.input, password.Hash())
			}
		})
	}
}

func TestPasswordCompare(t *testing.T) {
	password, err := domain.NewPassword("Str0ng!Pass")
	assert.NoError(t, err)

	assert.True(t, password.Compare("Str0ng!Pass"))
	assert.False(t, password.Compare("wrong-password"))
}

func TestLoadPasswordRoundTrip(t *testing.T) {
	original, err := domain.NewPassword("Str0ng!Pass")
	assert.NoError(t, err)

	loaded := domain.LoadPassword(original.Hash())

	assert.Equal(t, original.Hash(), loaded.Hash())
	assert.True(t, loaded.Compare("Str0ng!Pass"))
}
