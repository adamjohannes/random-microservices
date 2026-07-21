package http

import (
	"account/internal/domain"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const testAccountID = "11111111-1111-1111-1111-111111111111"

func TestMain(m *testing.M) {
	gin.SetMode(gin.TestMode)
	m.Run()
}

// newTestRouter wires the handler behind a stub auth middleware that seeds a fixed accountID,
// so ownership checks are exercised without a real token.
func newTestRouter(svc AccountService, authAccountID string) *gin.Engine {
	router := gin.New()
	handler := NewAccountHandler(svc)
	stubAuth := func(c *gin.Context) {
		c.Set("accountID", authAccountID)
		c.Next()
	}
	RegisterRoutes(router, handler, stubAuth)
	return router
}

func doRequest(t *testing.T, router *gin.Engine, method, path string, body any) *httptest.ResponseRecorder {
	t.Helper()
	var reader *bytes.Reader
	if body != nil {
		raw, err := json.Marshal(body)
		require.NoError(t, err)
		reader = bytes.NewReader(raw)
	} else {
		reader = bytes.NewReader(nil)
	}
	req := httptest.NewRequest(method, path, reader)
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()
	router.ServeHTTP(rec, req)
	return rec
}

func activeAccount(t *testing.T) *domain.Account {
	t.Helper()
	account, err := domain.NewAccount("test@example.com", "StrongPass1!", "John Doe")
	require.NoError(t, err)
	return account
}

func TestRegisterHandler(t *testing.T) {
	tests := []struct {
		name           string
		body           any
		registerFn     func(ctx context.Context, email, password, name string) (*domain.Account, error)
		expectedStatus int
	}{
		{
			name: "Success",
			body: RegisterRequest{Email: "test@example.com", Password: "StrongPass1!", Name: "John Doe"},
			registerFn: func(ctx context.Context, email, password, name string) (*domain.Account, error) {
				return activeAccount(t), nil
			},
			expectedStatus: http.StatusCreated,
		},
		{
			name:           "Missing required field is bad request",
			body:           RegisterRequest{Email: "test@example.com"},
			expectedStatus: http.StatusBadRequest,
		},
		{
			name: "Email taken is conflict",
			body: RegisterRequest{Email: "test@example.com", Password: "StrongPass1!", Name: "John Doe"},
			registerFn: func(ctx context.Context, email, password, name string) (*domain.Account, error) {
				return nil, domain.ErrEmailTaken
			},
			expectedStatus: http.StatusConflict,
		},
		{
			name: "Validation sentinel is bad request",
			body: RegisterRequest{Email: "test@example.com", Password: "StrongPass1!", Name: "John Doe"},
			registerFn: func(ctx context.Context, email, password, name string) (*domain.Account, error) {
				return nil, domain.ErrPasswordTooWeak
			},
			expectedStatus: http.StatusBadRequest,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			svc := &mockAccountService{RegisterAccountFn: tt.registerFn}
			router := newTestRouter(svc, testAccountID)

			rec := doRequest(t, router, http.MethodPost, "/api/v1/accounts/", tt.body)

			assert.Equal(t, tt.expectedStatus, rec.Code)
		})
	}
}

func TestLoginHandler(t *testing.T) {
	t.Run("Success returns login response", func(t *testing.T) {
		account := activeAccount(t)
		svc := &mockAccountService{
			AuthenticateFn: func(ctx context.Context, email, password string) (*domain.Account, string, error) {
				return account, "signed-token", nil
			},
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodPost, "/api/v1/accounts/login",
			LoginRequest{Email: "test@example.com", Password: "StrongPass1!"})

		require.Equal(t, http.StatusOK, rec.Code)
		var resp LoginResponse
		require.NoError(t, json.Unmarshal(rec.Body.Bytes(), &resp))
		assert.Equal(t, "signed-token", resp.AccessToken)
		assert.Equal(t, "Bearer", resp.TokenType)
		assert.Equal(t, 86400, resp.ExpiresIn)
		assert.Equal(t, account.Email.String(), resp.Account.Email)
	})

	t.Run("Invalid credentials is unauthorized", func(t *testing.T) {
		svc := &mockAccountService{
			AuthenticateFn: func(ctx context.Context, email, password string) (*domain.Account, string, error) {
				return nil, "", domain.ErrInvalidCredentials
			},
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodPost, "/api/v1/accounts/login",
			LoginRequest{Email: "test@example.com", Password: "wrong"})

		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})

	t.Run("Bad payload is bad request", func(t *testing.T) {
		svc := &mockAccountService{}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodPost, "/api/v1/accounts/login",
			LoginRequest{Email: "test@example.com"})

		assert.Equal(t, http.StatusBadRequest, rec.Code)
	})
}

