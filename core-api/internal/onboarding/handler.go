package onboarding

import (
	"encoding/json"
	"net/http"

	"github.com/sorota/core-api/pkg/response"
)

type Handler struct{}

func NewHandler() *Handler {
	return &Handler{}
}

func (h *Handler) Parse(w http.ResponseWriter, r *http.Request) {
	var req ParseRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		response.Error(w, http.StatusBadRequest, "invalid request body")
		return
	}

	result := Parse(req)
	response.JSON(w, http.StatusOK, result)
}
