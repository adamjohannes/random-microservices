package config

import (
	"errors"
	"fmt"
	"os"
	"time"

	"github.com/joho/godotenv"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var (
	errRequiredEnvMissing = errors.New("required environment variable not set")
	errInvalidLogLevel    = errors.New("invalid logger level")
)

type Config struct {
	Port          string
	Environment   string
	DatabaseUrl   string
	JWTSecret     string
	JWTExpiry     time.Duration
	AmqpHost      string
	AmqpUser      string
	AmqpPass      string
	LoggerOptions []zap.Option
}

// Load reads configuration from the environment and populates the Config struct.
func Load() (*Config, error) {
	loggerOptions, err := getLoggerOptions()
	if err != nil {
		return nil, err
	}

	_ = godotenv.Load()

	jwtExpiryStr := getEnvOrDefault("JWT_EXPIRY", "24h")
	jwtExpiry, err := time.ParseDuration(jwtExpiryStr)
	if err != nil {
		return nil, err
	}

	cfg := &Config{
		Port:          getEnvOrDefault("PORT", "8080"),
		Environment:   getEnvOrDefault("ENVIRONMENT", "development"),
		DatabaseUrl:   os.Getenv("DATABASE_URL"),
		JWTSecret:     os.Getenv("JWT_SECRET"),
		JWTExpiry:     jwtExpiry,
		AmqpHost:      getEnvOrDefault("AMQP_HOST", "localhost"),
		AmqpUser:      getEnvOrDefault("AMQP_USER", "guest"),
		AmqpPass:      getEnvOrDefault("AMQP_PASS", "guest"),
		LoggerOptions: loggerOptions,
	}

	// Validate required variables. If this fails, the app should crash on startup.
	if cfg.DatabaseUrl == "" {
		return nil, fmt.Errorf("%w: %v", errRequiredEnvMissing, "DATABASE_URL")
	}
	if cfg.JWTSecret == "" {
		return nil, fmt.Errorf("%w: %v", errRequiredEnvMissing, "DATABASE_URL")
	}

	return cfg, nil
}

// getLoggerOptions gets the configs list for setting up the global logger.
func getLoggerOptions() ([]zap.Option, error) {
	opts := []zap.Option{}

	// LOG_CALLER=enables/disables caller annotation
	if getEnvOrDefault("LOG_CALLER", "true") == "true" {
		opts = append(opts, zap.AddCaller())
	}

	// LOG_LEVEL=controls the minimum level that attaches a stack trace
	level := getEnvOrDefault("LOG_LEVEL", "info")
	switch level {
	case "debug":
		opts = append(opts, zap.AddStacktrace(zapcore.DebugLevel))
	case "info":
		opts = append(opts, zap.AddStacktrace(zapcore.InfoLevel))
	case "warn":
		opts = append(opts, zap.AddStacktrace(zapcore.WarnLevel))
	case "error":
		opts = append(opts, zap.AddStacktrace(zapcore.ErrorLevel))
	case "fatal":
		opts = append(opts, zap.AddStacktrace(zapcore.FatalLevel))
	default:
		return nil, fmt.Errorf("%w: %v", errInvalidLogLevel, level)
	}

	return opts, nil
}

// getEnvOrDefault gets an environment variable or returns a fallback value if it's empty.
func getEnvOrDefault(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
