package onboarding

import (
	"regexp"
	"strconv"
	"strings"
)

type ProfileDraft struct {
	BusinessName        string   `json:"business_name"`
	BusinessType        string   `json:"business_type"`
	Location            string   `json:"location"`
	MonthlyRevenue      *float64 `json:"monthly_revenue"`
	MonthlyProfit       *float64 `json:"monthly_profit"`
	MainProducts        string   `json:"main_products"`
	MainProblem         string   `json:"main_problem"`
	TargetGoal          string   `json:"target_goal"`
	SellingPricePerUnit *float64 `json:"selling_price_per_unit"`
	CostPerUnit         *float64 `json:"cost_per_unit"`
}

type ParseRequest struct {
	Message      string       `json:"message"`
	CurrentField string       `json:"current_field"`
	Draft        ProfileDraft `json:"draft"`
}

type ParseResponse struct {
	Draft         ProfileDraft `json:"draft"`
	MissingFields []string     `json:"missing_fields"`
	NextField     string       `json:"next_field"`
	NextQuestion  string       `json:"next_question"`
	ReadyToSave   bool         `json:"ready_to_save"`
}

var requiredFields = []string{
	"business_name",
	"business_type",
	"location",
	"main_problem",
}

func Parse(req ParseRequest) ParseResponse {
	draft := normalizeDraft(req.Draft)
	message := strings.TrimSpace(req.Message)

	if message != "" && !isSkip(message) {
		applyFieldValue(&draft, req.CurrentField, message)
		inferFromMessage(&draft, message)
	}

	missing := missingRequiredFields(draft)
	if missing == nil {
		missing = []string{}
	}
	nextField := "optional_details"
	nextQuestion := "Profil minimumnya sudah cukup. Kalau mau lebih akurat, tulis omzet, laba, produk utama, harga jual, HPP, atau target bisnis. Bisa juga langsung simpan."

	if len(missing) > 0 {
		nextField = missing[0]
		nextQuestion = questionForField(nextField)
	}

	return ParseResponse{
		Draft:         draft,
		MissingFields: missing,
		NextField:     nextField,
		NextQuestion:  nextQuestion,
		ReadyToSave:   len(missing) == 0,
	}
}

func normalizeDraft(d ProfileDraft) ProfileDraft {
	d.BusinessName = strings.TrimSpace(d.BusinessName)
	d.BusinessType = strings.TrimSpace(d.BusinessType)
	d.Location = strings.TrimSpace(d.Location)
	d.MainProducts = strings.TrimSpace(d.MainProducts)
	d.MainProblem = strings.TrimSpace(d.MainProblem)
	d.TargetGoal = strings.TrimSpace(d.TargetGoal)
	return d
}

func missingRequiredFields(d ProfileDraft) []string {
	var missing []string
	for _, field := range requiredFields {
		if fieldValue(d, field) == "" {
			missing = append(missing, field)
		}
	}
	return missing
}

func fieldValue(d ProfileDraft, field string) string {
	switch field {
	case "business_name":
		return d.BusinessName
	case "business_type":
		return d.BusinessType
	case "location":
		return d.Location
	case "main_problem":
		return d.MainProblem
	default:
		return ""
	}
}

func applyFieldValue(d *ProfileDraft, field, message string) {
	value := cleanTextAnswer(message)
	if value == "" {
		return
	}

	switch field {
	case "business_name":
		d.BusinessName = value
	case "business_type":
		d.BusinessType = value
	case "location":
		d.Location = value
	case "main_problem":
		d.MainProblem = value
	case "main_products":
		d.MainProducts = value
	case "target_goal":
		d.TargetGoal = value
	case "monthly_revenue":
		if amount, ok := parseMoney(message); ok {
			d.MonthlyRevenue = &amount
		}
	case "monthly_profit":
		if amount, ok := parseMoney(message); ok {
			d.MonthlyProfit = &amount
		}
	case "selling_price_per_unit":
		if amount, ok := parseMoney(message); ok {
			d.SellingPricePerUnit = &amount
		}
	case "cost_per_unit":
		if amount, ok := parseMoney(message); ok {
			d.CostPerUnit = &amount
		}
	}
}

