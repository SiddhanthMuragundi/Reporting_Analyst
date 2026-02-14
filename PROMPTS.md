# Prompts Documentation

This document contains all prompts used in the Research Portal API, along with design rationale and examples.

---

## 1. Financial Statement Extraction - Primary Prompt

### Purpose
Extract structured financial data from PDF reports with high accuracy and completeness.

### Prompt Text
```
Extract financial statement data from this document and provide it in a structured JSON format.

CRITICAL REQUIREMENTS:
1. Extract ALL line items from the Income Statement/Profit & Loss statement
2. Include ALL periods/years present in the document
3. For each line item, extract:
   - Line item name (standardized)
   - Values for each period (with proper numeric format)
   - Currency and units (if mentioned)
4. Handle missing values explicitly as null
5. Identify the currency and scale (e.g., INR Crores, USD Millions)

Return ONLY a JSON object with this structure:
{
    "currency": "string (e.g., INR)",
    "scale": "string (e.g., Crores, Millions)",
    "periods": ["Q3FY26", "Q3FY25", ...],
    "line_items": [
        {
            "name": "Revenue from Operations",
            "values": [1234.56, 1100.23, ...],
            "category": "Revenue/Expense/Profit"
        }
    ]
}

IMPORTANT: Return ONLY the JSON, no markdown formatting, no explanation text.
```

### Design Rationale

**1. "CRITICAL REQUIREMENTS" Section**
- Uses strong language to emphasize importance
- Explicitly states to extract ALL items (prevents partial extraction)
- Breaks down requirements into numbered list for clarity

**2. Structured JSON Schema**
- Provides exact expected structure
- Includes example values for clarity
- Specifies data types (string, array, number)