func TestGetByIdHandler(t *testing.T) {
	t.Run("Owner gets account", func(t *testing.T) {
		svc := &mockAccountService{
			GetActiveFn: func(ctx context.Context, id string) (*domain.Account, error) {
				return activeAccount(t), nil
			},
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodGet, "/api/v1/accounts/"+testAccountID, nil)

		assert.Equal(t, http.StatusOK, rec.Code)
	})

	t.Run("Non-owner is forbidden and service is not called", func(t *testing.T) {
		called := false
		svc := &mockAccountService{
			GetActiveFn: func(ctx context.Context, id string) (*domain.Account, error) {
				called = true
				return activeAccount(t), nil
			},
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodGet, "/api/v1/accounts/22222222-2222-2222-2222-222222222222", nil)

		assert.Equal(t, http.StatusForbidden, rec.Code)
		assert.False(t, called)
	})

	t.Run("Not found", func(t *testing.T) {
		svc := &mockAccountService{
			GetActiveFn: func(ctx context.Context, id string) (*domain.Account, error) {
				return nil, domain.ErrAccountNotFound
			},
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodGet, "/api/v1/accounts/"+testAccountID, nil)

		assert.Equal(t, http.StatusNotFound, rec.Code)
	})

	t.Run("Unexpected error is internal server error", func(t *testing.T) {
		svc := &mockAccountService{
			GetActiveFn: func(ctx context.Context, id string) (*domain.Account, error) {
				return nil, errors.New("boom")
			},
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodGet, "/api/v1/accounts/"+testAccountID, nil)

		assert.Equal(t, http.StatusInternalServerError, rec.Code)
	})
}

func TestUpdateHandler(t *testing.T) {
	t.Run("Success", func(t *testing.T) {
		svc := &mockAccountService{
			UpdateAccountFn: func(ctx context.Context, id, name, email string) error { return nil },
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodPut, "/api/v1/accounts/"+testAccountID,
			UpdateRequest{Name: "Jane Doe", Email: "jane@example.com"})

		assert.Equal(t, http.StatusNoContent, rec.Code)
	})

	t.Run("Non-owner is forbidden", func(t *testing.T) {
		svc := &mockAccountService{}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodPut, "/api/v1/accounts/22222222-2222-2222-2222-222222222222",
			UpdateRequest{Name: "Jane Doe", Email: "jane@example.com"})

		assert.Equal(t, http.StatusForbidden, rec.Code)
	})
}

func TestChangePasswordHandler(t *testing.T) {
	t.Run("Success", func(t *testing.T) {
		svc := &mockAccountService{
			ChangePasswordFn: func(ctx context.Context, id, oldPassword, newPassword string) error { return nil },
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodPatch, "/api/v1/accounts/"+testAccountID+"/password",
			ChangePasswordRequest{OldPassword: "StrongPass1!", NewPassword: "N3w!Password"})

		assert.Equal(t, http.StatusNoContent, rec.Code)
	})

	t.Run("Wrong old password is unauthorized", func(t *testing.T) {
		svc := &mockAccountService{
			ChangePasswordFn: func(ctx context.Context, id, oldPassword, newPassword string) error {
				return domain.ErrInvalidCredentials
			},
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodPatch, "/api/v1/accounts/"+testAccountID+"/password",
			ChangePasswordRequest{OldPassword: "wrong", NewPassword: "N3w!Password"})

		assert.Equal(t, http.StatusUnauthorized, rec.Code)
	})
}

func TestDeleteHandler(t *testing.T) {
	t.Run("Success", func(t *testing.T) {
		svc := &mockAccountService{
			RemoveAccountFn: func(ctx context.Context, id string) error { return nil },
		}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodDelete, "/api/v1/accounts/"+testAccountID, nil)

		assert.Equal(t, http.StatusNoContent, rec.Code)
	})

	t.Run("Non-owner is forbidden", func(t *testing.T) {
		svc := &mockAccountService{}
		router := newTestRouter(svc, testAccountID)

		rec := doRequest(t, router, http.MethodDelete, "/api/v1/accounts/22222222-2222-2222-2222-222222222222", nil)

		assert.Equal(t, http.StatusForbidden, rec.Code)
	})
}
