package ai

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// AIProvider is the abstraction for any AI backend.
type AIProvider interface {
	Generate(ctx context.Context, prompt string) (string, error)
}

// LoadPromptTemplate reads a prompt file from the ai-system folder
// and replaces the given placeholders.
func LoadPromptTemplate(aiSystemPath, templateName string, vars map[string]string) (string, error) {
	path := filepath.Join(aiSystemPath, "prompts", templateName)
	raw, err := os.ReadFile(path)
	if err != nil {
		return "", fmt.Errorf("read prompt template %s: %w", templateName, err)
	}

	result := string(raw)
	for k, v := range vars {
		result = strings.ReplaceAll(result, "{{"+k+"}}", v)
	}
	return result, nil
}