func inferFromMessage(d *ProfileDraft, message string) {
	if d.BusinessName == "" {
		if value := extractBusinessName(message); value != "" {
			d.BusinessName = value
		}
	}
	if d.BusinessType == "" {
		if value := inferBusinessType(message); value != "" {
			d.BusinessType = value
		}
	}
	if d.Location == "" {
		if value := extractLocation(message); value != "" {
			d.Location = value
		}
	}
	if d.MainProblem == "" {
		if value := extractAfterAny(message, []string{"masalahnya", "kendalanya", "problemnya", "tantangannya"}); value != "" {
			d.MainProblem = value
		}
	}
	if d.MainProducts == "" {
		if value := extractAfterAny(message, []string{"produk utama", "jualan", "menjual", "layanan"}); value != "" {
			d.MainProducts = value
		}
	}
	if d.TargetGoal == "" {
		if value := extractAfterAny(message, []string{"targetnya", "target saya", "ingin", "mau"}); value != "" {
			d.TargetGoal = value
		}
	}
	if d.MonthlyRevenue == nil {
		if amount, ok := extractMoneyNearKeyword(message, []string{"omzet", "omset", "pendapatan"}); ok {
			d.MonthlyRevenue = &amount
		}
	}
	if d.MonthlyProfit == nil {
		if amount, ok := extractMoneyNearKeyword(message, []string{"laba", "profit", "untung", "keuntungan"}); ok {
			d.MonthlyProfit = &amount
		}
	}
	if d.SellingPricePerUnit == nil {
		if amount, ok := extractMoneyNearKeyword(message, []string{"harga jual", "jual per unit"}); ok {
			d.SellingPricePerUnit = &amount
		}
	}
	if d.CostPerUnit == nil {
		if amount, ok := extractMoneyNearKeyword(message, []string{"hpp", "modal", "biaya per unit"}); ok {
			d.CostPerUnit = &amount
		}
	}
}

func questionForField(field string) string {
	switch field {
	case "business_name":
		return "Boleh sebut nama bisnisnya?"
	case "business_type":
		return "Bisnisnya bergerak di bidang apa? Contoh: kafe, laundry, toko kelontong, fashion."
	case "location":
		return "Lokasi bisnisnya di mana?"
	case "main_problem":
		return "Masalah utama yang paling ingin dibantu Sorota apa?"
	default:
		return "Bisa ceritakan sedikit lagi?"
	}
}

func cleanTextAnswer(value string) string {
	value = strings.TrimSpace(value)
	value = strings.Trim(value, ".")
	return strings.TrimSpace(value)
}

func isSkip(message string) bool {
	msg := strings.ToLower(strings.TrimSpace(message))
	skipWords := []string{"skip", "lewati", "langsung", "tidak tahu", "nggak tahu", "ga tahu", "belum tahu", "nanti"}
	for _, word := range skipWords {
		if msg == word || strings.Contains(msg, word) {
			return true
		}
	}
	return false
}

func extractBusinessName(message string) string {
	patterns := []*regexp.Regexp{
		regexp.MustCompile(`(?i)(?:nama bisnis|nama usaha)\s*(?:saya|kami)?\s*(?:adalah|namanya)?\s+([^,.]+)`),
		regexp.MustCompile(`(?i)(?:bisnis|usaha)\s*(?:saya|kami)?\s*(?:namanya|adalah)?\s+([^,.]+)`),
	}

	for _, pattern := range patterns {
		match := pattern.FindStringSubmatch(message)
		if len(match) < 2 {
			continue
		}
		value := strings.TrimSpace(match[1])
		value = splitBeforeAny(value, []string{" di ", " yang ", " dengan ", " bergerak "})
		if value != "" {
			return value
		}
	}
	return ""
}

