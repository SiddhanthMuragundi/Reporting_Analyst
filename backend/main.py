"""
Research Portal Backend - FastAPI Implementation
Implements financial statement extraction and earnings call summary tools
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import anthropic
import os
import base64
import pandas as pd
from datetime import datetime
import json
import traceback

app = FastAPI(title="Research Portal API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Response models
class FinancialExtractionResponse(BaseModel):
    status: str
    file_path: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EarningsCallSummaryResponse(BaseModel):
    status: str
    management_tone: Optional[str] = None
    confidence_level: Optional[str] = None
    key_positives: Optional[List[str]] = None
    key_concerns: Optional[List[str]] = None
    forward_guidance: Optional[Dict[str, str]] = None
    capacity_utilization: Optional[str] = None
    growth_initiatives: Optional[List[str]] = None
    error: Optional[str] = None

# Helper function to convert PDF to base64
def pdf_to_base64(file_content: bytes) -> str:
    """Convert PDF bytes to base64 string"""
    return base64.standard_b64encode(file_content).decode('utf-8')

# Financial Statement Extraction Tool
@app.post("/api/extract-financials", response_model=FinancialExtractionResponse)
async def extract_financials(file: UploadFile = File(...)):
    """
    Extract financial statement data from uploaded PDF and generate Excel file
    Implements retry logic with feedback loop
    """
    try:
        # Read file content
        file_content = await file.read()
        pdf_base64 = pdf_to_base64(file_content)
        
        # Attempt extraction with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} of {max_retries}")
                
                # Call Claude API for extraction
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
                                        "data": pdf_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": """Extract financial statement data from this document and provide it in a structured JSON format.

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

IMPORTANT: Return ONLY the JSON, no markdown formatting, no explanation text."""
                                }
                            ]
                        }
                    ]
                )
                
                # Extract response text
                response_text = response.content[0].text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif response_text.startswith("```"):
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                financial_data = json.loads(response_text)
                
                # Validate structure
                if not all(key in financial_data for key in ["currency", "periods", "line_items"]):
                    raise ValueError("Invalid JSON structure returned")
                
                # Convert to DataFrame and Excel
                df = create_excel_from_json(financial_data, file.filename)
                
                return FinancialExtractionResponse(
                    status="success",
                    file_path=df,
                    metadata={
                        "currency": financial_data.get("currency"),
                        "scale": financial_data.get("scale"),
                        "periods": financial_data.get("periods"),
                        "line_items_count": len(financial_data.get("line_items", []))
                    }
                )
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    # Final attempt - try OCR backup
                    return await extract_financials_ocr_backup(file_content, file.filename)
                continue
                
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                continue
        
        # If all retries failed
        raise HTTPException(status_code=500, detail="Failed to extract financials after 3 attempts")
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()
        return FinancialExtractionResponse(
            status="failed",
            error=f"Failed to extract financials: {str(e)}"
        )

async def extract_financials_ocr_backup(file_content: bytes, filename: str) -> FinancialExtractionResponse:
    """
    OCR backup method using Claude's vision capabilities
    """
    try:
        print("Using OCR backup method")
        pdf_base64 = pdf_to_base64(file_content)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": """This is an OCR backup extraction. Extract financial data even if the structure is imperfect.

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

Return ONLY JSON, no markdown."""
                        }
                    ]
                }
            ]
        )
        
        response_text = response.content[0].text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1].split("```")[0].strip()
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()
        
        financial_data = json.loads(response_text)
        df = create_excel_from_json(financial_data, filename)
        
        return FinancialExtractionResponse(
            status="success",
            file_path=df,
            metadata={
                "method": "OCR backup",
                "currency": financial_data.get("currency"),
                "scale": financial_data.get("scale")
            }
        )
        
    except Exception as e:
        return FinancialExtractionResponse(
            status="failed",
            error=f"OCR backup also failed: {str(e)}"
        )

def create_excel_from_json(financial_data: dict, original_filename: str) -> str:
    """
    Convert JSON financial data to Excel file
    """
    periods = financial_data.get("periods", [])
    line_items = financial_data.get("line_items", [])
    
    # Create DataFrame
    rows = []
    for item in line_items:
        row = {
            "Line Item": item.get("name", ""),
            "Category": item.get("category", "")
        }
        values = item.get("values", [])
        for i, period in enumerate(periods):
            if i < len(values):
                row[period] = values[i]
            else:
                row[period] = None
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Add metadata sheet
    metadata_df = pd.DataFrame([
        ["Currency", financial_data.get("currency", "")],
        ["Scale", financial_data.get("scale", "")],
        ["Source File", original_filename],
        ["Extracted At", datetime.now().isoformat()]
    ])
    
    # Create output directory in root folder if it doesn't exist
    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to Excel
    output_filename = f"financial_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    output_path = os.path.join(output_dir, output_filename)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Financial Data', index=False)
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False, header=False)
    
    return output_path

# Earnings Call Summary Tool
@app.post("/api/summarize-earnings-call", response_model=EarningsCallSummaryResponse)
async def summarize_earnings_call(file: UploadFile = File(...)):
    """
    Generate structured summary from earnings call transcript
    Implements retry logic with feedback loop
    """
    try:
        file_content = await file.read()
        pdf_base64 = pdf_to_base64(file_content)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} of {max_retries}")
                
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
                                        "data": pdf_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": """Analyze this earnings call transcript and provide a structured summary.

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

Return ONLY the JSON, no markdown, no explanations."""
                                }
                            ]
                        }
                    ]
                )
                
                response_text = response.content[0].text.strip()
                
                # Clean markdown if present
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif response_text.startswith("```"):
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                summary_data = json.loads(response_text)
                
                # Validate structure
                required_keys = ["management_tone", "confidence_level", "key_positives", "key_concerns"]
                if not all(key in summary_data for key in required_keys):
                    raise ValueError("Invalid JSON structure")
                
                return EarningsCallSummaryResponse(
                    status="success",
                    management_tone=summary_data.get("management_tone"),
                    confidence_level=summary_data.get("confidence_level"),
                    key_positives=summary_data.get("key_positives", []),
                    key_concerns=summary_data.get("key_concerns", []),
                    forward_guidance=summary_data.get("forward_guidance", {}),
                    capacity_utilization=summary_data.get("capacity_utilization"),
                    growth_initiatives=summary_data.get("growth_initiatives", [])
                )
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=500, detail="Failed to parse response after 3 attempts")
                continue
                
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                continue
        
        raise HTTPException(status_code=500, detail="Failed after 3 attempts")
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()
        return EarningsCallSummaryResponse(
            status="failed",
            error=f"Failed to summarize earnings call: {str(e)}"
        )

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download generated Excel file
    """
    output_dir = os.path.join(os.getcwd(), "outputs")
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "status": "online",
        "service": "Research Portal API",
        "endpoints": {
            "extract_financials": "/api/extract-financials",
            "summarize_earnings": "/api/summarize-earnings-call",
            "download": "/api/download/{filename}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)