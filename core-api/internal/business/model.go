package business

import "time"

type Profile struct {
	ID                  string    `json:"id" db:"id"`
	UserID              string    `json:"user_id" db:"user_id"`
	BusinessName        string    `json:"business_name" db:"business_name"`
	BusinessType        string    `json:"business_type" db:"business_type"`
	Location            string    `json:"location" db:"location"`
	MonthlyRevenue      *float64  `json:"monthly_revenue,omitempty" db:"monthly_revenue"`
	MonthlyProfit       *float64  `json:"monthly_profit,omitempty" db:"monthly_profit"`
	MainProducts        *string   `json:"main_products,omitempty" db:"main_products"`
	MainProblem         string    `json:"main_problem" db:"main_problem"`
	TargetGoal          *string   `json:"target_goal,omitempty" db:"target_goal"`
	SellingPricePerUnit *float64  `json:"selling_price_per_unit,omitempty" db:"selling_price_per_unit"`
	CostPerUnit         *float64  `json:"cost_per_unit,omitempty" db:"cost_per_unit"`
	CreatedAt           time.Time `json:"created_at" db:"created_at"`
	UpdatedAt           time.Time `json:"updated_at" db:"updated_at"`
}

type CreateProfileRequest struct {
	UserID              string   `json:"user_id"`
	BusinessName        string   `json:"business_name"`
	BusinessType        string   `json:"business_type"`
	Location            string   `json:"location"`
	MonthlyRevenue      *float64 `json:"monthly_revenue,omitempty"`
	MonthlyProfit       *float64 `json:"monthly_profit,omitempty"`
	MainProducts        *string  `json:"main_products,omitempty"`
	MainProblem         string   `json:"main_problem"`
	TargetGoal          *string  `json:"target_goal,omitempty"`
	SellingPricePerUnit *float64 `json:"selling_price_per_unit,omitempty"`
	CostPerUnit         *float64 `json:"cost_per_unit,omitempty"`
}

type UpdateProfileRequest struct {
	BusinessName        *string  `json:"business_name,omitempty"`
	BusinessType        *string  `json:"business_type,omitempty"`
	Location            *string  `json:"location,omitempty"`
	MonthlyRevenue      *float64 `json:"monthly_revenue,omitempty"`
	MonthlyProfit       *float64 `json:"monthly_profit,omitempty"`
	MainProducts        *string  `json:"main_products,omitempty"`
	MainProblem         *string  `json:"main_problem,omitempty"`
	TargetGoal          *string  `json:"target_goal,omitempty"`
	SellingPricePerUnit *float64 `json:"selling_price_per_unit,omitempty"`
	CostPerUnit         *float64 `json:"cost_per_unit,omitempty"`
}
