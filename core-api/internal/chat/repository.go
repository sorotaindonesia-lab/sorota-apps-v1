package chat

import (
	"context"
	"fmt"
	"strings"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Repository struct {
	db *pgxpool.Pool
}

func NewRepository(db *pgxpool.Pool) *Repository {
	return &Repository{db: db}
}

func (r *Repository) CreateSession(ctx context.Context, userID, title string) (*Session, error) {
	s := &Session{ID: uuid.NewString(), UserID: userID, Title: title}
	_, err := r.db.Exec(ctx,
		`INSERT INTO chat_sessions (id, user_id, title) VALUES ($1, $2, $3)`,
		s.ID, s.UserID, s.Title,
	)
	if err != nil {
		return nil, fmt.Errorf("create session: %w", err)
	}
	return r.GetSession(ctx, s.ID)
}

func (r *Repository) GetSession(ctx context.Context, id string) (*Session, error) {
	s := &Session{}
	err := r.db.QueryRow(ctx,
		`SELECT id, user_id, title, created_at, updated_at FROM chat_sessions WHERE id = $1`, id,
	).Scan(&s.ID, &s.UserID, &s.Title, &s.CreatedAt, &s.UpdatedAt)
	if err != nil {
		return nil, fmt.Errorf("get session: %w", err)
	}
	return s, nil
}

func (r *Repository) ListSessions(ctx context.Context, userID string) ([]Session, error) {
	rows, err := r.db.Query(ctx,
		`SELECT id, user_id, title, created_at, updated_at
		 FROM chat_sessions WHERE user_id = $1 ORDER BY updated_at DESC`, userID,
	)
	if err != nil {
		return nil, fmt.Errorf("list sessions: %w", err)
	}
	defer rows.Close()

	var sessions []Session
	for rows.Next() {
		var s Session
		if err := rows.Scan(&s.ID, &s.UserID, &s.Title, &s.CreatedAt, &s.UpdatedAt); err != nil {
			return nil, err
		}
		sessions = append(sessions, s)
	}
	return sessions, nil
}

func (r *Repository) SaveMessage(ctx context.Context, sessionID, role, content string) (*Message, error) {
	m := &Message{ID: uuid.NewString(), SessionID: sessionID, Role: role, Content: content}
	_, err := r.db.Exec(ctx,
		`INSERT INTO chat_messages (id, session_id, role, content) VALUES ($1, $2, $3, $4)`,
		m.ID, m.SessionID, m.Role, m.Content,
	)
	if err != nil {
		return nil, fmt.Errorf("save message: %w", err)
	}

	// bump session updated_at
	_, _ = r.db.Exec(ctx, `UPDATE chat_sessions SET updated_at = NOW() WHERE id = $1`, sessionID)

	return m, nil
}

func (r *Repository) ListMessages(ctx context.Context, sessionID string) ([]Message, error) {
	rows, err := r.db.Query(ctx,
		`SELECT id, session_id, role, content, created_at
		 FROM chat_messages WHERE session_id = $1 ORDER BY created_at ASC`, sessionID,
	)
	if err != nil {
		return nil, fmt.Errorf("list messages: %w", err)
	}
	defer rows.Close()

	var messages []Message
	for rows.Next() {
		var m Message
		if err := rows.Scan(&m.ID, &m.SessionID, &m.Role, &m.Content, &m.CreatedAt); err != nil {
			return nil, err
		}
		messages = append(messages, m)
	}
	return messages, nil
}

// BuildChatHistory formats recent messages into a readable string for the prompt.
func BuildChatHistory(messages []Message, limit int) string {
	if len(messages) > limit {
		messages = messages[len(messages)-limit:]
	}
	var sb strings.Builder
	for _, m := range messages {
		sb.WriteString(m.Role + ": " + m.Content + "\n")
	}
	return sb.String()
}
