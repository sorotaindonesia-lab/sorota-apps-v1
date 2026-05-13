package chat

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/go-chi/chi/v5"
	"github.com/sorota/core-api/internal/ai"
	"github.com/sorota/core-api/internal/business"
	"github.com/sorota/core-api/internal/mentor"
	"github.com/sorota/core-api/pkg/response"
)

type Handler struct {
	repo         *Repository
	businessRepo *business.Repository
	mentorRepo   *mentor.Repository
	aiProvider   ai.AIProvider
	aiSystemPath string
}

func NewHandler(
	repo *Repository,
	businessRepo *business.Repository,
	mentorRepo *mentor.Repository,
	aiProvider ai.AIProvider,
	aiSystemPath string,
) *Handler {
	return &Handler{
		repo:         repo,
		businessRepo: businessRepo,
		mentorRepo:   mentorRepo,
		aiProvider:   aiProvider,
		aiSystemPath: aiSystemPath,
	}
}

func (h *Handler) Send(w http.ResponseWriter, r *http.Request) {
	var req SendMessageRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		response.Error(w, http.StatusBadRequest, "invalid request body")
		return
	}

	ctx := r.Context()

	// Get or create session
	var sessionID string
	if req.SessionID != nil && *req.SessionID != "" {
		sessionID = *req.SessionID
	} else {
		title := truncate(req.Message, 50)
		session, err := h.repo.CreateSession(ctx, req.UserID, title)
		if err != nil {
			response.Error(w, http.StatusInternalServerError, err.Error())
			return
		}
		sessionID = session.ID
	}

	// Fetch mentors if the message is mentor-related (single DB call reused for both prompt + response)
	var mentorCards []MentorCard
	var mentorSection string
	if isMentorRelated(req.Message) {
		mentors, err := h.mentorRepo.List(ctx)
		if err == nil && len(mentors) > 0 {
			mentorSection = formatMentorSection(mentors)
			for _, m := range mentors {
				mentorCards = append(mentorCards, MentorCard{
					Name:       m.Name,
					Expertise:  m.Expertise,
					BookingURL: m.BookingURL,
				})
			}
		}
	}

	// Build context strings
	businessContext := h.buildBusinessContext(ctx, req.UserID)
	messages, _ := h.repo.ListMessages(ctx, sessionID)
	chatHistory := BuildChatHistory(messages, 10)

	// Load and fill prompt template
	prompt, err := ai.LoadPromptTemplate(h.aiSystemPath, "business_advisor.md", map[string]string{
		"BUSINESS_CONTEXT": businessContext,
		"CHAT_HISTORY":     chatHistory,
		"USER_MESSAGE":     req.Message,
		"MENTOR_SECTION":   mentorSection,
	})
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "failed to load prompt: "+err.Error())
		return
	}

	// Save user message
	if _, err := h.repo.SaveMessage(ctx, sessionID, "user", req.Message); err != nil {
		response.Error(w, http.StatusInternalServerError, err.Error())
		return
	}

	// Call AI
	reply, err := h.aiProvider.Generate(ctx, prompt)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "AI error: "+err.Error())
		return
	}

	// Save assistant response
	if _, err := h.repo.SaveMessage(ctx, sessionID, "assistant", reply); err != nil {
		response.Error(w, http.StatusInternalServerError, err.Error())
		return
	}

	response.JSON(w, http.StatusOK, SendMessageResponse{
		SessionID:          sessionID,
		Reply:              reply,
		RecommendedMentors: mentorCards,
	})
}

func (h *Handler) ListSessions(w http.ResponseWriter, r *http.Request) {
	userID := chi.URLParam(r, "user_id")
	sessions, err := h.repo.ListSessions(r.Context(), userID)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, err.Error())
		return
	}
	response.JSON(w, http.StatusOK, sessions)
}

func (h *Handler) ListMessages(w http.ResponseWriter, r *http.Request) {
	sessionID := chi.URLParam(r, "session_id")
	messages, err := h.repo.ListMessages(r.Context(), sessionID)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, err.Error())
		return
	}
	response.JSON(w, http.StatusOK, messages)
}

func (h *Handler) buildBusinessContext(ctx context.Context, userID string) string {
	profile, err := h.businessRepo.GetByUserID(ctx, userID)
	if err != nil {
		return "Profil bisnis belum tersedia."
	}

	var sb strings.Builder
	fmt.Fprintf(&sb, "Nama Bisnis: %s\n", profile.BusinessName)
	fmt.Fprintf(&sb, "Jenis Bisnis: %s\n", profile.BusinessType)
	fmt.Fprintf(&sb, "Lokasi: %s\n", profile.Location)
	if profile.MonthlyRevenue != nil {
		fmt.Fprintf(&sb, "Omset Bulanan: Rp %.0f\n", *profile.MonthlyRevenue)
	}
	if profile.MonthlyProfit != nil {
		fmt.Fprintf(&sb, "Laba Bulanan: Rp %.0f\n", *profile.MonthlyProfit)
	}
	if profile.MainProducts != nil {
		fmt.Fprintf(&sb, "Produk Utama: %s\n", *profile.MainProducts)
	}
	fmt.Fprintf(&sb, "Masalah Utama: %s\n", profile.MainProblem)
	if profile.TargetGoal != nil {
		fmt.Fprintf(&sb, "Target: %s\n", *profile.TargetGoal)
	}
	if profile.SellingPricePerUnit != nil {
		fmt.Fprintf(&sb, "Harga Jual per Unit: Rp %.0f\n", *profile.SellingPricePerUnit)
	}
	if profile.CostPerUnit != nil {
		fmt.Fprintf(&sb, "Modal/HPP per Unit: Rp %.0f\n", *profile.CostPerUnit)
		if profile.SellingPricePerUnit != nil && *profile.SellingPricePerUnit > 0 {
			margin := ((*profile.SellingPricePerUnit - *profile.CostPerUnit) / *profile.SellingPricePerUnit) * 100
			fmt.Fprintf(&sb, "Margin per Unit: %.1f%%\n", margin)
		}
	}
	return sb.String()
}

// formatMentorSection builds the prompt section for mentor recommendations.
func formatMentorSection(mentors []mentor.Mentor) string {
	var sb strings.Builder
	sb.WriteString("MENTOR_SECTION:\n")
	sb.WriteString("Berikut daftar mentor yang tersedia di platform Sorota. ")
	sb.WriteString("Rekomendasikan mentor yang paling cocok berdasarkan masalah user. ")
	sb.WriteString("Sertakan nama mentor, keahliannya, dan alasan singkat kenapa cocok. ")
	sb.WriteString("Jangan suruh user mencari mentor di tempat lain.\n\n")
	for i, m := range mentors {
		fmt.Fprintf(&sb, "%d. %s — Keahlian: %s\n", i+1, m.Name, m.Expertise)
		fmt.Fprintf(&sb, "   Deskripsi: %s\n", m.Description)
		if m.BusinessBackground != nil {
			fmt.Fprintf(&sb, "   Background: %s\n", *m.BusinessBackground)
		}
		fmt.Fprintf(&sb, "   Booking: %s\n\n", m.BookingURL)
	}
	return sb.String()
}

// isMentorRelated checks if the user message is asking about mentors.
func isMentorRelated(msg string) bool {
	msg = strings.ToLower(msg)
	keywords := []string{
		"mentor", "konsultan", "konsultasi", "carikan mentor",
		"cari mentor", "rekomendasi mentor", "butuh mentor",
		"minta mentor", "booking mentor",
	}
	for _, kw := range keywords {
		if strings.Contains(msg, kw) {
			return true
		}
	}
	return false
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "..."
}
