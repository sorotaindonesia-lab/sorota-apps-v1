package business

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/sorota/core-api/pkg/response"
)

type Handler struct {
	repo *Repository
}

func NewHandler(repo *Repository) *Handler {
	return &Handler{repo: repo}
}

func (h *Handler) Create(w http.ResponseWriter, r *http.Request) {
	var req CreateProfileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		response.Error(w, http.StatusBadRequest, "invalid request body")
		return
	}

	profile, err := h.repo.Create(r.Context(), req)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, err.Error())
		return
	}
	response.JSON(w, http.StatusCreated, profile)
}

func (h *Handler) GetByUserID(w http.ResponseWriter, r *http.Request) {
	userID := chi.URLParam(r, "user_id")

	profile, err := h.repo.GetByUserID(r.Context(), userID)
	if err != nil {
		response.Error(w, http.StatusNotFound, "business profile not found")
		return
	}
	response.JSON(w, http.StatusOK, profile)
}

func (h *Handler) Update(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")

	var req UpdateProfileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		response.Error(w, http.StatusBadRequest, "invalid request body")
		return
	}

	profile, err := h.repo.Update(r.Context(), id, req)
	if err != nil {
		response.Error(w, http.StatusInternalServerError, err.Error())
		return
	}
	response.JSON(w, http.StatusOK, profile)
}
