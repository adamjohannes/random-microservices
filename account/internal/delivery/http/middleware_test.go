package http

import (
	"account/internal/domain"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func newMiddlewareRouter(ts domain.TokenService) *gin.Engine {
	router := gin.New()
	router.GET("/protected", AuthMiddleware(ts), func(c *gin.Context) {
		c.String(http.StatusOK, c.GetString("accountID"))
	})
	return router
}

func TestAuthMiddleware(t *testing.T) {
	validID := domain.NewAccountID()

	tests := []struct {
		name           string
		header         string
		setHeader      bool
		validateFn     func(token string) (domain.AccountID, error)
		expectedStatus int
		expectedBody   string
	}{
		{
			name:           "Missing header",
			setHeader:      false,
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:           "Wrong scheme",
			header:         "Basic abc",
			setHeader:      true,
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:           "Single token part",
			header:         "abc",
			setHeader:      true,
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:      "Invalid token",
			header:    "Bearer bad-token",
			setHeader: true,
			validateFn: func(token string) (domain.AccountID, error) {
				return domain.AccountID{}, domain.ErrInvalidToken
			},
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:      "Expired token",
			header:    "Bearer expired",
			setHeader: true,
			validateFn: func(token string) (domain.AccountID, error) {
				return domain.AccountID{}, domain.ErrExpiredToken
			},
			expectedStatus: http.StatusUnauthorized,
		},
		{
			name:      "Valid token sets accountID downstream",
			header:    "Bearer good",
			setHeader: true,
			validateFn: func(token string) (domain.AccountID, error) {
				return validID, nil
			},
			expectedStatus: http.StatusOK,
			expectedBody:   validID.String(),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ts := &mockTokenService{ValidateFn: tt.validateFn}
			router := newMiddlewareRouter(ts)

			req := httptest.NewRequest(http.MethodGet, "/protected", nil)
			if tt.setHeader {
				req.Header.Set("Authorization", tt.header)
			}
			rec := httptest.NewRecorder()
			router.ServeHTTP(rec, req)

			assert.Equal(t, tt.expectedStatus, rec.Code)
			if tt.expectedBody != "" {
				assert.Equal(t, tt.expectedBody, rec.Body.String())
			}
		})
	}
}
