#!/usr/bin/env python3
"""
Kommo API Helper Functions
Fetch leads and prepare proforma invoice data
"""
import os
import requests
import re
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

KOMMO_SUBDOMAIN = os.getenv('KOMMO_SUBDOMAIN')
KOMMO_ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')

# Pipeline and Status IDs
PIPELINE_ID = 11307791  # Main pipeline
GENERATE_PROFORMA_STATUS_ID = 94720975  # "Generate pro forma" status
GENERATE_TAX_INVOICE_STATUS_ID = 95171727  # "Generate tax invoice" status

headers = {
    'Authorization': f'Bearer {KOMMO_ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}


def get_leads_in_status(status_id, limit=250):
    """
    Get leads in a specific status using proper API filter
    
    Uses both pipeline_id and status_id in filter for accurate results
    """
    url = f"https://{KOMMO_SUBDOMAIN}.kommo.com/api/v4/leads"
    
    try:
        all_leads = []
        page = 1
        max_pages = 10  # Safety limit
        
        logger.info(f"Fetching leads in status {status_id}...")
        
        while page <= max_pages:
            # Include BOTH pipeline_id and status_id for filter to work
            params = {
                'filter[pipeline_id]': PIPELINE_ID,
                'filter[statuses][0][pipeline_id]': PIPELINE_ID,
                'filter[statuses][0][status_id]': status_id,
                'with': 'contacts,catalog_elements,tags',
                'limit': limit,
                'page': page
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 204 or not response.text:
                logger.info(f"  No more leads (page {page})")
                break
            
            response.raise_for_status()
            data = response.json()
            
            leads = data.get('_embedded', {}).get('leads', [])
            
            if not leads:
                break
            
            all_leads.extend(leads)
            logger.info(f"  Page {page}: Fetched {len(leads)} leads (Total: {len(all_leads)})")
            
            # Check if there's a next page
            links = data.get('_links', {})
            if 'next' not in links:
                logger.info(f"  No more pages")
                break
            
            page += 1
        
        logger.info(f"✓ Found {len(all_leads)} leads in status {status_id}")
        
        return all_leads
    except Exception as e:
        logger.error(f"Error fetching leads: {e}")
        return []


def has_tag(lead, tag_name):
    """Check if lead has a specific tag"""
    tags = lead.get('_embedded', {}).get('tags', [])
    for tag in tags:
        if tag.get('name', '').lower() == tag_name.lower():
            return True
    return False


def add_tag_to_lead(lead_id, tag_name):
    """Add a tag to a lead (preserves existing tags)"""
    url = f"https://{KOMMO_SUBDOMAIN}.kommo.com/api/v4/leads/{lead_id}"
    
    try:
        # First, get current tags
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        lead = response.json()
        
        existing_tags = []
        if '_embedded' in lead and 'tags' in lead['_embedded']:
            existing_tags = lead['_embedded']['tags']
        
        # Build tag list
        all_tags = []
        for tag in existing_tags:
            if tag.get('id'):
                all_tags.append({'id': tag['id']})
            elif tag.get('name'):
                all_tags.append({'name': tag['name']})
        
        # Add new tag
        all_tags.append({'name': tag_name})
        
        # Update lead with tags
        update_data = {
            '_embedded': {
                'tags': all_tags
            }
        }
        
        response = requests.patch(url, headers=headers, json=update_data)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Could not add tag '{tag_name}' to lead {lead_id}: {e}")
        return False


def get_contact(contact_id):
    """Get full contact details"""
    url = f"https://{KOMMO_SUBDOMAIN}.kommo.com/api/v4/contacts/{contact_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching contact: {e}")
        return None


def get_catalog_element(catalog_id, element_id):
    """Get catalog element details"""
    url = f"https://{KOMMO_SUBDOMAIN}.kommo.com/api/v4/catalogs/{catalog_id}/elements/{element_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching catalog element {element_id}: {e}")
        return None


