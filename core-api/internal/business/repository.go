package business

import (
	"context"
	"fmt"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Repository struct {
	db *pgxpool.Pool
}

func NewRepository(db *pgxpool.Pool) *Repository {
	return &Repository{db: db}
}

func (r *Repository) Create(ctx context.Context, req CreateProfileRequest) (*Profile, error) {
	// Ensure user row exists before inserting business profile (MVP: no auth yet).
	_, err := r.db.Exec(ctx, `
		INSERT INTO users (id, name, email)
		VALUES ($1, $2, $3)
		ON CONFLICT DO NOTHING`,
		req.UserID,
		"User "+req.UserID[:8],
		req.UserID+"@sorota.local",
	)
	if err != nil {
		return nil, fmt.Errorf("ensure user exists: %w", err)
	}

	p := &Profile{
		ID:                  uuid.NewString(),
		UserID:              req.UserID,
		BusinessName:        req.BusinessName,
		BusinessType:        req.BusinessType,
		Location:            req.Location,
		MonthlyRevenue:      req.MonthlyRevenue,
		MonthlyProfit:       req.MonthlyProfit,
		MainProducts:        req.MainProducts,
		MainProblem:         req.MainProblem,
		TargetGoal:          req.TargetGoal,
		SellingPricePerUnit: req.SellingPricePerUnit,
		CostPerUnit:         req.CostPerUnit,
	}

	_, err = r.db.Exec(ctx, `
		INSERT INTO business_profiles
			(id, user_id, business_name, business_type, location,
			 monthly_revenue, monthly_profit, main_products, main_problem, target_goal,
			 selling_price_per_unit, cost_per_unit)
		VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)`,
		p.ID, p.UserID, p.BusinessName, p.BusinessType, p.Location,
		p.MonthlyRevenue, p.MonthlyProfit, p.MainProducts, p.MainProblem, p.TargetGoal,
		p.SellingPricePerUnit, p.CostPerUnit,
	)
	if err != nil {
		return nil, fmt.Errorf("create business profile: %w", err)
	}
	return r.GetByUserID(ctx, req.UserID)
}

func (r *Repository) GetByUserID(ctx context.Context, userID string) (*Profile, error) {
	p := &Profile{}
	err := r.db.QueryRow(ctx, `
		SELECT id, user_id, business_name, business_type, location,
		       monthly_revenue, monthly_profit, main_products, main_problem, target_goal,
		       selling_price_per_unit, cost_per_unit,
		       created_at, updated_at
		FROM business_profiles WHERE user_id = $1`, userID,
	).Scan(
		&p.ID, &p.UserID, &p.BusinessName, &p.BusinessType, &p.Location,
		&p.MonthlyRevenue, &p.MonthlyProfit, &p.MainProducts, &p.MainProblem, &p.TargetGoal,
		&p.SellingPricePerUnit, &p.CostPerUnit,
		&p.CreatedAt, &p.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("get business profile: %w", err)
	}
	return p, nil
}

func (r *Repository) Update(ctx context.Context, id string, req UpdateProfileRequest) (*Profile, error) {
	_, err := r.db.Exec(ctx, `
		UPDATE business_profiles SET
			business_name          = COALESCE($2,  business_name),
			business_type          = COALESCE($3,  business_type),
			location               = COALESCE($4,  location),
			monthly_revenue        = COALESCE($5,  monthly_revenue),
			monthly_profit         = COALESCE($6,  monthly_profit),
			main_products          = COALESCE($7,  main_products),
			main_problem           = COALESCE($8,  main_problem),
			target_goal            = COALESCE($9,  target_goal),
			selling_price_per_unit = COALESCE($10, selling_price_per_unit),
			cost_per_unit          = COALESCE($11, cost_per_unit),
			updated_at             = NOW()
		WHERE id = $1`,
		id,
		req.BusinessName, req.BusinessType, req.Location,
		req.MonthlyRevenue, req.MonthlyProfit, req.MainProducts,
		req.MainProblem, req.TargetGoal,
		req.SellingPricePerUnit, req.CostPerUnit,
	)
	if err != nil {
		return nil, fmt.Errorf("update business profile: %w", err)
	}

	p := &Profile{}
	err = r.db.QueryRow(ctx, `
		SELECT id, user_id, business_name, business_type, location,
		       monthly_revenue, monthly_profit, main_products, main_problem, target_goal,
		       selling_price_per_unit, cost_per_unit,
		       created_at, updated_at
		FROM business_profiles WHERE id = $1`, id,
	).Scan(
		&p.ID, &p.UserID, &p.BusinessName, &p.BusinessType, &p.Location,
		&p.MonthlyRevenue, &p.MonthlyProfit, &p.MainProducts, &p.MainProblem, &p.TargetGoal,
		&p.SellingPricePerUnit, &p.CostPerUnit,
		&p.CreatedAt, &p.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("get updated business profile: %w", err)
	}
	return p, nil
}
