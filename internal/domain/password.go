package domain

import (
	"errors"
	"regexp"
	"strings"

	"golang.org/x/crypto/bcrypt"
)

var (
	ErrPasswordTooShort = errors.New("password must be at least 8 characters long")
	ErrPasswordTooWeak  = errors.New("password must contain at least one upper and lower case characters, a special character and a number")
	passwordRegex       = regexp.MustCompile(`^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$`)
)

// Password is a Value Object for password creation and validation.
type Password struct {
	hash string
}

// NewPassword factory for the password value object.
func NewPassword(plainText string) (Password, error) {
	plainText = strings.TrimSpace(plainText)
	if len(plainText) < 8 {
		return Password{}, ErrPasswordTooShort
	}
	if !passwordRegex.MatchString(plainText) {
		return Password{}, ErrPasswordTooWeak
	}

	hashBytes, err := bcrypt.GenerateFromPassword([]byte(plainText), bcrypt.DefaultCost)
	if err != nil {
		return Password{}, err
	}

	return Password{hash: string(hashBytes)}, nil
}

// LoadPassword rehydrates the value object from the database without re-hashing it.
func LoadPassword(existingHash string) Password {
	return Password{hash: existingHash}
}

// Compare checks if the given plain text password matches the hash.
func (p Password) Compare(plainText string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(p.hash), []byte(plainText))
	return err == nil
}

// Hash returns the hashed string to be saved to the database.
func (p Password) Hash() string {
	return p.hash
}
