package domain

import (
	"errors"
	"regexp"
	"strings"
)

var (
	ErrEmailEmpty   = errors.New("email cannot be empty")
	ErrInvalidEmail = errors.New("invalid email format")
	emailRegex      = regexp.MustCompile(`^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,4}$`)
)

// Email is a Value Object for e-mail creation and validation.
type Email struct {
	value string
}

// NewEmail factory for the Email value object.
func NewEmail(address string) (Email, error) {
	address = strings.ToLower(strings.TrimSpace(address))
	if address == "" {
		return Email{}, ErrEmailEmpty
	}
	if !emailRegex.MatchString(address) {
		return Email{}, ErrInvalidEmail
	}
	return Email{value: address}, nil
}

func (e Email) String() string {
	return e.value
}
