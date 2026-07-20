package usecase

import (
	"account/internal/domain"
	"context"
)

type AccountUsecase struct {
	repo domain.AccountRepository
}

func NewAccountUsecase(repo domain.AccountRepository) *AccountUsecase {
	return &AccountUsecase{repo: repo}
}

// Authenticate verifies credentials and returns the account if valid
func (u *AccountUsecase) Authenticate(ctx context.Context, email, plainTextPassword string) (*domain.Account, error) {
	account, err := u.repo.GetByEmail(ctx, email)
	if err != nil {
		return nil, domain.ErrAccountNotFound
	}

	// Users shouldn't be able to authenticate into deleted accounts
	if account.IsDeleted() {
		return nil, domain.ErrAccountNotFound
	}

	if !account.Password.Compare(plainTextPassword) {
		return nil, domain.ErrAccountNotFound // keep error generic for security
	}

	return account, nil
}

// RegisterAccount handles the creation of a new user account.
func (u *AccountUsecase) RegisterAccount(ctx context.Context, email, password, name string) (*domain.Account, error) {
	account, err := domain.NewAccount(email, password, name)
	if err != nil {
		return nil, err
	}

	if err := u.repo.Create(ctx, account); err != nil {
		return nil, err
	}

	return account, nil
}

// GetActiveAccount retrieves an Account active account from the database and fails if it has been soft deleted.
func (u *AccountUsecase) GetActiveAccount(ctx context.Context, id string) (*domain.Account, error) {
	accountID, err := domain.BuildAccountID(id)
	if err != nil {
		return nil, err
	}

	account, err := u.repo.GetByID(ctx, accountID)
	if err != nil {
		return nil, err
	}

	// Do not return soft-deleted accounts
	if account.IsDeleted() {
		return nil, domain.ErrAccountNotFound
	}

	return account, nil
}

// RemoveAccount soft deletes an Account.
func (u *AccountUsecase) RemoveAccount(ctx context.Context, id string) error {
	accountID, err := domain.BuildAccountID(id)
	if err != nil {
		return err
	}

	return u.repo.SoftDelete(ctx, accountID)
}

func (u *AccountUsecase) UpdateAccount(ctx context.Context, id, newName, newEmail string) error {
	accountID, err := domain.BuildAccountID(id)
	if err != nil {
		return err
	}

	account, err := u.repo.GetByID(ctx, accountID)
	if err != nil {
		return err
	}

	if account.IsDeleted() {
		return domain.ErrAccountNotFound
	}

	isModified := false

	if newName != account.Name.String() {
		if err := account.UpdateName(newName); err != nil {
			return err
		}
		isModified = true
	}

	if newEmail != account.Email.String() {
		if err := account.UpdateEmail(newEmail); err != nil {
			return err
		}
		isModified = true
	}

	// Only call the database if something actually changed
	if isModified {
		return u.repo.Update(ctx, account)
	}

	return nil
}

func (u *AccountUsecase) ChangePassword(ctx context.Context, id, oldPassword, newPassword string) error {
	account, err := u.GetActiveAccount(ctx, id)
	if err != nil {
		return err
	}

	if !account.Password.Compare(oldPassword) {
		return domain.ErrAccountNotFound // keep error generic for security
	}

	if err := account.UpdatePassword(newPassword); err != nil {
		return err
	}

	return u.repo.Update(ctx, account)
}
