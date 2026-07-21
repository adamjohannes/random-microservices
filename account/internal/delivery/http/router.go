package http

import "github.com/gin-gonic/gin"

func RegisterRoutes(router *gin.Engine, handler *AccountHandler) {
	api := router.Group("/api/v1/accounts")
	{
		api.POST("/", handler.Register)
		api.POST("/login", handler.Login)

		// TODO: These need to be protected by an auth middleware
		api.GET("/:id", handler.GetById)
		api.PUT("/:id", handler.Update)
		api.PATCH("/:id/password", handler.ChangePassword)
		api.DELETE("/:id", handler.Delete)
	}
}
