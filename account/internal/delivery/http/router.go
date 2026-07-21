package http

import "github.com/gin-gonic/gin"

func RegisterRoutes(router *gin.Engine, handler *AccountHandler, authMiddleware gin.HandlerFunc) {
	api := router.Group("/api/v1/accounts")
	{
		api.POST("/", handler.Register)
		api.POST("/login", handler.Login)

		// Protected routs
		protected := api.Group("/")
		protected.Use(authMiddleware)
		{
			protected.GET("/:id", handler.GetById)
			protected.PUT("/:id", handler.Update)
			protected.PATCH("/:id/password", handler.ChangePassword)
			protected.DELETE("/:id", handler.Delete)
		}
	}
}
