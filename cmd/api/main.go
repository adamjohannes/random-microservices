package main

import (
	"account/internal/adapter/storage/postgres"
	"account/internal/config"
	"account/internal/delivery/http"
	"account/internal/usecase"
	"fmt"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
	gormpostgres "gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	// Load configs
	cfg, err := config.Load()
	if err != nil {
		panic(err)
	}

	// Initialize logger
	logger, err := zap.NewProduction(cfg.LoggerOptions...)
	if err != nil {
		panic(err)
	}
	defer logger.Sync()

	logger.Info("Starting Account microservice...")

	// Connect to database
	db, err := gorm.Open(gormpostgres.Open(cfg.DatabaseUrl), &gorm.Config{})
	if err != nil {
		logger.Fatal("Failed to connect to the database", zap.Error(err))
	}
	logger.Info("Successfully conected to the dabase")

	// TODO: An auto-migrate function needs to be added here

	accountRepo := postgres.NewAccountRepository(db)
	accountService := usecase.NewAccountUsecase(accountRepo)
	accountHandler := http.NewAccounHandler(accountService)

	// Setup Gin router and delivery layer
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}
	router := gin.Default()

	http.RegisterRoutes(router, accountHandler)

	// Start the HTTP server
	addr := fmt.Sprintf(":%s", cfg.Port)
	logger.Info("Server listening", zap.String("port", addr))

	if err := router.Run(addr); err != nil {
		logger.Fatal("Server failed to start", zap.Error(err))
	}
}
