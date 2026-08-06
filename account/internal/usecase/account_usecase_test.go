package usecase_test

import (
	"account/internal/adapter/messaging/rabbitmq"
	"account/internal/domain"
	"account/internal/usecase"
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	validEmail    = "test@example.com"
	validPassword = "StrongPass1!"
	validName     = "John Doe"
)

// newActiveAccount builds a persisted-looking account for repo mocks to hand back.
func newActiveAccount(t *testing.T) *domain.Account {
	t.Helper()
	account, err := domain.NewAccount(validEmail, validPassword, validName)
	require.NoError(t, err)
	return account
}

func TestRegisterAccount(t *testing.T) {
	tests := []struct {
		name          string
		email         string
		password      string
		userName      string
		createFn      func(ctx context.Context, account *domain.Account) error
		expectedError error
		expectCreate  bool
	}{
		{
			name:         "Success",
			email:        validEmail,
			password:     validPassword,
			userName:     validName,
			createFn:     func(ctx context.Context, account *domain.Account) error { return nil },
			expectCreate: true,
		},
		{
			name:          "Invalid email rejected before repo",
			email:         "bad-email",
			password:      validPassword,
			userName:      validName,
			expectedError: domain.ErrInvalidEmail,
			expectCreate:  false,
		},
		{
			name:          "Email already taken",
			email:         validEmail,
			password:      validPassword,
			userName:      validName,
			createFn:      func(ctx context.Context, account *domain.Account) error { return domain.ErrEmailTaken },
			expectedError: domain.ErrEmailTaken,
			expectCreate:  true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			createCalled := false
			repo := &mockAccountRepo{
				CreateFn: func(ctx context.Context, account *domain.Account) error {
					createCalled = true
					return tt.createFn(ctx, account)
				},
			}
			uc := usecase.NewAccountUsecase(repo, &mockTokenService{}, rabbitmq.NoopPublisher{})

			account, err := uc.RegisterAccount(context.Background(), tt.email, tt.password, tt.userName)

			assert.Equal(t, tt.expectCreate, createCalled)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
				assert.Nil(t, account)
				return
			}

			require.NoError(t, err)
			require.NotNil(t, account)
			assert.Equal(t, tt.email, account.Email.String())
		})
	}
}

func TestAuthenticate(t *testing.T) {
	dbErr := errors.New("connection refused")

	tests := []struct {
		name          string
		getByEmailFn  func(ctx context.Context, email string) (*domain.Account, error)
		generateFn    func(id domain.AccountID) (string, error)
		password      string
		expectedToken string
		expectedError error
	}{
		{
			name: "Success returns account and token",
			getByEmailFn: func(ctx context.Context, email string) (*domain.Account, error) {
				return newActiveAccount(t), nil
			},
			generateFn:    func(id domain.AccountID) (string, error) { return "signed-token", nil },
			password:      validPassword,
			expectedToken: "signed-token",
		},
		{
			name: "Not found maps to invalid credentials",
			getByEmailFn: func(ctx context.Context, email string) (*domain.Account, error) {
				return nil, domain.ErrAccountNotFound
			},
			password:      validPassword,
			expectedError: domain.ErrInvalidCredentials,
		},
		{
			name: "Real repo error propagates (P0.2 regression guard)",
			getByEmailFn: func(ctx context.Context, email string) (*domain.Account, error) {
				return nil, dbErr
			},
			password:      validPassword,
			expectedError: dbErr,
		},
		{
			name: "Wrong password is invalid credentials",
			getByEmailFn: func(ctx context.Context, email string) (*domain.Account, error) {
				return newActiveAccount(t), nil
			},
			password:      "WrongPass1!",
			expectedError: domain.ErrInvalidCredentials,
		},
		{
			name: "Soft-deleted account is invalid credentials",
			getByEmailFn: func(ctx context.Context, email string) (*domain.Account, error) {
				account := newActiveAccount(t)
				now := account.CreatedAt
				account.DeletedAt = &now
				return account, nil
			},
			password:      validPassword,
			expectedError: domain.ErrInvalidCredentials,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			repo := &mockAccountRepo{GetByEmailFn: tt.getByEmailFn}
			ts := &mockTokenService{GenerateFn: tt.generateFn}
			uc := usecase.NewAccountUsecase(repo, ts, rabbitmq.NoopPublisher{})

			account, token, err := uc.Authenticate(context.Background(), validEmail, tt.password)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
				assert.Nil(t, account)
				assert.Empty(t, token)
				return
			}

			require.NoError(t, err)
			require.NotNil(t, account)
			assert.Equal(t, tt.expectedToken, token)
		})
	}
}

