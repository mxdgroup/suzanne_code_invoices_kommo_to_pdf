#!/usr/bin/env python3
"""
FastAPI Invoice Generator & Email Sender
Generates PDF invoices from JSON and sends via Resend
"""
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
import resend
import tempfile
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import invoice generation modules from the same directory
from generate_invoice import generate_html, calculate_item_totals
from generate_proforma_invoice import generate_proforma_html, calculate_proforma_totals
from generate_tax_invoice import generate_tax_invoice_html
from convert_to_pdf import html_to_pdf
from mongodb_helper import get_db_helper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Invoice Generator API",
    description="Generate and send PDF invoices via email",
    version="1.0.0"
)

# Load environment variables
API_SECRET_TOKEN = os.getenv("API_SECRET_TOKEN")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "invoices@yourdomain.com")

if not API_SECRET_TOKEN:
    logger.warning("⚠️  API_SECRET_TOKEN not set! Using default (INSECURE)")
    API_SECRET_TOKEN = "your-secret-token-here"

if not RESEND_API_KEY:
    logger.error("❌ RESEND_API_KEY not set!")

# Configure Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Pydantic models for request validation
class InvoiceInfo(BaseModel):
    number: str
    date_of_issuing: str
    date_of_supply: str

class IssuedTo(BaseModel):
    name: str
    address: str
    trn: Optional[str] = ""
    tel: Optional[str] = ""
    email: str

class Terms(BaseModel):
    payment_terms: str
    delivery_terms: Optional[str] = ""

class Item(BaseModel):
    description: str
    quantity: float
    uom: str
    price_aed: float
    discount_pct: float = 0
    vat_pct: float = 5
    rate_usd: float = 3.6725

class InvoiceRequest(BaseModel):
    invoice: InvoiceInfo
    issued_to: IssuedTo
    terms: Terms
    items: List[Item]
    supply_total_text: str
    recipient_emails: List[EmailStr]  # List of emails to send invoice to

# Proforma Invoice Models
class ProformaInvoiceInfo(BaseModel):
    number: str
    date_of_issuing: str
    deal_number: str

class ProformaIssuedTo(BaseModel):
    name: str
    address: str
    trn: Optional[str] = ""
    email: str

class ProformaTerms(BaseModel):
    payment_terms: str
    amount_paid: str

class ProformaItem(BaseModel):
    description: str
    sub_description: Optional[str] = ""
    quantity: float
    uom: str
    price_incl_vat_aed: float  # Price already includes VAT
    discount_pct: float = 0
    vat_pct: float = 5

class ProformaInvoiceRequest(BaseModel):
    invoice: ProformaInvoiceInfo
    issued_to: ProformaIssuedTo
    terms: ProformaTerms
    items: List[ProformaItem]
    amount_in_words: Optional[str] = None  # Optional - will be auto-generated if not provided
    recipient_emails: List[EmailStr]  # List of emails to send invoice to

# Tax Invoice Models (for updating proforma to tax invoice)
class TaxInvoiceInfo(BaseModel):
    number: str
    date_of_issuing: str
    deal_number: str

class TaxInvoiceRequest(BaseModel):
    invoice: TaxInvoiceInfo

