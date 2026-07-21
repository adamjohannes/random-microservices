package domain

import (
	"errors"
	"regexp"
	"strings"
)

var (
	ErrInvalidNameLenght    = errors.New("name must be between 2 and 50 characters")
	ErrInvalidNameCharacter = errors.New("name must contain only alphabetical characters")
	nameRegex               = regexp.MustCompile(`^[a-zA-Z\s]+$`)
)

// Name is a Value Object for name creation and validation.
type Name struct {
	value string
}

// NewName factory for the Name value object.
func NewName(name string) (Name, error) {
	name = strings.TrimSpace(name)
	if len(name) < 2 || len(name) > 50 {
		return Name{}, ErrInvalidNameLenght
	}
	if !nameRegex.MatchString(name) {
		return Name{}, ErrInvalidNameCharacter
	}
	return Name{value: name}, nil
}

func (n Name) String() string {
	return n.value
}
