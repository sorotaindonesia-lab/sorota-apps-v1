package chat

import (
	"testing"

	"github.com/sorota/core-api/internal/business"
	"github.com/sorota/core-api/internal/mentor"
)

func TestIsGreetingOnly(t *testing.T) {
	tests := []struct {
		name string
		msg  string
		want bool
	}{
		{name: "casual admin greeting", msg: "Haloww min", want: true},
		{name: "simple greeting", msg: "halo", want: true},
		{name: "time greeting", msg: "Selamat pagi kak", want: true},
		{name: "business question with greeting", msg: "halo, tolong analisa omzet saya", want: false},
		{name: "direct business question", msg: "apa margin saya sehat?", want: false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := isGreetingOnly(tt.msg); got != tt.want {
				t.Fatalf("isGreetingOnly(%q) = %v, want %v", tt.msg, got, tt.want)
			}
		})
	}
}

func TestRecommendMentorsReturnsTopRelevantMentor(t *testing.T) {
	profile := &business.Profile{
		BusinessName: "Cookusbox",
		BusinessType: "F&B / Kuliner",
		MainProblem:  "Ingin scale omzet dari Rp1,3 juta ke Rp3 juta",
	}
	mentors := []mentor.Mentor{
		{
			Name:        "Agus Prasetyo",
			Expertise:   "Digital Marketing & E-Commerce",
			Description: "Membantu UMKM masuk ke era digital.",
			BookingURL:  "https://example.com/agus",
		},
		{
			Name:        "Budi Santoso",
			Expertise:   "F&B & Kuliner",
			Description: "Membantu UMKM kuliner meningkatkan profitabilitas dan memperluas jangkauan pasar.",
			BookingURL:  "https://example.com/budi",
		},
		{
			Name:        "Dewi Kusuma",
			Expertise:   "Keuangan & Pembukuan UMKM",
			Description: "Membantu pemilik usaha memahami laporan keuangan.",
			BookingURL:  "https://example.com/dewi",
		},
	}

	cards := recommendMentors("bisa carikan mentor?", profile, mentors, 1)
	if len(cards) != 1 {
		t.Fatalf("len(cards) = %d, want 1", len(cards))
	}
	if cards[0].Name != "Budi Santoso" {
		t.Fatalf("recommended mentor = %q, want Budi Santoso", cards[0].Name)
	}
	if cards[0].Reason == "" {
		t.Fatal("recommended mentor should include a reason")
	}
}

func TestRecommendMentorsHonorsExplicitUserDomain(t *testing.T) {
	profile := &business.Profile{
		BusinessName: "Cookusbox",
		BusinessType: "F&B / Kuliner",
		MainProblem:  "Ingin scale omzet dari Rp1,3 juta ke Rp3 juta",
	}
	mentors := []mentor.Mentor{
		{
			Name:        "Budi Santoso",
			Expertise:   "F&B & Kuliner",
			Description: "Membantu UMKM kuliner meningkatkan profitabilitas.",
			BookingURL:  "https://example.com/budi",
		},
		{
			Name:        "Dewi Kusuma",
			Expertise:   "Keuangan & Pembukuan UMKM",
			Description: "Membantu pemilik usaha memahami laporan keuangan.",
			BookingURL:  "https://example.com/dewi",
		},
	}

	cards := recommendMentors("saya butuh mentor pembukuan dan keuangan", profile, mentors, 1)
	if len(cards) != 1 {
		t.Fatalf("len(cards) = %d, want 1", len(cards))
	}
	if cards[0].Name != "Dewi Kusuma" {
		t.Fatalf("recommended mentor = %q, want Dewi Kusuma", cards[0].Name)
	}
}
