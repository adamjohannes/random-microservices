package usecase_test

import (
	"account/internal/domain"
	"context"
)

type mockAccountRepo struct {
	CreateFn     func(ctx context.Context, account *domain.Account) error
	GetByIDFn    func(ctx context.Context, id domain.AccountID) (*domain.Account, error)
	GetByEmailFn func(ctx context.Context, email string) (*domain.Account, error)
	UpdateFn     func(ctx context.Context, account *domain.Account) error
	SoftDeleteFn func(ctx context.Context, id domain.AccountID) error
}

func (m *mockAccountRepo) Create(ctx context.Context, account *domain.Account) error {
	return m.CreateFn(ctx, account)
}

func (m *mockAccountRepo) GetByID(ctx context.Context, id domain.AccountID) (*domain.Account, error) {
	return m.GetByIDFn(ctx, id)
}

func (m *mockAccountRepo) GetByEmail(ctx context.Context, email string) (*domain.Account, error) {
	return m.GetByEmailFn(ctx, email)
}

func (m *mockAccountRepo) Update(ctx context.Context, account *domain.Account) error {
	return m.UpdateFn(ctx, account)
}

func (m *mockAccountRepo) SoftDelete(ctx context.Context, id domain.AccountID) error {
	return m.SoftDeleteFn(ctx, id)
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
