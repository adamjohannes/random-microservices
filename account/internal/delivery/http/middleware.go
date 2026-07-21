package http

import (
	"account/internal/domain"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

var (
	authorizationHeaderRequired = "authorization header required"
	invalidAuthorizationFormat  = "invalid authorization format"
)

func AuthMiddleware(ts domain.TokenService) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": authorizationHeaderRequired})
			return
		}

		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": invalidAuthorizationFormat})
			return
		}

		accountID, err := ts.Validate(parts[1])
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
			return
		}

		c.Set("accountID", accountID.String())
		c.Next()
	}
}
