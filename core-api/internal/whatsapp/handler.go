package whatsapp

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/sorota/core-api/internal/ai"
	"github.com/sorota/core-api/internal/business"
	"github.com/sorota/core-api/internal/chat"
	"github.com/sorota/core-api/pkg/response"
)

type InboundRequest struct {
	PhoneNumber string `json:"phone_number"`
	Message     string `json:"message"`
}

type InboundResponse struct {
	Reply string `json:"reply"`
}

type Handler struct {
	chatRepo     *chat.Repository
	businessRepo *business.Repository
	aiProvider   ai.AIProvider
	aiSystemPath string
}

func NewHandler(
	chatRepo *chat.Repository,
	businessRepo *business.Repository,
	aiProvider ai.AIProvider,
	aiSystemPath string,
) *Handler {
	return &Handler{
		chatRepo:     chatRepo,
		businessRepo: businessRepo,
		aiProvider:   aiProvider,
		aiSystemPath: aiSystemPath,
	}
}

func (h *Handler) Receive(w http.ResponseWriter, r *http.Request) {
	var req InboundRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		response.Error(w, http.StatusBadRequest, "invalid request body")
		return
	}

	ctx := r.Context()

	// For WhatsApp we use phone number as a simple user identifier.
	// No full user lookup for MVP; business context may be absent.
	businessContext := h.buildContext(ctx, req.PhoneNumber)

	prompt, err := ai.LoadPromptTemplate(h.aiSystemPath, "business_advisor.md", map[string]string{
		"BUSINESS_CONTEXT": businessContext,
		"CHAT_HISTORY":     "",
		"USER_MESSAGE":     req.Message,
	})
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "failed to load prompt")
		return
	}

	reply, err := h.aiProvider.Generate(ctx, prompt)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, "AI error: "+err.Error())
		return
	}

	response.JSON(w, http.StatusOK, InboundResponse{Reply: reply})
}

func (h *Handler) buildContext(ctx context.Context, phoneNumber string) string {
	_ = ctx
	_ = phoneNumber
	// MVP: return placeholder. In a real implementation, look up
	// whatsapp_contacts -> user_id -> business_profile.
	var sb strings.Builder
	fmt.Fprintf(&sb, "Pengguna menghubungi melalui WhatsApp (%s).\n", phoneNumber)
	fmt.Fprintf(&sb, "Profil bisnis belum terhubung ke nomor ini.\n")
	return sb.String()
}
