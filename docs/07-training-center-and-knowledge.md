# 07 Training Center and Knowledge

## Goal

Training Center memungkinkan admin/researcher meningkatkan kualitas assistant tanpa fine-tuning terlebih dahulu.

Admin bisa menambahkan:

- Knowledge bisnis
- Research notes
- Contoh pertanyaan dan jawaban ideal
- Rules/persona
- Skills/tools
- Feedback jawaban bot

## Knowledge input form

Fields:

```text
title
category
business_category
location
summary/content
source_type
source_url
confidence_score
valid_until
```

## Knowledge categories

```text
market_price
supplier
competitor
trend
pricing_strategy
margin_strategy
restock_strategy
general_business
```

## Researcher workflow

```text
Researcher inputs note
↓
Knowledge stored as draft
↓
Admin reviews/approves
↓
Knowledge becomes active
↓
Embedding generated optional
↓
AI can retrieve it during answer generation
```

## Response examples

Admin can add examples:

```text
Question:
Harga ayam naik, saya harus naikin harga jual nggak?

Ideal answer:
Kalau HPP naik lebih dari 10%, cek ulang margin dulu. Jika target margin 30% dan harga jual sekarang sudah tipis, naik Rp1.000-Rp2.000 bisa lebih sehat daripada menahan harga tapi margin habis.
```

## Bot rules

Examples:

```text
Always answer in Indonesian.
Use friendly UMKM tone.
Avoid long theoretical explanation.
Always include actionable next step.
If data is missing, ask one focused question.
Never fabricate exact market prices without evidence.
Mention uncertainty if source is weak.
```

## Skill settings

Skills:

```text
margin_calculator
pricing_advisor
hpp_helper
supplier_finder
trend_monitor
competitor_checker
research_notes_reader
early_warning_agent
```

Skill can be:

- globally active
- active by business category
- active per customer

## Feedback loop

Admin reviews bot answers and marks:

```text
good
wrong
too_long
too_generic
not_actionable
needs_human_review
```

Feedback should be stored and used to improve prompts and training examples.

## Fine-tuning policy

Do not fine-tune in MVP.

Fine-tuning can be considered later if:

- There are at least hundreds/thousands of high-quality examples.
- Prompt + knowledge retrieval is not enough.
- Desired response style is stable.
- Evaluation set already exists.

