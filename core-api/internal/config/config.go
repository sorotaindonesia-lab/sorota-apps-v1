package config

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	Port         string
	DatabaseURL  string
	AIProvider   string
	AIAPIKey     string
	AIBaseURL    string
	AIModel      string
	AISystemPath string
}

func Load() *Config {
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, reading from environment")
	}

	return &Config{
		Port:         getEnv("PORT", "8080"),
		DatabaseURL:  mustGetEnv("DATABASE_URL"),
		AIProvider:   getEnv("AI_PROVIDER", "mock"),
		AIAPIKey:     getEnv("AI_API_KEY", ""),
		AIBaseURL:    getEnv("AI_BASE_URL", "https://api.openai.com/v1"),
		AIModel:      getEnv("AI_MODEL", "gpt-4o-mini"),
		AISystemPath: getEnv("AI_SYSTEM_PATH", "../ai-system"),
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func mustGetEnv(key string) string {
	v := os.Getenv(key)
	if v == "" {
		log.Fatalf("required environment variable %s is not set", key)
	}
	return v
}
