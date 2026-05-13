package main

import (
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	chimiddleware "github.com/go-chi/chi/v5/middleware"

	"github.com/sorota/core-api/internal/ai"
	"github.com/sorota/core-api/internal/business"
	"github.com/sorota/core-api/internal/chat"
	"github.com/sorota/core-api/internal/config"
	"github.com/sorota/core-api/internal/database"
	"github.com/sorota/core-api/internal/mentor"
	apimiddleware "github.com/sorota/core-api/internal/middleware"
	"github.com/sorota/core-api/internal/whatsapp"
	"github.com/sorota/core-api/pkg/response"
)

func main() {
	cfg := config.Load()
	db := database.Connect(cfg.DatabaseURL)
	defer db.Close()

	// AI provider
	var aiProvider ai.AIProvider
	if cfg.AIProvider == "openai" {
		aiProvider = ai.NewOpenAIProvider(cfg.AIAPIKey, cfg.AIBaseURL, cfg.AIModel)
		log.Printf("AI provider: OpenAI-compatible (%s)", cfg.AIBaseURL)
	} else {
		aiProvider = ai.NewMockProvider()
		log.Println("AI provider: mock")
	}

	// Repositories
	businessRepo := business.NewRepository(db)
	chatRepo := chat.NewRepository(db)
	mentorRepo := mentor.NewRepository(db)

	// Handlers
	businessHandler := business.NewHandler(businessRepo)
	chatHandler := chat.NewHandler(chatRepo, businessRepo, mentorRepo, aiProvider, cfg.AISystemPath)
	mentorHandler := mentor.NewHandler(mentorRepo)
	whatsappHandler := whatsapp.NewHandler(chatRepo, businessRepo, aiProvider, cfg.AISystemPath)

	// Router
	r := chi.NewRouter()
	r.Use(chimiddleware.Logger)
	r.Use(chimiddleware.Recoverer)
	r.Use(apimiddleware.CORS())

	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		response.JSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})

	r.Route("/api/v1", func(r chi.Router) {
		// Business profiles
		r.Post("/business-profiles", businessHandler.Create)
		r.Get("/business-profiles/{user_id}", businessHandler.GetByUserID)
		r.Put("/business-profiles/{id}", businessHandler.Update)

		// Chat
		r.Post("/chat", chatHandler.Send)
		r.Get("/chat/sessions/{user_id}", chatHandler.ListSessions)
		r.Get("/chat/messages/{session_id}", chatHandler.ListMessages)

		// Mentors
		r.Get("/mentors", mentorHandler.List)

		// WhatsApp bridge
		r.Post("/whatsapp/message", whatsappHandler.Receive)
	})

	log.Printf("Sorota core-api listening on :%s", cfg.Port)
	if err := http.ListenAndServe(":"+cfg.Port, r); err != nil {
		log.Fatal(err)
	}
}
