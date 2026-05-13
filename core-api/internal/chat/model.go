package chat

import "time"

type Session struct {
	ID        string    `json:"id" db:"id"`
	UserID    string    `json:"user_id" db:"user_id"`
	Title     string    `json:"title" db:"title"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

type Message struct {
	ID        string    `json:"id" db:"id"`
	SessionID string    `json:"session_id" db:"session_id"`
	Role      string    `json:"role" db:"role"` // user | assistant | system
	Content   string    `json:"content" db:"content"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

type SendMessageRequest struct {
	UserID    string  `json:"user_id"`
	SessionID *string `json:"session_id,omitempty"`
	Message   string  `json:"message"`
}

// MentorCard is a lightweight mentor summary returned alongside AI replies
// when the user asks about mentors.
type MentorCard struct {
	Name       string `json:"name"`
	Expertise  string `json:"expertise"`
	Reason     string `json:"reason"`
	BookingURL string `json:"booking_url"`
}

type SendMessageResponse struct {
	SessionID          string       `json:"session_id"`
	Reply              string       `json:"reply"`
	RecommendedMentors []MentorCard `json:"recommended_mentors,omitempty"`
}