**3. "Return ONLY JSON"**
- Prevents markdown code blocks (```json)
- Avoids explanatory preambles
- Ensures clean parsing

**4. Specific Field Requirements**
- `currency`: Captures INR, USD, etc.
- `scale`: Captures Crores, Millions, etc. (critical for Indian financials)
- `periods`: Array format allows multiple quarters/years
- `category`: Helps organize line items in Excel

### Example Output
```json
{
    "currency": "INR",
    "scale": "Crores",
    "periods": ["Q3FY26", "Q3FY25", "9MFY26", "9MFY25"],
    "line_items": [
        {
            "name": "Revenue from Operations",
            "values": [2234.56, 2100.23, 6543.21, 6234.11],
            "category": "Revenue"
        },
        {
            "name": "Operating Expenses",
            "values": [1234.56, 1100.23, 3543.21, 3234.11],
            "category": "Expense"
        },
        {
            "name": "EBITDA",
            "values": [456.78, 423.45, 1234.56, 1123.45],
            "category": "Profit"
        }
    ]
}
```

---

## 2. Financial Statement Extraction - OCR Backup Prompt

### Purpose
Fallback extraction when primary method fails. More lenient but still structured.

### Prompt Text
```
This is an OCR backup extraction. Extract financial data even if the structure is imperfect.

Focus on finding:
1. Revenue/Sales figures
2. Expenses (Operating, Admin, etc.)
3. Profit figures (Operating, Net, EBITDA)
4. Any time periods mentioned

Return as JSON:
{
    "currency": "best guess",
    "scale": "best guess",
    "periods": ["extracted periods"],
    "line_items": [
        {"name": "item name", "values": [numbers], "category": "Revenue/Expense/Profit"}
    ]
}

Return ONLY JSON, no markdown.
```

### Design Rationale

**1. Acknowledges Context**
- States "OCR backup" to set expectations
- Allows for imperfect structure

**2. Simplified Focus**
- Only asks for core metrics (Revenue, Expenses, Profit)
- Reduces chance of complete failure

**3. "Best Guess" Flexibility**
- Allows estimation for currency/scale
- Better than failing entirely

**4. Maintains JSON Structure**
- Keeps same format as primary for consistent parsing
- Ensures downstream code works

### When This Triggers
- Primary extraction fails 3 times
- JSON parsing errors occur
- Response contains invalid structure

---

## 3. Earnings Call Summary - Primary Prompt

### Purpose
Extract structured insights from earnings call transcripts without hallucination.

### Prompt Text
```
Analyze this earnings call transcript and provide a structured summary.

REQUIREMENTS:
1. Management Tone/Sentiment: optimistic, cautious, neutral, or pessimistic (choose ONE)
2. Confidence Level: high, medium, or low (choose ONE)
3. Key Positives: List 3-5 specific positive points mentioned
4. Key Concerns/Challenges: List 3-5 specific concerns or challenges
5. Forward Guidance: Extract any revenue, margin, or capex outlook mentioned
6. Capacity Utilization: Extract any trends or mentions
7. Growth Initiatives: List 2-3 new initiatives described

CRITICAL: Base your analysis ONLY on what is explicitly stated in the transcript. Do not infer or hallucinate information.

Return ONLY a JSON object:
{
    "management_tone": "optimistic/cautious/neutral/pessimistic",
    "confidence_level": "high/medium/low",
    "key_positives": ["point 1", "point 2", ...],
    "key_concerns": ["concern 1", "concern 2", ...],
    "forward_guidance": {
        "revenue": "specific guidance or 'Not mentioned'",
        "margin": "specific guidance or 'Not mentioned'",
        "capex": "specific guidance or 'Not mentioned'"
    },
    "capacity_utilization": "specific mention or 'Not mentioned'",
    "growth_initiatives": ["initiative 1", "initiative 2", ...]
}

Return ONLY the JSON, no markdown, no explanations.
```

### Design Rationale

**1. Limited Choice Sets**
- `management_tone`: Exactly 4 options prevents confusion
- `confidence_level`: Exactly 3 options for clear categorization
- Forces selection, avoids vague responses

**2. Specific Quantities**
- "3-5" for positives/concerns prevents too many/few items
- "2-3" for initiatives keeps it focused
- Balances completeness with conciseness

**3. Anti-Hallucination Measures**
- "CRITICAL: Base your analysis ONLY on what is explicitly stated"
- "Not mentioned" as explicit option prevents fabrication
- "specific guidance or 'Not mentioned'" format

**4. Nested Structure for Guidance**
- Separate fields for revenue, margin, capex
- Each can be individually "Not mentioned"
- Prevents single missing field from breaking entire guidance

### Example Output
```json
{
    "management_tone": "optimistic",
    "confidence_level": "high",
    "key_positives": [
        "Strong volume growth in Parachute brand despite pricing actions",
        "Successful turnaround in Vietnam and South Africa businesses",
        "Market share gains in value-added hair oils (30% value share)",
        "Investment in 4700BC brand showing early traction",
        "Digital-first portfolio expansion progressing well"
    ],
    "key_concerns": [
        "Elevated copra prices impacting gross margins",
        "Inflationary headwinds in rural markets affecting demand",
        "Foods portfolio growth paused for profitability improvement",
        "Saffola Edible Oil volumes below threshold margins"
    ],
    "forward_guidance": {
        "revenue": "Mid-teens growth expected in coming quarters",
        "margin": "150-200 basis points operating margin expansion targeted",
        "capex": "Not mentioned"
    },
    "capacity_utilization": "Improved quality of rural distribution through Project SETU",
    "growth_initiatives": [
        "Investment in 4700BC premium gourmet snacking brand (INR 140 crores ARR target)",
        "Expansion in modern trade and premium food outlets",
        "Digital-first portfolio scaling (Beardo, True Elements)"
    ]
}
```

---

## Prompt Engineering Techniques Used

### 1. Structured Output Enforcement
- Provide exact JSON schema
- Use quotes around expected values
- Specify data types implicitly through examples

### 2. Explicit Instructions
- "Return ONLY JSON" (no markdown)
- "no explanations" (prevents preambles)
- "choose ONE" (prevents multiple answers)

### 3. Anti-Hallucination
- "ONLY on what is explicitly stated"
- "Not mentioned" as valid option
- "specific" before every request

### 4. Categorization Aids
- Limited choice sets (optimistic/cautious/neutral/pessimistic)
- Clear buckets (Revenue/Expense/Profit)
- Numeric ranges (3-5 items)

### 5. Fallback Strategies
- Primary prompt → OCR backup
- "best guess" in backup prompts
- Simplified requirements on retry

---

## Retry Logic Flow

### Financial Extraction
```
Attempt 1: Primary Prompt
    ↓ (if fails)
Attempt 2: Primary Prompt (retry)
    ↓ (if fails)
Attempt 3: Primary Prompt (retry)
    ↓ (if fails)
OCR Backup Prompt
    ↓ (if fails)
Return Failure
```

### Earnings Call Summary
```
Attempt 1: Primary Prompt
    ↓ (if JSON parse fails)
Attempt 2: Primary Prompt (retry)
    ↓ (if JSON parse fails)
Attempt 3: Primary Prompt (retry)
    ↓ (if fails)
Return Failure
```

**Key Difference**: 
- Financial extraction has OCR backup
- Earnings summary has no meaningful fallback (interpretation is binary)

---

## Common Failure Modes & Mitigations

### Problem 1: Markdown Code Blocks
**Issue**: Claude returns ```json ... ``` instead of pure JSON

**Solution**: Post-processing cleanup
```python
if response_text.startswith("```json"):
    response_text = response_text.split("```json")[1].split("```")[0].strip()
```

### Problem 2: Explanatory Preambles
**Issue**: "Here's the extracted data: {...}"

**Solution**: 
- Explicit "Return ONLY JSON" instruction
- Attempt to find JSON object in response
- Retry with more explicit prompt

### Problem 3: Hallucinated Values
**Issue**: Making up guidance that wasn't mentioned

**Solution**:
- "CRITICAL: Base your analysis ONLY on what is explicitly stated"
- Require "Not mentioned" as valid value
- Multiple retries to enforce

### Problem 4: Inconsistent Units
**Issue**: Mixing Crores and Millions in same response

**Solution**:
- Extract currency and scale separately
- Validate all values are in same scale
- Retry if inconsistent

---

## Prompt Testing & Validation

### Testing Checklist
- [ ] Returns valid JSON (no markdown)
- [ ] All required fields present
- [ ] No hallucinated information
- [ ] Consistent units/currency
- [ ] "Not mentioned" used appropriately
- [ ] Arrays have 3-5 items (where specified)
- [ ] Tone/confidence from limited set

### Sample Test Cases

**Test 1**: Document with complete data
- Expected: All fields populated
- Validation: Check no "Not mentioned" for available data

**Test 2**: Document missing guidance
- Expected: "Not mentioned" in forward_guidance fields
- Validation: Ensure no fabricated numbers

**Test 3**: Multi-year financial data
- Expected: All years in periods array
- Validation: Check period count matches document

**Test 4**: Transcript with vague guidance
- Expected: Capture exact wording (e.g., "gradual improvement")
- Validation: No conversion to specific percentages

---

## Customization Guide

### To Add New Line Items
Modify the financial extraction prompt:
```
3. For each line item, extract:
   - Line item name (standardized)
   - Values for each period
   - Currency and units
   + New field: "note" for any annotations
```

### To Add New Summary Fields
Modify the earnings call prompt:
```json
{
    ...existing fields...,
    "competitor_mentions": ["company 1", "company 2"],
    "regulatory_concerns": "specific concerns or 'Not mentioned'"
}
```

### To Change Retry Count
In `main.py`:
```python
max_retries = 3  # Change to 5, 10, etc.
```

**Trade-off**: More retries = more API calls = higher cost

---

## Cost Optimization

### Prompt Length
- Current prompts: ~400 tokens
- PDF processing: ~2000-5000 tokens input
- Response: ~500-1000 tokens

**Estimated Cost per Request**: $0.01 - $0.03 (Claude Sonnet 4)

### Optimization Strategies
1. **Reduce retry attempts**: 3→2 saves 33% on failures
2. **Compress prompts**: Remove examples if not needed
3. **Batch processing**: Process multiple files in single session
4. **Use Claude Haiku**: 10x cheaper but less accurate

---

## Version History

### v1.0 (Current)
- Primary financial extraction prompt
- OCR backup prompt
- Earnings call summary prompt
- 3-attempt retry logic

### Future Enhancements
- [ ] Comparative analysis prompt (multiple transcripts)
- [ ] Trend detection prompt (multi-quarter)
- [ ] Risk assessment prompt
- [ ] Competitor benchmarking prompt

---

## References

- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)
- [JSON Schema for Validation](https://json-schema.org/)
- Assignment Requirements: `Tech_Intern_L2_Assignment.pdf`
