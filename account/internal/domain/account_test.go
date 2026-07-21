package domain_test

import (
	"account/internal/domain"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

const validPassword = "Str0ng!Pass"

func TestNewAccount(t *testing.T) {
	tests := []struct {
		name          string
		email         string
		password      string
		userName      string
		expectedError error
	}{
		{"Valid account", "test@example.com", validPassword, "John", nil},
		{"Invalid email", "bad-email", validPassword, "John", domain.ErrInvalidEmail},
		{"Invalid password", "test@example.com", "short", "John", domain.ErrPasswordTooShort},
		{"Invalid name", "test@example.com", validPassword, "J", domain.ErrInvalidNameLength},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			account, err := domain.NewAccount(tt.email, tt.password, tt.userName)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
				assert.Nil(t, account)
				return
			}

			assert.NoError(t, err)
			assert.Equal(t, tt.email, account.Email.String())
			assert.Equal(t, tt.userName, account.Name.String())
			assert.NotEmpty(t, account.ID.String())
			assert.False(t, account.CreatedAt.IsZero())
			assert.Equal(t, account.CreatedAt, account.UpdatedAt)
			assert.Nil(t, account.DeletedAt)
		})
	}
}

func TestAccountUpdateEmail(t *testing.T) {
	account, err := domain.NewAccount("test@example.com", validPassword, "John")
	assert.NoError(t, err)
	previous := account.UpdatedAt

	err = account.UpdateEmail("bad-email")
	assert.ErrorIs(t, err, domain.ErrInvalidEmail)
	assert.Equal(t, "test@example.com", account.Email.String())
	assert.Equal(t, previous, account.UpdatedAt)

	err = account.UpdateEmail("new@example.com")
	assert.NoError(t, err)
	assert.Equal(t, "new@example.com", account.Email.String())
	assert.True(t, account.UpdatedAt.After(previous) || account.UpdatedAt.Equal(previous))
}

func TestAccountUpdatePassword(t *testing.T) {
	account, err := domain.NewAccount("test@example.com", validPassword, "John")
	assert.NoError(t, err)

	err = account.UpdatePassword("short")
	assert.ErrorIs(t, err, domain.ErrPasswordTooShort)
	assert.True(t, account.Password.Compare(validPassword))

	err = account.UpdatePassword("N3w!Password")
	assert.NoError(t, err)
	assert.True(t, account.Password.Compare("N3w!Password"))
}

func TestAccountUpdateName(t *testing.T) {
	account, err := domain.NewAccount("test@example.com", validPassword, "John")
	assert.NoError(t, err)

	err = account.UpdateName("J")
	assert.ErrorIs(t, err, domain.ErrInvalidNameLength)
	assert.Equal(t, "John", account.Name.String())

	err = account.UpdateName("Jane")
	assert.NoError(t, err)
	assert.Equal(t, "Jane", account.Name.String())
}

func TestAccountIsDeleted(t *testing.T) {
	account, err := domain.NewAccount("test@example.com", validPassword, "John")
	assert.NoError(t, err)

	assert.False(t, account.IsDeleted())

	now := time.Now().UTC()
	account.DeletedAt = &now
	assert.True(t, account.IsDeleted())
}
