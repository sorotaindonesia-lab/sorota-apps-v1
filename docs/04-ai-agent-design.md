# 04 AI Agent Design

## Principle

Do not fine-tune first. Build a training layer with:

- Prompt templates
- Knowledge base
- Training examples
- Rules
- Skills/tools
- Feedback
- Usage logging

## AI gateway

All OpenAI calls must go through one gateway.

Suggested files:

```text
backend/app/ai/gateway.py
backend/app/ai/prompts/intent_router.md
backend/app/ai/prompts/business_profiler.md
backend/app/ai/prompts/memory_extractor.md
backend/app/ai/prompts/answer_composer.md
backend/app/ai/prompts/admin_query_parser.md
backend/app/ai/prompts/early_warning_composer.md
```

Do not call OpenAI directly from controllers.

## Agent/task separation

### 1. Intent Router

Input:

- customer message
- active conversation state
- small customer context

Output JSON:

```json
{
  "intent": "pricing_advice",
  "confidence": 0.91,
  "required_tools": ["calculate_margin"],
  "missing_data": ["hpp"],
  "should_answer_now": true
}
```

### 2. Business Profiler

Input:

- customer message
- current profiling state
- known profile fields

Output JSON:

```json
{
  "extracted_fields": {
    "business_name": "Ayam Geprek Mas Budi",
    "business_category": "kuliner",
    "business_subcategory": "warung makan",
    "location": "Bandung",
    "main_products": ["ayam geprek", "es teh"]
  },
  "missing_fields": ["hpp", "target_margin_percent"],
  "next_question": "Produk utama yang paling sering dijual apa, Kak?"
}
```

### 3. Memory Extractor

Input:

- latest customer message
- assistant response
- known memory

Output JSON:

```json
{
  "memories": [
    {
      "memory_key": "target_margin_percent",
      "memory_value": 30,
      "confidence": 0.9
    }
  ]
}
```

### 4. Answer Composer

Input:

- user question
- business profile
- products
- relevant knowledge
- tool results
- active rules
- active examples

Output:

Natural WhatsApp answer in Indonesian.

Response style:

- Short
- Practical
- Friendly
- Explain calculation if there is number
- Always include clear next action
- If data missing, ask one focused question

### 5. Admin Query Parser

Input:

Admin dashboard command, e.g.

```text
Cek customer kuliner yang belum aktif minggu ini.
```

Output JSON:

```json
{
  "intent": "customer_search",
  "filters": {
    "business_category": "kuliner",
    "status": "inactive",
    "period": "this_week"
  },
  "needs_confirmation": false
}
```

### 6. Early Warning Composer

Input:

- warning candidate
- customer business profile
- evidence
- rule

Output:

```json
{
  "title": "Harga bahan ayam berpotensi naik",
  "severity": "warning",
  "message": "Kak, ada indikasi harga ayam naik di area sekitar. Kalau HPP ayam geprek ikut naik, cek ulang margin agar harga jual tetap sehat.",
  "action_items": [
    "Cek HPP ayam geprek hari ini",
    "Bandingkan harga supplier alternatif",
    "Pertimbangkan naik harga Rp1.000-Rp2.000 jika margin turun di bawah target"
  ]
}
```

## Model usage strategy

- Use small/cheap model for routing and extraction.
- Use stronger model for final answer and complex reasoning.
- Use deterministic code for calculations.
- Never use AI for simple arithmetic.
- Log all AI usage.

## Skill/tool contract

### Margin Calculator

Input:

```json
{
  "selling_price": 18000,
  "hpp": 11500
}
```

Output:

```json
{
  "margin_amount": 6500,
  "margin_percent": 36.11,
  "status": "healthy",
  "recommendation": "Margin masih aman jika target 30%."
}
```

### Recommend Price

Input:

```json
{
  "hpp": 11500,
  "target_margin_percent": 30
}
```

Output:

```json
{
  "minimum_price": 16429,
  "recommended_price_range": [17000, 19000],
  "explanation": "Harga minimal untuk margin 30% sekitar Rp16.429."
}
```

