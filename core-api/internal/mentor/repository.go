package mentor

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
)

type Repository struct {
	db *pgxpool.Pool
}

func NewRepository(db *pgxpool.Pool) *Repository {
	return &Repository{db: db}
}

func (r *Repository) List(ctx context.Context) ([]Mentor, error) {
	rows, err := r.db.Query(ctx, `
		SELECT id, name, expertise, description, business_background,
		       booking_url, image_url, created_at, updated_at
		FROM mentors ORDER BY name ASC`,
	)
	if err != nil {
		return nil, fmt.Errorf("list mentors: %w", err)
	}
	defer rows.Close()

	var mentors []Mentor
	for rows.Next() {
		var m Mentor
		if err := rows.Scan(
			&m.ID, &m.Name, &m.Expertise, &m.Description, &m.BusinessBackground,
			&m.BookingURL, &m.ImageURL, &m.CreatedAt, &m.UpdatedAt,
		); err != nil {
			return nil, err
		}
		mentors = append(mentors, m)
	}
	return mentors, nil
}
