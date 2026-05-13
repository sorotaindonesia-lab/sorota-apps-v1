package ai

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
)

// OpenAIProvider calls any OpenAI-compatible chat completions API.
type OpenAIProvider struct {
	apiKey  string
	baseURL string
	model   string
}

func NewOpenAIProvider(apiKey, baseURL, model string) *OpenAIProvider {
	baseURL = strings.TrimRight(baseURL, "/")
	return &OpenAIProvider{
		apiKey:  apiKey,
		baseURL: baseURL,
		model:   model,
	}
}

type openAIRequest struct {
	Model    string          `json:"model"`
	Messages []openAIMessage `json:"messages"`
}

type openAIMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type openAIResponse struct {
	Choices []struct {
		Message openAIMessage `json:"message"`
	} `json:"choices"`
}

func (p *OpenAIProvider) Generate(ctx context.Context, prompt string) (string, error) {
	body, _ := json.Marshal(openAIRequest{
		Model:    p.model,
		Messages: []openAIMessage{{Role: "user", Content: prompt}},
	})

	endpoint := p.baseURL + "/chat/completions"
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+p.apiKey)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	raw, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("AI API error %d: %s", resp.StatusCode, raw)
	}

	var result openAIResponse
	if err := json.Unmarshal(raw, &result); err != nil {
		return "", err
	}
	if len(result.Choices) == 0 {
		return "", fmt.Errorf("AI API returned no choices")
	}
	return result.Choices[0].Message.Content, nil
}
