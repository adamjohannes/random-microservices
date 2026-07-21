package domain

import (
	"errors"
	"time"
)

var (
	ErrAccountNotFound    = errors.New("account not found")
	ErrEmailTaken         = errors.New("email is already in use")
	ErrInvalidCredentials = errors.New("invalid email or password")
)

// Account represents a user account inside the system.
type Account struct {
	ID        AccountID
	Email     Email
	Password  Password
	Name      Name
	CreatedAt time.Time
	UpdatedAt time.Time
	DeletedAt *time.Time
}

// BuildAccount rehydrates an Account from database records.
func BuildAccount(id AccountID, email string, hash string, name string, createdAt, updatedAt time.Time, deletedAt *time.Time) *Account {
	return &Account{
		ID:        id,
		Email:     Email{value: email},
		Password:  LoadPassword(hash),
		Name:      Name{value: name},
		CreatedAt: createdAt,
		UpdatedAt: updatedAt,
		DeletedAt: deletedAt,
	}
}

// NewAccount factory for the Account domain entity.
func NewAccount(emailAddress, plainTextPassword, userName string) (*Account, error) {
	email, err := NewEmail(emailAddress)
	if err != nil {
		return nil, err
	}

	password, err := NewPassword(plainTextPassword)
	if err != nil {
		return nil, err
	}

	name, err := NewName(userName)
	if err != nil {
		return nil, err
	}

	now := time.Now().UTC()
	return &Account{
		ID:        NewAccountID(),
		Email:     email,
		Password:  password,
		Name:      name,
		CreatedAt: now,
		UpdatedAt: now,
		DeletedAt: nil,
	}, nil
}

// UpdateEmail replaces the Account's e-mail if the new address is valid.
func (a *Account) UpdateEmail(newAddress string) error {
	newEmail, err := NewEmail(newAddress)
	if err != nil {
		return err
	}

	a.Email = newEmail
	a.UpdatedAt = time.Now()
	return nil
}

// UpdatePassword replaces the Account's password if the new value is valid.
func (a *Account) UpdatePassword(newValue string) error {
	newPassword, err := NewPassword(newValue)
	if err != nil {
		return err
	}

	a.Password = newPassword
	a.UpdatedAt = time.Now()
	return nil
}

// UpdateName replaces the Account's name if the new value is valid.
func (a *Account) UpdateName(newValue string) error {
	newName, err := NewName(newValue)
	if err != nil {
		return err
	}

	a.Name = newName
	a.UpdatedAt = time.Now()
	return nil
}

// IsDeleted checks if the user account has been soft deleted.
func (a *Account) IsDeleted() bool {
	return a.DeletedAt != nil
}
