package http

import (
	"account/internal/domain"
	"context"
)

type mockAccountService struct {
	RegisterAccountFn func(ctx context.Context, email, password, name string) (*domain.Account, error)
	AuthenticateFn    func(ctx context.Context, email, password string) (*domain.Account, string, error)
	GetActiveFn       func(ctx context.Context, id string) (*domain.Account, error)
	UpdateAccountFn   func(ctx context.Context, id, name, email string) error
	ChangePasswordFn  func(ctx context.Context, id, oldPassword, newPassword string) error
	RemoveAccountFn   func(ctx context.Context, id string) error
}

func (m *mockAccountService) RegisterAccount(ctx context.Context, email, password, name string) (*domain.Account, error) {
	return m.RegisterAccountFn(ctx, email, password, name)
}

func (m *mockAccountService) Authenticate(ctx context.Context, email, password string) (*domain.Account, string, error) {
	return m.AuthenticateFn(ctx, email, password)
}

func (m *mockAccountService) GetActiveAccount(ctx context.Context, id string) (*domain.Account, error) {
	return m.GetActiveFn(ctx, id)
}

func (m *mockAccountService) UpdateAccount(ctx context.Context, id, name, email string) error {
	return m.UpdateAccountFn(ctx, id, name, email)
}

func (m *mockAccountService) ChangePassword(ctx context.Context, id, oldPassword, newPassword string) error {
	return m.ChangePasswordFn(ctx, id, oldPassword, newPassword)
}

func (m *mockAccountService) RemoveAccount(ctx context.Context, id string) error {
	return m.RemoveAccountFn(ctx, id)
}

type mockTokenService struct {
	GenerateFn func(id domain.AccountID) (string, error)
	ValidateFn func(token string) (domain.AccountID, error)
}

func (m *mockTokenService) Generate(id domain.AccountID) (string, error) {
	return m.GenerateFn(id)
}

func (m *mockTokenService) Validate(token string) (domain.AccountID, error) {
	return m.ValidateFn(token)
}
