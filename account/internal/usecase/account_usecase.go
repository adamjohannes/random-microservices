package usecase

import (
	"account/internal/domain"
	"context"
	"encoding/json"
	"errors"
	"time"
)

type AccountUsecase struct {
	repo           domain.AccountRepository
	tokenService   domain.TokenService
	eventPublisher domain.EventPublisher
}

func NewAccountUsecase(repo domain.AccountRepository, tokenService domain.TokenService, eventPublisher domain.EventPublisher) *AccountUsecase {
	return &AccountUsecase{repo: repo, tokenService: tokenService, eventPublisher: eventPublisher}
}

// Authenticate verifies credentials and returns the account if valid
func (u *AccountUsecase) Authenticate(ctx context.Context, email, plainTextPassword string) (*domain.Account, string, error) {
	account, err := u.repo.GetByEmail(ctx, email)
	if err != nil {
		if errors.Is(err, domain.ErrAccountNotFound) {
			return nil, "", domain.ErrInvalidCredentials
		}
		return nil, "", err
	}

	if account.IsDeleted() || !account.Password.Compare(plainTextPassword) {
		return nil, "", domain.ErrInvalidCredentials
	}

	token, err := u.tokenService.Generate(account.ID)
	if err != nil {
		return nil, "", err
	}

	return account, token, nil
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

	u.publishUserRegistered(ctx, account)

	return account, nil
}

func (u *AccountUsecase) publishUserRegistered(ctx context.Context, account *domain.Account) {
	payload, err := json.Marshal(struct {
		EventType  string    `json:"event_type"`
		OccurredAt time.Time `json:"occurred_at"`
		AccountID  string    `json:"account_id"`
		Name       string    `json:"name"`
		Email      string    `json:"email"`
	}{
		EventType:  "account.user_registered",
		OccurredAt: time.Now().UTC(),
		AccountID:  account.ID.String(),
		Name:       account.Name.String(),
		Email:      account.Email.String(),
	})
	if err != nil {
		return
	}
	_ = u.eventPublisher.Publish(ctx, "account.user_registered", payload)
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
		return domain.ErrInvalidCredentials
	}

	if err := account.UpdatePassword(newPassword); err != nil {
		return err
	}

	return u.repo.Update(ctx, account)
}