# Token validation
def verify_token(authorization: Optional[str] = Header(None)):
    """Verify API token from Authorization header"""
    if not authorization:
        logger.warning("❌ Missing Authorization header")
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    # Support both "Bearer <token>" and plain token
    token = authorization.replace("Bearer ", "").strip()
    
    if token != API_SECRET_TOKEN:
        logger.warning(f"❌ Invalid token attempted: {token[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    return True

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Invoice Generator API",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    """Detailed health check"""
    return {
        "status": "ok",
        "resend_configured": bool(RESEND_API_KEY),
        "token_configured": bool(API_SECRET_TOKEN and API_SECRET_TOKEN != "your-secret-token-here")
    }

@app.post("/generate-invoice")
async def generate_invoice(
    request: InvoiceRequest,
    authorized: bool = Depends(verify_token)
):
    """
    Generate PDF invoice and send via email
    
    Requires Authorization header with secret token
    """
    try:
        logger.info(f"📄 Generating invoice: {request.invoice.number}")
        
        # Create temporary directory for this invoice
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate filenames based on invoice number
            invoice_number_clean = request.invoice.number.replace("/", "-").replace(" ", "_")
            json_file = os.path.join(temp_dir, f"{invoice_number_clean}.json")
            html_file = os.path.join(temp_dir, f"{invoice_number_clean}.html")
            pdf_file = os.path.join(temp_dir, f"{invoice_number_clean}.pdf")
            
            # Save JSON to file
            import json
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(request.dict(exclude={'recipient_emails'}), f, indent=2)
            
            # Generate HTML
            logger.info("  📝 Generating HTML...")
            generate_html(json_file, html_file)
            
            # Generate PDF
            logger.info("  📄 Converting to PDF...")
            html_to_pdf(html_file, pdf_file)
            
            # Verify PDF file was created
            if not os.path.exists(pdf_file):
                raise Exception(f"PDF file was not created at {pdf_file}")
            
            # Get PDF file size
            pdf_size_kb = os.path.getsize(pdf_file) / 1024
            logger.info(f"  ✓ PDF generated: {pdf_size_kb:.1f} KB")
            
            # Send via Resend
            if not RESEND_API_KEY:
                raise HTTPException(
                    status_code=500,
                    detail="RESEND_API_KEY not configured"
                )
            
            # Read PDF file as bytes
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()
            
            # Calculate totals for email body
            totals = calculate_item_totals([item.dict() for item in request.items])
            
            # Send email to each recipient
            sent_to = []
            for recipient_email in request.recipient_emails:
                logger.info(f"  📧 Sending to: {recipient_email}")
                
                params = {
                    "from": FROM_EMAIL,
                    "to": [recipient_email],
                    "subject": f"Invoice {request.invoice.number} - {request.issued_to.name}",
                    "html": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #333;">Tax Invoice</h2>
                        <p>Dear {request.issued_to.name},</p>
                        <p>Please find attached your tax invoice.</p>
                        
                        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <strong>Invoice Number:</strong> {request.invoice.number}<br/>
                            <strong>Date of Issuing:</strong> {request.invoice.date_of_issuing}<br/>
                            <strong>Total Amount (AED):</strong> {totals['total_aed']}<br/>
                            <strong>Total Amount (USD):</strong> {totals['total_usd']}
                        </div>
                        
                        <p>Thank you for your business.</p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;" />
                        <p style="color: #666; font-size: 12px;">
                            <strong>SUZANNE CODE JEWELLERY TRADING L.L.C.</strong><br/>
                            Shop B5-OF-05, Burj Khalifa, Dubai, UAE<br/>
                            TRN: 104644174200003
                        </p>
                    </div>
                    """,
                    "attachments": [
                        {
                            "filename": f"Invoice_{invoice_number_clean}.pdf",
                            "content": list(pdf_data)
                        }
                    ]
                }
                
                # Send email
                email_response = resend.Emails.send(params)
                sent_to.append(recipient_email)
                logger.info(f"  ✓ Email sent to {recipient_email} (ID: {email_response.get('id', 'N/A')})")
            
            return {
                "status": "success",
                "message": "Invoice generated and sent successfully",
                "invoice_number": request.invoice.number,
                "pdf_filename": f"Invoice_{invoice_number_clean}.pdf",
                "pdf_size_kb": round(pdf_size_kb, 2),
                "emails_sent_to": sent_to,
                "total_aed": totals['total_aed'],
                "total_usd": totals['total_usd']
            }
    
    except Exception as e:
        logger.error(f"❌ Error generating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating invoice: {str(e)}")

