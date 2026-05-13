package ai

import (
	"context"
	"fmt"
)

// MockProvider returns a canned response. Used in development.
type MockProvider struct{}

func NewMockProvider() *MockProvider {
	return &MockProvider{}
}

func (m *MockProvider) Generate(_ context.Context, prompt string) (string, error) {
	_ = prompt // prompt is accepted but not processed in mock
	return fmt.Sprintf(
		"[Mock AI Response] Terima kasih atas pertanyaan Anda. "+
			"Ini adalah respons dummy dari Sorota AI. "+
			"Ganti AI_PROVIDER=openai di .env untuk menggunakan respons nyata.",
	), nil
}
