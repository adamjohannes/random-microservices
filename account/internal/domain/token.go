package domain

import "errors"

var (
	ErrInvalidToken = errors.New("invalid or malformed token")
	ErrExpiredToken = errors.New("token has expired")
	ErrForbidden    = errors.New("access forbidden")
)

type TokenService interface {
	Generate(id AccountID) (string, error)
	Validate(token string) (AccountID, error)
}
