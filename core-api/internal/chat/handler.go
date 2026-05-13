package chat

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"sort"
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

	if isGreetingOnly(req.Message) {
		if _, err := h.repo.SaveMessage(ctx, sessionID, "user", req.Message); err != nil {
			response.Error(w, http.StatusInternalServerError, err.Error())
			return
		}

		reply := h.buildGreetingReply(ctx, req.UserID)
		if _, err := h.repo.SaveMessage(ctx, sessionID, "assistant", reply); err != nil {
			response.Error(w, http.StatusInternalServerError, err.Error())
			return
		}

		response.JSON(w, http.StatusOK, SendMessageResponse{
			SessionID: sessionID,
			Reply:     reply,
		})
		return
	}

	// Fetch mentors if the message is mentor-related (single DB call reused for both prompt + response)
	var mentorCards []MentorCard
	var mentorSection string
	if isMentorRelated(req.Message) {
		mentors, err := h.mentorRepo.List(ctx)
		if err == nil && len(mentors) > 0 {
			profile, _ := h.businessRepo.GetByUserID(ctx, req.UserID)
			mentorCards = recommendMentors(req.Message, profile, mentors, 1)
			mentorSection = formatMentorSection(mentorCards)
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

func (h *Handler) buildGreetingReply(ctx context.Context, userID string) string {
	businessName := ""
	if profile, err := h.businessRepo.GetByUserID(ctx, userID); err == nil && profile.BusinessName != "" {
		businessName = profile.BusinessName
	}

	if businessName == "" {
		return "Haloww, salam kenal! Saya Sorota, asisten bisnis yang siap bantu kamu menentukan strategi bisnis dengan lebih praktis.\n\n" +
			"Kamu bisa tanya soal omzet, margin, harga, promosi, operasional, atau target berikutnya.\n\n" +
			"Mau saya bantu mulai dari bagian mana dulu?"
	}

	return fmt.Sprintf(
		"Haloww, salam kenal owner %s! Saya Sorota, asisten bisnis yang siap bantu kamu menentukan strategi bisnis dengan lebih praktis.\n\n"+
			"Kamu bisa tanya soal omzet, margin, harga, promosi, operasional, atau target berikutnya.\n\n"+
			"Mau saya bantu mulai dari bagian mana dulu?",
		businessName,
	)
}

// formatMentorSection builds the prompt section for mentor recommendations.
func formatMentorSection(mentors []MentorCard) string {
	if len(mentors) == 0 {
		return ""
	}

	var sb strings.Builder
	sb.WriteString("MENTOR_SECTION:\n")
	sb.WriteString("Berikut mentor Sorota yang paling cocok berdasarkan profil dan pertanyaan user. ")
	sb.WriteString("Rekomendasikan hanya mentor di daftar ini. ")
	sb.WriteString("Jangan tulis URL booking mentah karena tombol booking akan tampil di kartu mentor.\n\n")
	for i, m := range mentors {
		fmt.Fprintf(&sb, "%d. %s - Keahlian: %s\n", i+1, m.Name, m.Expertise)
		fmt.Fprintf(&sb, "   Alasan cocok: %s\n\n", m.Reason)
	}
	return sb.String()
}

type mentorCandidate struct {
	card  MentorCard
	score int
}

func recommendMentors(
	userMessage string,
	profile *business.Profile,
	mentors []mentor.Mentor,
	limit int,
) []MentorCard {
	if limit <= 0 {
		limit = 1
	}

	context := buildMentorContext(userMessage, profile)
	userContext := strings.ToLower(userMessage)
	candidates := make([]mentorCandidate, 0, len(mentors))
	for _, m := range mentors {
		score, reason := scoreMentor(userContext, context, m)
		candidates = append(candidates, mentorCandidate{
			score: score,
			card: MentorCard{
				Name:       m.Name,
				Expertise:  m.Expertise,
				Reason:     reason,
				BookingURL: m.BookingURL,
			},
		})
	}

	sort.SliceStable(candidates, func(i, j int) bool {
		return candidates[i].score > candidates[j].score
	})

	if limit > len(candidates) {
		limit = len(candidates)
	}

	recommended := make([]MentorCard, 0, limit)
	for _, candidate := range candidates[:limit] {
		recommended = append(recommended, candidate.card)
	}
	return recommended
}

func buildMentorContext(userMessage string, profile *business.Profile) string {
	var sb strings.Builder
	sb.WriteString(strings.ToLower(userMessage))
	if profile == nil {
		return sb.String()
	}

	writeContextValue(&sb, profile.BusinessName)
	writeContextValue(&sb, profile.BusinessType)
	writeContextValue(&sb, profile.Location)
	writeContextValue(&sb, profile.MainProblem)
	if profile.MainProducts != nil {
		writeContextValue(&sb, *profile.MainProducts)
	}
	if profile.TargetGoal != nil {
		writeContextValue(&sb, *profile.TargetGoal)
	}
	return sb.String()
}

func writeContextValue(sb *strings.Builder, value string) {
	value = strings.TrimSpace(value)
	if value == "" {
		return
	}
	sb.WriteString(" ")
	sb.WriteString(strings.ToLower(value))
}

func scoreMentor(userContext, context string, m mentor.Mentor) (int, string) {
	expertise := strings.ToLower(m.Expertise)
	description := strings.ToLower(m.Description)
	text := expertise + " " + description

	score := 1
	reason := "Cocok untuk membantu merapikan prioritas bisnis dan menentukan langkah berikutnya."

	if containsAny(userContext, []string{"f&b", "fnb", "kuliner", "makanan", "minuman", "kopi", "kafe", "cafe"}) &&
		containsAny(text, []string{"f&b", "kuliner"}) {
		score += 20
	}

	if containsAny(userContext, []string{"promosi", "marketing", "iklan", "online", "marketplace", "e-commerce", "sosmed", "instagram", "tiktok"}) &&
		containsAny(text, []string{"digital", "marketing", "e-commerce"}) {
		score += 20
	}

	if containsAny(userContext, []string{"margin", "laba", "profit", "cash flow", "cashflow", "modal", "hpp", "pembukuan", "keuangan"}) &&
		containsAny(text, []string{"keuangan", "pembukuan"}) {
		score += 20
	}

	if containsAny(userContext, []string{"fashion", "baju", "pakaian", "hijab", "retail", "stok", "toko"}) &&
		containsAny(text, []string{"retail", "fashion"}) {
		score += 20
	}

	if containsAny(context, []string{"f&b", "fnb", "kuliner", "makanan", "minuman", "kopi", "kafe", "cafe", "warung", "box"}) &&
		containsAny(text, []string{"f&b", "kuliner"}) {
		score += 12
		reason = "Paling relevan karena fokus di F&B/kuliner, cocok untuk membahas produk, paket jualan, operasional, dan scale omzet."
	}

	if containsAny(context, []string{"promosi", "marketing", "iklan", "online", "marketplace", "e-commerce", "sosmed", "instagram", "tiktok", "channel"}) &&
		containsAny(text, []string{"digital", "marketing", "e-commerce"}) {
		score += 10
		reason = "Cocok kalau fokus utama kamu adalah promosi, channel penjualan online, dan akuisisi pelanggan baru."
	}

	if containsAny(context, []string{"margin", "laba", "profit", "cash flow", "cashflow", "modal", "hpp", "pembukuan", "keuangan"}) &&
		containsAny(text, []string{"keuangan", "pembukuan"}) {
		score += 10
		reason = "Cocok kalau kamu ingin membedah margin, cash flow, HPP, pembukuan, dan keputusan keuangan UMKM."
	}

	if containsAny(context, []string{"fashion", "baju", "pakaian", "hijab", "retail", "stok", "toko"}) &&
		containsAny(text, []string{"retail", "fashion"}) {
		score += 10
		reason = "Cocok untuk membahas stok, pricing, brand, dan penjualan retail/fashion."
	}

	if containsAny(context, []string{"scale", "naik", "omzet", "omset", "cabang", "repeat order", "order harian"}) &&
		containsAny(text, []string{"profitabilitas", "perluasan", "f&b", "kuliner"}) {
		score += 4
	}

	return score, reason
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

func isGreetingOnly(msg string) bool {
	normalized := strings.ToLower(strings.TrimSpace(msg))
	normalized = strings.NewReplacer(
		".", " ",
		",", " ",
		"!", " ",
		"?", " ",
		"~", " ",
		":", " ",
		";", " ",
		"-", " ",
	).Replace(normalized)

	tokens := strings.Fields(normalized)
	if len(tokens) == 0 || len(tokens) > 4 {
		return false
	}

	allowed := map[string]bool{
		"halo":            true,
		"haloo":           true,
		"halooo":          true,
		"halow":           true,
		"haloww":          true,
		"halowww":         true,
		"hallo":           true,
		"hai":             true,
		"hi":              true,
		"hey":             true,
		"hei":             true,
		"selamat":         true,
		"pagi":            true,
		"siang":           true,
		"sore":            true,
		"malam":           true,
		"assalamualaikum": true,
		"assalamu":        true,
		"min":             true,
		"admin":           true,
		"kak":             true,
		"mas":             true,
		"mbak":            true,
		"pak":             true,
		"bu":              true,
		"sorota":          true,
	}

	hasGreeting := false
	for _, token := range tokens {
		if strings.HasPrefix(token, "halo") || strings.HasPrefix(token, "hallo") || allowed[token] {
			if strings.HasPrefix(token, "halo") || strings.HasPrefix(token, "hallo") ||
				token == "hai" || token == "hi" || token == "hey" || token == "hei" ||
				token == "pagi" || token == "siang" || token == "sore" || token == "malam" ||
				token == "assalamualaikum" || token == "assalamu" {
				hasGreeting = true
			}
			continue
		}
		return false
	}

	return hasGreeting
}

func containsAny(value string, keywords []string) bool {
	for _, keyword := range keywords {
		if strings.Contains(value, keyword) {
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