def get_field_value(custom_fields_values, field_name):
    """Extract value from custom fields by field name"""
    if not custom_fields_values:
        return None
    
    for field in custom_fields_values:
        if field.get('field_name') == field_name:
            values = field.get('values', [])
            if values and isinstance(values[0], dict) and 'value' in values[0]:
                return values[0]['value']
            elif values:
                return values[0]
    
    return None


def get_field_value_by_code(custom_fields_values, field_code):
    """Extract value from custom fields by field code"""
    if not custom_fields_values:
        return None
    
    for field in custom_fields_values:
        if field.get('field_code') == field_code:
            values = field.get('values', [])
            if values and isinstance(values[0], dict) and 'value' in values[0]:
                return values[0]['value']
            elif values:
                return values[0]
    
    return None


def get_product_custom_field(custom_fields_values, field_name):
    """Extract custom field value from product"""
    if not custom_fields_values:
        return None
    
    for field in custom_fields_values:
        if field.get('field_name') == field_name:
            values = field.get('values', [])
            if values and len(values) > 0:
                if isinstance(values[0], dict) and 'value' in values[0]:
                    return values[0]['value']
                else:
                    return values[0]
    
    return None


def generate_invoice_number(lead_id):
    """Generate invoice number based on lead ID"""
    return f"00PI25-{lead_id:08d}"


def format_date(timestamp=None):
    """Format date as 'Month DD, YYYY'"""
    if timestamp:
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = datetime.now()
    
    return dt.strftime("%B %d, %Y")


def extract_discount_percentage(discount_value):
    """Extract discount percentage from discount field value"""
    if not discount_value:
        return 0
    
    discount_str = str(discount_value).upper()
    
    if 'NO DISCOUNT' in discount_str:
        return 0
    # Check longer patterns first to avoid partial matches (e.g., "15%" contains "5%")
    elif '20%' in discount_str or discount_str == '20':
        return 20
    elif '15%' in discount_str or discount_str == '15':
        return 15
    elif '10%' in discount_str or discount_str == '10':
        return 10
    elif '5%' in discount_str or discount_str == '5':
        return 5
    else:
        # Try to extract number using regex
        match = re.search(r'(\d+)', discount_str)
        if match:
            return int(match.group(1))
    
    return 0