func inferBusinessType(message string) string {
	msg := strings.ToLower(message)
	switch {
	case containsAny(msg, []string{"kopi", "kafe", "cafe", "warung", "makanan", "minuman", "kuliner", "resto"}):
		return "F&B / Kuliner"
	case strings.Contains(msg, "laundry"):
		return "Laundry"
	case containsAny(msg, []string{"fashion", "baju", "pakaian", "hijab"}):
		return "Retail / Fashion"
	case containsAny(msg, []string{"toko", "kelontong", "retail", "sembako"}):
		return "Retail"
	case containsAny(msg, []string{"online shop", "olshop", "marketplace", "e-commerce"}):
		return "E-Commerce"
	default:
		return ""
	}
}

func extractLocation(message string) string {
	pattern := regexp.MustCompile(`(?i)(?:lokasi(?:nya)?\s*)?(?:di|daerah)\s+([a-zA-Z\s]+?)(?:,|\.|\s+dengan\s+|\s+yang\s+|\s+dan\s+|$)`)
	match := pattern.FindStringSubmatch(message)
	if len(match) < 2 {
		return ""
	}

	value := strings.TrimSpace(match[1])
	value = strings.Trim(value, ".")
	if strings.HasPrefix(strings.ToLower(value), "bidang ") {
		return ""
	}
	return strings.TrimSpace(value)
}

func extractAfterAny(message string, keywords []string) string {
	lower := strings.ToLower(message)
	for _, keyword := range keywords {
		idx := strings.Index(lower, keyword)
		if idx == -1 {
			continue
		}
		start := idx + len(keyword)
		value := strings.TrimSpace(message[start:])
		value = strings.TrimLeft(value, " :-")
		value = splitBeforeAny(value, []string{". ", "\n"})
		return cleanTextAnswer(value)
	}
	return ""
}

func splitBeforeAny(value string, separators []string) string {
	lowest := -1
	lower := strings.ToLower(value)
	for _, separator := range separators {
		idx := strings.Index(lower, separator)
		if idx == -1 {
			continue
		}
		if lowest == -1 || idx < lowest {
			lowest = idx
		}
	}
	if lowest == -1 {
		return strings.TrimSpace(value)
	}
	return strings.TrimSpace(value[:lowest])
}

func containsAny(value string, keywords []string) bool {
	for _, keyword := range keywords {
		if strings.Contains(value, keyword) {
			return true
		}
	}
	return false
}

func extractMoneyNearKeyword(message string, keywords []string) (float64, bool) {
	lower := strings.ToLower(message)
	for _, keyword := range keywords {
		idx := strings.Index(lower, keyword)
		if idx == -1 {
			continue
		}
		start := idx + len(keyword)
		end := start + 80
		if end > len(message) {
			end = len(message)
		}
		if amount, ok := parseMoney(message[start:end]); ok {
			return amount, true
		}
	}
	return 0, false
}

func parseMoney(value string) (float64, bool) {
	pattern := regexp.MustCompile(`(?i)(?:rp\s*)?([0-9][0-9.,]*)\s*(miliar|juta|ribu|jt|rb|k|m)?`)
	match := pattern.FindStringSubmatch(value)
	if len(match) < 2 {
		return 0, false
	}

	unit := ""
	if len(match) > 2 {
		unit = strings.ToLower(match[2])
	}

	num, err := parseLocalizedNumber(match[1], unit != "")
	if err != nil {
		return 0, false
	}

	switch unit {
	case "miliar", "m":
		num *= 1_000_000_000
	case "juta", "jt":
		num *= 1_000_000
	case "ribu", "rb", "k":
		num *= 1_000
	}

	if num <= 0 {
		return 0, false
	}
	return num, true
}

func parseLocalizedNumber(raw string, hasUnit bool) (float64, error) {
	cleaned := strings.TrimSpace(raw)
	if hasUnit {
		cleaned = strings.ReplaceAll(cleaned, ",", ".")
		if strings.Count(cleaned, ".") > 1 {
			cleaned = strings.ReplaceAll(cleaned, ".", "")
		}
		return strconv.ParseFloat(cleaned, 64)
	}

	cleaned = strings.ReplaceAll(cleaned, ".", "")
	cleaned = strings.ReplaceAll(cleaned, ",", "")
	return strconv.ParseFloat(cleaned, 64)
}
