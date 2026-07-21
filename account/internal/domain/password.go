package domain

import (
	"errors"
	"strings"
	"unicode"

	"golang.org/x/crypto/bcrypt"
)

var (
	ErrPasswordTooShort = errors.New("password must be at least 8 characters long")
	ErrPasswordTooWeak  = errors.New("password must contain at least one upper and lower case characters, a special character and a number")
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
	if !isPasswordStrong(plainText) {
		return Password{}, ErrPasswordTooWeak
	}

	hashBytes, err := bcrypt.GenerateFromPassword([]byte(plainText), bcrypt.DefaultCost)
	if err != nil {
		return Password{}, err
	}

	return Password{hash: string(hashBytes)}, nil
}

func isPasswordStrong(s string) bool {
	var hasLower, hasUpper, hasNumber, hasSpecial bool

	for _, char := range s {
		switch {
		case unicode.IsLower(char):
			hasLower = true
		case unicode.IsUpper(char):
			hasUpper = true
		case unicode.IsDigit(char):
			hasNumber = true
		case unicode.IsPunct(char) || unicode.IsSymbol(char):
			hasSpecial = true
		}
	}

	return hasLower && hasUpper && hasNumber && hasSpecial
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