def build_proforma_invoice_json(lead, contact, products):
    """Build proforma invoice JSON from lead data"""
    
    lead_id = lead.get('id')
    lead_custom_fields = lead.get('custom_fields_values', [])
    contact_custom_fields = contact.get('custom_fields_values', [])
    
    # Invoice info
    invoice_number = generate_invoice_number(lead_id)
    date_of_issuing = format_date()
    deal_number = str(lead_id)
    
    # Customer info
    customer_name = contact.get('name', '')
    if not customer_name:
        customer_name = lead.get('name', 'Customer')
    
    customer_address = get_field_value(lead_custom_fields, 'Delivery address') or ''
    customer_email = get_field_value_by_code(contact_custom_fields, 'EMAIL') or ''
    customer_trn = get_field_value(contact_custom_fields, 'TRN') or ''
    
    # Payment terms
    payment_terms = get_field_value(lead_custom_fields, 'Payment Terms') or 'Advance payment of 50% before Delivery'
    
    # Amount paid
    payment_type = get_field_value(lead_custom_fields, 'Payment')
    deposit_amount = get_field_value(lead_custom_fields, 'Deposit Amount')
    
    if payment_type and 'deposit' in str(payment_type).lower() and deposit_amount:
        amount_paid = str(deposit_amount)
    else:
        amount_paid = "0"
    
    # Get discount percentage
    discount_value = get_field_value(lead_custom_fields, 'Discount')
    discount_pct = extract_discount_percentage(discount_value)
    
    # Build items list
    items = []
    for product in products:
        # Product name as description
        description = product.get('name', 'Product')
        
        # SKU or product details as sub-description
        product_custom_fields = product.get('custom_fields_values', [])
        sku = get_product_custom_field(product_custom_fields, 'SKU')
        product_details = get_product_custom_field(product_custom_fields, 'Product Details')
        
        sub_description = sku or ''
        if product_details:
            sub_description = f"{sku}, {product_details}" if sku else product_details
        
        # Price (already includes VAT)
        price_str = get_product_custom_field(product_custom_fields, 'Price (AED)') or '0'
        try:
            price_incl_vat_aed = float(str(price_str).replace(',', ''))
        except:
            price_incl_vat_aed = 0.0
        
        # Quantity
        quantity = product.get('quantity', 1)
        try:
            quantity = float(quantity)
        except:
            quantity = 1.0
        
        # Unit of measure
        uom = get_product_custom_field(product_custom_fields, 'Unit') or 'Pcs'
        if not uom or uom == 'N/A':
            uom = 'Pcs'
        
        item = {
            'description': description,
            'sub_description': sub_description,
            'quantity': quantity,
            'uom': uom,
            'price_incl_vat_aed': price_incl_vat_aed,
            'discount_pct': discount_pct,
            'vat_pct': 5
        }
        
        items.append(item)
    
    # Build complete JSON
    invoice_json = {
        'invoice': {
            'number': invoice_number,
            'date_of_issuing': date_of_issuing,
            'deal_number': deal_number
        },
        'issued_to': {
            'name': customer_name,
            'address': customer_address,
            'trn': customer_trn,
            'email': customer_email
        },
        'terms': {
            'payment_terms': payment_terms,
            'amount_paid': amount_paid
        },
        'items': items,
        'recipient_emails': [customer_email] if customer_email else []
    }
    
    return invoice_json


def prepare_lead_for_proforma(lead):
    """Prepare a single lead for proforma invoice generation"""
    lead_id = lead.get('id')
    lead_name = lead.get('name', f'Lead #{lead_id}')
    
    logger.info(f"Processing lead {lead_id}: {lead_name}")
    
    # Get contact details
    contact_links = lead.get('_embedded', {}).get('contacts', [])
    if not contact_links:
        logger.warning(f"  No contact found for lead {lead_id}")
        return None
    
    contact_id = contact_links[0].get('id')
    contact = get_contact(contact_id)
    if not contact:
        logger.warning(f"  Failed to fetch contact {contact_id}")
        return None
    
    # Get products
    catalog_elements = lead.get('_embedded', {}).get('catalog_elements', [])
    if not catalog_elements:
        logger.warning(f"  No products found for lead {lead_id}")
        return None
    
    products = []
    for element in catalog_elements:
        catalog_id = element.get('metadata', {}).get('catalog_id')
        element_id = element.get('id')
        
        if catalog_id and element_id:
            product = get_catalog_element(catalog_id, element_id)
            if product:
                products.append(product)
    
    if not products:
        logger.warning(f"  No valid products found for lead {lead_id}")
        return None
    
    # Build proforma invoice JSON
    invoice_json = build_proforma_invoice_json(lead, contact, products)
    
    return invoice_json


def generate_tax_invoice_number(lead_id):
    """Generate tax invoice number based on lead ID"""
    return f"TAXZS-{lead_id:05d}"


