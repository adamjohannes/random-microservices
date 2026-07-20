package main

import (
	"account/internal/config"

	"go.uber.org/zap"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		panic(err)
	}

	logger, err := zap.NewProduction(cfg.LoggerOptions...)
	if err != nil {
		panic(err)
	}
	defer logger.Sync()
}
