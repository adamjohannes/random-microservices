package main

import (
	"account/internal/adapter/messaging/rabbitmq"
	"account/internal/adapter/storage/postgres"
	"account/internal/auth"
	"account/internal/config"
	"account/internal/delivery/http"
	"account/internal/domain"
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
	db, err := gorm.Open(gormpostgres.Open(cfg.DatabaseUrl), &gorm.Config{TranslateError: true})
	if err != nil {
		logger.Fatal("Failed to connect to the database", zap.Error(err))
	}
	logger.Info("Successfully conected to the dabase")

	if err := postgres.Migrate(db); err != nil {
		logger.Fatal("Failed to run database migrations", zap.Error(err))
	}

	accountRepo := postgres.NewAccountRepository(db)
	jwtService := auth.NewJWTService(cfg.JWTSecret, cfg.JWTExpiry)

	var eventPublisher domain.EventPublisher
	amqpPublisher, err := rabbitmq.NewPublisher(cfg.AmqpHost, cfg.AmqpUser, cfg.AmqpPass)
	if err != nil {
		logger.Warn("RabbitMQ unavailable, events will not be published", zap.Error(err))
		eventPublisher = rabbitmq.NoopPublisher{}
	} else {
		eventPublisher = amqpPublisher
	}

	accountService := usecase.NewAccountUsecase(accountRepo, jwtService, eventPublisher)
	accountHandler := http.NewAccountHandler(accountService)

	authMiddleware := http.AuthMiddleware(jwtService)

	// Setup Gin router and delivery layer
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}
	router := gin.Default()

	http.RegisterRoutes(router, accountHandler, authMiddleware)

	// Start the HTTP server
	addr := fmt.Sprintf(":%s", cfg.Port)
	logger.Info("Server listening", zap.String("port", addr))

	if err := router.Run(addr); err != nil {
		logger.Fatal("Server failed to start", zap.Error(err))
	}
}