func TestGetActiveAccount(t *testing.T) {
	tests := []struct {
		name          string
		id            string
		getByIDFn     func(ctx context.Context, id domain.AccountID) (*domain.Account, error)
		expectedError error
	}{
		{
			name:          "Malformed ID rejected before repo",
			id:            "not-a-uuid",
			expectedError: domain.ErrInvalidAccountID,
		},
		{
			name: "Not found",
			id:   domain.NewAccountID().String(),
			getByIDFn: func(ctx context.Context, id domain.AccountID) (*domain.Account, error) {
				return nil, domain.ErrAccountNotFound
			},
			expectedError: domain.ErrAccountNotFound,
		},
		{
			name: "Soft-deleted account is treated as not found",
			id:   domain.NewAccountID().String(),
			getByIDFn: func(ctx context.Context, id domain.AccountID) (*domain.Account, error) {
				account := newActiveAccount(t)
				now := account.CreatedAt
				account.DeletedAt = &now
				return account, nil
			},
			expectedError: domain.ErrAccountNotFound,
		},
		{
			name: "Success",
			id:   domain.NewAccountID().String(),
			getByIDFn: func(ctx context.Context, id domain.AccountID) (*domain.Account, error) {
				return newActiveAccount(t), nil
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			repo := &mockAccountRepo{GetByIDFn: tt.getByIDFn}
			uc := usecase.NewAccountUsecase(repo, &mockTokenService{}, rabbitmq.NoopPublisher{})

			account, err := uc.GetActiveAccount(context.Background(), tt.id)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
				assert.Nil(t, account)
				return
			}

			require.NoError(t, err)
			require.NotNil(t, account)
		})
	}
}

func TestUpdateAccount(t *testing.T) {
	tests := []struct {
		name          string
		id            string
		newName       string
		newEmail      string
		expectUpdate  bool
		expectedError error
	}{
		{
			name:         "No-op when values unchanged does not call repo.Update",
			id:           domain.NewAccountID().String(),
			newName:      validName,
			newEmail:     validEmail,
			expectUpdate: false,
		},
		{
			name:         "Partial update of name only",
			id:           domain.NewAccountID().String(),
			newName:      "Jane Doe",
			newEmail:     validEmail,
			expectUpdate: true,
		},
		{
			name:          "Invalid new email surfaces validation error",
			id:            domain.NewAccountID().String(),
			newName:       validName,
			newEmail:      "bad-email",
			expectUpdate:  false,
			expectedError: domain.ErrInvalidEmail,
		},
		{
			name:          "Malformed ID rejected before repo",
			id:            "not-a-uuid",
			newName:       validName,
			newEmail:      validEmail,
			expectUpdate:  false,
			expectedError: domain.ErrInvalidAccountID,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			updateCalled := false
			repo := &mockAccountRepo{
				GetByIDFn: func(ctx context.Context, id domain.AccountID) (*domain.Account, error) {
					return newActiveAccount(t), nil
				},
				UpdateFn: func(ctx context.Context, account *domain.Account) error {
					updateCalled = true
					return nil
				},
			}
			uc := usecase.NewAccountUsecase(repo, &mockTokenService{}, rabbitmq.NoopPublisher{})

			err := uc.UpdateAccount(context.Background(), tt.id, tt.newName, tt.newEmail)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
			} else {
				require.NoError(t, err)
			}
			assert.Equal(t, tt.expectUpdate, updateCalled)
		})
	}
}

func TestChangePassword(t *testing.T) {
	tests := []struct {
		name          string
		oldPassword   string
		newPassword   string
		expectUpdate  bool
		expectedError error
	}{
		{
			name:         "Success",
			oldPassword:  validPassword,
			newPassword:  "N3w!Password",
			expectUpdate: true,
		},
		{
			name:          "Wrong old password is invalid credentials",
			oldPassword:   "WrongPass1!",
			newPassword:   "N3w!Password",
			expectUpdate:  false,
			expectedError: domain.ErrInvalidCredentials,
		},
		{
			name:          "Weak new password surfaces validation error",
			oldPassword:   validPassword,
			newPassword:   "weak",
			expectUpdate:  false,
			expectedError: domain.ErrPasswordTooShort,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			updateCalled := false
			repo := &mockAccountRepo{
				GetByIDFn: func(ctx context.Context, id domain.AccountID) (*domain.Account, error) {
					return newActiveAccount(t), nil
				},
				UpdateFn: func(ctx context.Context, account *domain.Account) error {
					updateCalled = true
					return nil
				},
			}
			uc := usecase.NewAccountUsecase(repo, &mockTokenService{}, rabbitmq.NoopPublisher{})

			err := uc.ChangePassword(context.Background(), domain.NewAccountID().String(), tt.oldPassword, tt.newPassword)

			if tt.expectedError != nil {
				assert.ErrorIs(t, err, tt.expectedError)
			} else {
				require.NoError(t, err)
			}
			assert.Equal(t, tt.expectUpdate, updateCalled)
		})
	}
}
