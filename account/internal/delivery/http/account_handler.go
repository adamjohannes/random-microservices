package http

import (
	"account/internal/domain"
	"account/internal/usecase"
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"
)

type AccountHandler struct {
	service *usecase.AccountUsecase
}

func NewAccounHandler(service *usecase.AccountUsecase) *AccountHandler {
	return &AccountHandler{service: service}
}

// Register creates a new account.
func (h *AccountHandler) Register(c *gin.Context) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request payload"})
		return
	}

	account, err := h.service.RegisterAccount(c.Request.Context(), req.Email, req.Password, req.Name)
	if err != nil {
		h.handleError(c, err)
		return
	}

	c.JSON(http.StatusCreated, toAccountResponse(account))
}

// GetById fetches an active Account using the ID in the URL parameter.
func (h *AccountHandler) GetById(c *gin.Context) {
	id := c.Param("id")

	account, err := h.service.GetActiveAccount(c.Request.Context(), id)
	if err != nil {
		h.handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, toAccountResponse(account))
}

// Delete soft deletes an Account.
func (h *AccountHandler) Delete(c *gin.Context) {
	id := c.Param("id")

	err := h.service.RemoveAccount(c.Request.Context(), id)
	if err != nil {
		h.handleError(c, err)
		return
	}

	c.Status(http.StatusNoContent)
}

// Login authenticates a user.
func (h *AccountHandler) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request payload"})
		return
	}

	account, err := h.service.Authenticate(c.Request.Context(), req.Email, req.Password)
	if err != nil {
		h.handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, toAccountResponse(account))
}

// Update changes an Account name and e-mail address.
func (h *AccountHandler) Update(c *gin.Context) {
	id := c.Param("id")
	var req UpdateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request payload"})
		return
	}

	err := h.service.UpdateAccount(c.Request.Context(), id, req.Name, req.Email)
	if err != nil {
		h.handleError(c, err)
		return
	}

	c.Status(http.StatusNoContent)
}

// ChangePassword changes an Account password.
func (h *AccountHandler) ChangePassword(c *gin.Context) {
	id := c.Param("id")
	var req ChangePasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request payload"})
		return
	}

	err := h.service.ChangePassword(c.Request.Context(), id, req.OldPassword, req.NewPassword)
	if err != nil {
		h.handleError(c, err)
		return
	}

	c.Status(http.StatusNoContent)
}

// Maps an Account to an AccountResponse.
func toAccountResponse(account *domain.Account) AccountResponse {
	return AccountResponse{
		ID:        account.ID.String(),
		Email:     account.Email.String(),
		Name:      account.Name.String(),
		CreatedAt: account.CreatedAt,
		UpdatedAt: account.UpdatedAt,
	}
}

func (h *AccountHandler) handleError(c *gin.Context, err error) {
	switch {
	case errors.Is(err, domain.ErrAccountNotFound):
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
	case errors.Is(err, domain.ErrEmailTaken):
		c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
	case errors.Is(err, domain.ErrInvalidAccountID) ||
		errors.Is(err, domain.ErrEmailEmpty) ||
		errors.Is(err, domain.ErrInvalidEmail) ||
		errors.Is(err, domain.ErrInvalidNameLenght) ||
		errors.Is(err, domain.ErrInvalidNameCharacter) ||
		errors.Is(err, domain.ErrPasswordTooShort) ||
		errors.Is(err, domain.ErrPasswordTooWeak):
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
	default:
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
	}
}
