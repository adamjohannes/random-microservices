package domain

import "context"

type AccountRepository interface {
	Create(ctx context.Context, account *Account) error
	GetByID(ctx context.Context, id AccountID) (*Account, error)
	GetByEmail(ctx context.Context, email string) (*Account, error)
	Update(ctx context.Context, account *Account) error
	SoftDelete(ctx context.Context, id AccountID) error
}
