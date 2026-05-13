package onboarding

import "testing"

func TestParseCapturesRequiredFieldByCurrentField(t *testing.T) {
	result := Parse(ParseRequest{
		Message:      "Warung Kopi Pak Joko",
		CurrentField: "business_name",
		Draft:        ProfileDraft{},
	})

	if result.Draft.BusinessName != "Warung Kopi Pak Joko" {
		t.Fatalf("BusinessName = %q", result.Draft.BusinessName)
	}
	if result.NextField != "location" {
		t.Fatalf("NextField = %q", result.NextField)
	}
	if result.ReadyToSave {
		t.Fatal("ReadyToSave should be false while required fields are missing")
	}
}

func TestParseInfersMoneyAndBusinessContext(t *testing.T) {
	result := Parse(ParseRequest{
		Message: "Nama bisnis saya Kopi Rapi di Semarang, omzet 15 juta, laba 3,5 juta, masalahnya sepi sore.",
		Draft:   ProfileDraft{},
	})

	if result.Draft.BusinessName != "Kopi Rapi" {
		t.Fatalf("BusinessName = %q", result.Draft.BusinessName)
	}
	if result.Draft.BusinessType != "F&B / Kuliner" {
		t.Fatalf("BusinessType = %q", result.Draft.BusinessType)
	}
	if result.Draft.Location != "Semarang" {
		t.Fatalf("Location = %q", result.Draft.Location)
	}
	if result.Draft.MainProblem != "sepi sore" {
		t.Fatalf("MainProblem = %q", result.Draft.MainProblem)
	}
	if result.Draft.MonthlyRevenue == nil || *result.Draft.MonthlyRevenue != 15_000_000 {
		t.Fatalf("MonthlyRevenue = %v", result.Draft.MonthlyRevenue)
	}
	if result.Draft.MonthlyProfit == nil || *result.Draft.MonthlyProfit != 3_500_000 {
		t.Fatalf("MonthlyProfit = %v", result.Draft.MonthlyProfit)
	}
	if !result.ReadyToSave {
		t.Fatal("ReadyToSave should be true after required fields are complete")
	}
	if result.MissingFields == nil {
		t.Fatal("MissingFields should be an empty array, not nil")
	}
}