@app.post("/generate-proforma-invoice")
async def generate_proforma_invoice(
    request: ProformaInvoiceRequest,
    authorized: bool = Depends(verify_token)
):
    """
    Generate PDF proforma invoice and send via email
    
    Requires Authorization header with secret token
    """
    try:
        logger.info(f"📄 Generating proforma invoice: {request.invoice.number}")
        
        # Check and update MongoDB
        db_helper = get_db_helper()
        deal_number = request.invoice.deal_number
        
        # Prepare invoice data for database (include ALL fields including recipient_emails)
        invoice_data = request.dict()
        
        # Check if deal number exists and update/insert
        is_new, doc_id = db_helper.upsert_invoice(deal_number, invoice_data)
        
        if is_new:
            logger.info(f"✓ Created new database record for deal number: {deal_number}")
        else:
            logger.info(f"✓ Updated existing database record for deal number: {deal_number}")
        
        # Create temporary directory for this invoice
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate filenames based on invoice number
            invoice_number_clean = request.invoice.number.replace("/", "-").replace(" ", "_")
            json_file = os.path.join(temp_dir, f"{invoice_number_clean}.json")
            html_file = os.path.join(temp_dir, f"{invoice_number_clean}.html")
            pdf_file = os.path.join(temp_dir, f"{invoice_number_clean}.pdf")
            
            # Save JSON to file
            import json
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(request.dict(exclude={'recipient_emails'}), f, indent=2)
            
            # Generate HTML
            logger.info("  📝 Generating HTML...")
            generate_proforma_html(json_file, html_file)
            
            # Generate PDF
            logger.info("  📄 Converting to PDF...")
            html_to_pdf(html_file, pdf_file)
            
            # Verify PDF file was created
            if not os.path.exists(pdf_file):
                raise Exception(f"PDF file was not created at {pdf_file}")
            
            # Get PDF file size
            pdf_size_kb = os.path.getsize(pdf_file) / 1024
            logger.info(f"  ✓ PDF generated: {pdf_size_kb:.1f} KB")
            
            # Send via Resend
            if not RESEND_API_KEY:
                raise HTTPException(
                    status_code=500,
                    detail="RESEND_API_KEY not configured"
                )
            
            # Read PDF file as bytes
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()
            
            # Calculate totals for email body
            totals = calculate_proforma_totals([item.dict() for item in request.items])
            
            # Send email to each recipient
            sent_to = []
            for recipient_email in request.recipient_emails:
                logger.info(f"  📧 Sending to: {recipient_email}")
                
                params = {
                    "from": FROM_EMAIL,
                    "to": [recipient_email],
                    "subject": f"Proforma Invoice {request.invoice.number} - {request.issued_to.name}",
                    "html": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #333;">Proforma Invoice</h2>
                        <p>Dear {request.issued_to.name},</p>
                        <p>Please find attached your proforma invoice.</p>
                        
                        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <strong>Invoice Number:</strong> {request.invoice.number}<br/>
                            <strong>Date of Issuing:</strong> {request.invoice.date_of_issuing}<br/>
                            <strong>Total Amount (AED):</strong> {totals['total_incl_vat']}<br/>
                        </div>
                        
                        <p>Thank you for your business.</p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;" />
                        <p style="color: #666; font-size: 12px;">
                            <strong>SUZANNE CODE JEWELLERY TRADING L.L.C.</strong><br/>
                            Shop BF-05, Burj Khalifa, Dubai, UAE<br/>
                            TRN: 104644174200003
                        </p>
                    </div>
                    """,
                    "attachments": [
                        {
                            "filename": f"ProformaInvoice_{invoice_number_clean}.pdf",
                            "content": list(pdf_data)
                        }
                    ]
                }
                
                # Send email
                email_response = resend.Emails.send(params)
                sent_to.append(recipient_email)
                logger.info(f"  ✓ Email sent to {recipient_email} (ID: {email_response.get('id', 'N/A')})")
            
            return {
                "status": "success",
                "message": "Proforma invoice generated and sent successfully",
                "invoice_number": request.invoice.number,
                "deal_number": deal_number,
                "database_operation": "created" if is_new else "updated",
                "database_record_id": doc_id,
                "pdf_filename": f"ProformaInvoice_{invoice_number_clean}.pdf",
                "pdf_size_kb": round(pdf_size_kb, 2),
                "emails_sent_to": sent_to,
                "total_aed": totals['total_incl_vat']
            }
    
    except Exception as e:
        logger.error(f"❌ Error generating proforma invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating proforma invoice: {str(e)}")

@app.post("/generate-tax-invoice")
async def generate_tax_invoice(
    request: TaxInvoiceRequest,
    authorized: bool = Depends(verify_token)
):
    """
    Generate PDF tax invoice from existing proforma invoice in MongoDB
    
    Fetches proforma invoice by deal_number, updates invoice number and date,
    generates a TAX INVOICE PDF and sends via email
    
    Requires Authorization header with secret token
    """
    try:
        deal_number = request.invoice.deal_number
        logger.info(f"📄 Generating tax invoice for deal number: {deal_number}")
        
        # Fetch proforma invoice from MongoDB
        db_helper = get_db_helper()
        proforma_doc = db_helper.find_by_deal_number(deal_number)
        
        if not proforma_doc:
            raise HTTPException(
                status_code=404,
                detail=f"No proforma invoice found for deal number: {deal_number}"
            )
        
        logger.info(f"✓ Found proforma invoice for deal number: {deal_number}")
        
        # Get recipient emails from the stored proforma invoice
        recipient_emails = proforma_doc.get('recipient_emails', [])
        if not recipient_emails:
            raise HTTPException(
                status_code=400,
                detail=f"No recipient emails found in proforma invoice for deal number: {deal_number}"
            )
        
        # Update invoice number and date with new values from request
        proforma_doc['invoice']['number'] = request.invoice.number
        proforma_doc['invoice']['date_of_issuing'] = request.invoice.date_of_issuing
        
        # Remove MongoDB _id and timestamps for processing
        proforma_doc.pop('_id', None)
        proforma_doc.pop('created_at', None)
        proforma_doc.pop('updated_at', None)
        
        # Create temporary directory for this invoice
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate filenames based on invoice number
            invoice_number_clean = request.invoice.number.replace("/", "-").replace(" ", "_")
            json_file = os.path.join(temp_dir, f"{invoice_number_clean}.json")
            html_file = os.path.join(temp_dir, f"{invoice_number_clean}.html")
            pdf_file = os.path.join(temp_dir, f"{invoice_number_clean}.pdf")
            
            # Save updated JSON to file
            import json
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(proforma_doc, f, indent=2)
            
            # Generate HTML (using tax invoice template)
            logger.info("  📝 Generating tax invoice HTML...")
            generate_tax_invoice_html(json_file, html_file)
            
            # Generate PDF
            logger.info("  📄 Converting to PDF...")
            html_to_pdf(html_file, pdf_file)
            
            # Verify PDF file was created
            if not os.path.exists(pdf_file):
                raise Exception(f"PDF file was not created at {pdf_file}")
            
            # Get PDF file size
            pdf_size_kb = os.path.getsize(pdf_file) / 1024
            logger.info(f"  ✓ PDF generated: {pdf_size_kb:.1f} KB")
            
            # Send via Resend
            if not RESEND_API_KEY:
                raise HTTPException(
                    status_code=500,
                    detail="RESEND_API_KEY not configured"
                )
            
            # Read PDF file as bytes
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()
            
            # Calculate totals for email body
            totals = calculate_proforma_totals(proforma_doc['items'])
            
            # Send email to each recipient
            sent_to = []
            for recipient_email in recipient_emails:
                logger.info(f"  📧 Sending to: {recipient_email}")
                
                params = {
                    "from": FROM_EMAIL,
                    "to": [recipient_email],
                    "subject": f"Tax Invoice {request.invoice.number} - {proforma_doc['issued_to']['name']}",
                    "html": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #333;">Tax Invoice</h2>
                        <p>Dear {proforma_doc['issued_to']['name']},</p>
                        <p>Please find attached your tax invoice.</p>
                        
                        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <strong>Invoice Number:</strong> {request.invoice.number}<br/>
                            <strong>Date of Issuing:</strong> {request.invoice.date_of_issuing}<br/>
                            <strong>Deal Number:</strong> {deal_number}<br/>
                            <strong>Total Amount (AED):</strong> {totals['total_incl_vat']}<br/>
                        </div>
                        
                        <p>Thank you for your business.</p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;" />
                        <p style="color: #666; font-size: 12px;">
                            <strong>SUZANNE CODE JEWELLERY TRADING L.L.C.</strong><br/>
                            Shop BF-05, Burj Khalifa, Dubai, UAE<br/>
                            TRN: 104644174200003
                        </p>
                    </div>
                    """,
                    "attachments": [
                        {
                            "filename": f"TaxInvoice_{invoice_number_clean}.pdf",
                            "content": list(pdf_data)
                        }
                    ]
                }
                
                # Send email
                email_response = resend.Emails.send(params)
                sent_to.append(recipient_email)
                logger.info(f"  ✓ Email sent to {recipient_email} (ID: {email_response.get('id', 'N/A')})")
            
            return {
                "status": "success",
                "message": "Tax invoice generated and sent successfully",
                "invoice_number": request.invoice.number,
                "deal_number": deal_number,
                "pdf_filename": f"TaxInvoice_{invoice_number_clean}.pdf",
                "pdf_size_kb": round(pdf_size_kb, 2),
                "emails_sent_to": sent_to,
                "total_aed": totals['total_incl_vat']
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating tax invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating tax invoice: {str(e)}")

@app.post("/test-token")
def test_token(authorized: bool = Depends(verify_token)):
    """Test endpoint to verify your token works"""
    return {
        "status": "success",
        "message": "Token is valid! ✓"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