def build_tax_invoice_json(lead, contact, products):
    """Build tax invoice JSON from lead data"""
    
    lead_id = lead.get('id')
    lead_custom_fields = lead.get('custom_fields_values', [])
    contact_custom_fields = contact.get('custom_fields_values', [])
    
    # Invoice info
    invoice_number = generate_tax_invoice_number(lead_id)
    date_of_issuing = format_date()
    deal_number = str(lead_id)
    
    # Customer info
    customer_name = contact.get('name', '')
    if not customer_name:
        customer_name = lead.get('name', 'Customer')
    
    customer_address = get_field_value(lead_custom_fields, 'Delivery address') or ''
    customer_email = get_field_value_by_code(contact_custom_fields, 'EMAIL') or ''
    customer_trn = get_field_value(contact_custom_fields, 'TRN') or ''
    
    # Payment terms - always "Payment on Delivery" for tax invoices
    payment_terms = 'Payment on Delivery'
    
    # Get discount percentage
    discount_value = get_field_value(lead_custom_fields, 'Discount')
    discount_pct = extract_discount_percentage(discount_value)
    
    # Build items list
    items = []
    for product in products:
        # Product name as description
        description = product.get('name', 'Product')
        
        # SKU or product details as sub-description
        product_custom_fields = product.get('custom_fields_values', [])
        sku = get_product_custom_field(product_custom_fields, 'SKU')
        product_details = get_product_custom_field(product_custom_fields, 'Product Details')
        
        sub_description = sku or ''
        if product_details:
            sub_description = f"{sku}, {product_details}" if sku else product_details
        
        # Price (already includes VAT)
        price_str = get_product_custom_field(product_custom_fields, 'Price (AED)') or '0'
        try:
            price_incl_vat_aed = float(str(price_str).replace(',', ''))
        except:
            price_incl_vat_aed = 0.0
        
        # Quantity
        quantity = product.get('quantity', 1)
        try:
            quantity = float(quantity)
        except:
            quantity = 1.0
        
        # Unit of measure
        uom = get_product_custom_field(product_custom_fields, 'Unit') or 'Pcs'
        if not uom or uom == 'N/A':
            uom = 'Pcs'
        
        item = {
            'description': description,
            'sub_description': sub_description,
            'quantity': quantity,
            'uom': uom,
            'price_incl_vat_aed': price_incl_vat_aed,
            'discount_pct': discount_pct,
            'vat_pct': 5
        }
        
        items.append(item)
    
    # Build complete JSON (using same structure as proforma but with different payment terms)
    invoice_json = {
        'invoice': {
            'number': invoice_number,
            'date_of_issuing': date_of_issuing,
            'deal_number': deal_number
        },
        'issued_to': {
            'name': customer_name,
            'address': customer_address,
            'trn': customer_trn,
            'email': customer_email
        },
        'terms': {
            'payment_terms': payment_terms,
            'amount_paid': '0'  # Not used in tax invoices but kept for compatibility
        },
        'items': items,
        'recipient_emails': [customer_email] if customer_email else []
    }
    
    return invoice_json


def prepare_lead_for_tax_invoice(lead):
    """Prepare a single lead for tax invoice generation"""
    lead_id = lead.get('id')
    lead_name = lead.get('name', f'Lead #{lead_id}')
    
    logger.info(f"Processing lead {lead_id}: {lead_name}")
    
    # Get contact details
    contact_links = lead.get('_embedded', {}).get('contacts', [])
    if not contact_links:
        logger.warning(f"  No contact found for lead {lead_id}")
        return None
    
    contact_id = contact_links[0].get('id')
    contact = get_contact(contact_id)
    if not contact:
        logger.warning(f"  Failed to fetch contact {contact_id}")
        return None
    
    # Get products
    catalog_elements = lead.get('_embedded', {}).get('catalog_elements', [])
    if not catalog_elements:
        logger.warning(f"  No products found for lead {lead_id}")
        return None
    
    products = []
    for element in catalog_elements:
        catalog_id = element.get('metadata', {}).get('catalog_id')
        element_id = element.get('id')
        
        if catalog_id and element_id:
            product = get_catalog_element(catalog_id, element_id)
            if product:
                products.append(product)
    
    if not products:
        logger.warning(f"  No valid products found for lead {lead_id}")
        return None
    
    # Build tax invoice JSON
    invoice_json = build_tax_invoice_json(lead, contact, products)
    
    return invoice_json

