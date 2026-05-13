package mentor

import "time"

type Mentor struct {
	ID                 string    `json:"id" db:"id"`
	Name               string    `json:"name" db:"name"`
	Expertise          string    `json:"expertise" db:"expertise"`
	Description        string    `json:"description" db:"description"`
	BusinessBackground *string   `json:"business_background,omitempty" db:"business_background"`
	BookingURL         string    `json:"booking_url" db:"booking_url"`
	ImageURL           *string   `json:"image_url,omitempty" db:"image_url"`
	CreatedAt          time.Time `json:"created_at" db:"created_at"`
	UpdatedAt          time.Time `json:"updated_at" db:"updated_at"`
}
