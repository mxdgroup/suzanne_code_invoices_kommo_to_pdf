#!/usr/bin/env python3
"""
Tax Invoice HTML Generator
Generates tax invoice HTML (based on proforma structure but labeled as TAX INVOICE)
"""
import json
from generate_proforma_invoice import calculate_proforma_totals, format_number, amount_to_words


def generate_tax_invoice_html(json_file, output_html):
    """Generate tax invoice HTML from JSON data"""
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Hardcoded company information
    issued_by = {
        'company_name': 'SUZANNE CODE JEWELLERY TRADING L.L.C.',
        'address': 'Shop BF-05 ,Burj Khalifa, Emaar  The Dubai Mall Fountain Views, PO Box:9440, Dubai, UAE',
        'trn': '104644174200003',
        'tel': '+971505752796',
        'email': 'uae@suzannecode.com'
    }
    
    bank_details = {
        'bank_name': 'Abu Dhabi Islamic Bank',
        'iban': 'AE08500000000019283818',
        'swift': 'ABDIAEADXXX',
        'beneficiary': 'SUZANNE CODE JEWELLERY TRADING L.L.C.'
    }
    
    # Calculate totals
    totals = calculate_proforma_totals(data['items'])
    
    # Generate amount in words from calculated total
    amount_in_words_text = amount_to_words(totals['total_incl_vat_numeric'])
    
    # Image paths - use absolute paths relative to the script location
    import pathlib
    script_dir = pathlib.Path(__file__).parent
    logo_path = script_dir / 'logo.png'
    signature_path = script_dir / 'signutare.png'
    stamp_path = script_dir / 'stamp.png'
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>TAX INVOICE - {data['invoice']['number']}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  @page {{
    size: 400mm 360mm;
    margin: 12mm;
  }}
  
  :root{{
    --gray:#7f7f7f;
    --border:#b7b7b7;
    --dark:#333;
    --light:#f3f3f3;
  }}
  *{{box-sizing:border-box}}
  html,body{{margin:0;padding:0;font-family:Arial,Helvetica,sans-serif;color:#000;}}
  body{{padding:20px 24px;background:#fff;}}
  .page{{max-width:1500px;width:100%;margin:0 auto;border:1px solid #ddd;box-shadow:0 0 0.5rem rgba(0,0,0,.04)}}
  .wrap{{padding:40px 45px 50px 45px}}
  .top-bar{{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:30px}}
  .title{{font-size:34px;font-weight:800;letter-spacing:.7px}}
  .meta{{margin-top:12px}}
  .meta div{{font-size:15px;font-weight:700}}
  .meta .number{{margin-bottom:5px}}
  .logo{{height:95px;object-fit:contain;opacity:.9}}
  .grid{{width:100%;border-collapse:collapse;font-size:15px;margin-top:14px}}
  .grid th,.grid td{{border:1px solid var(--border);padding:13px 14px;vertical-align:top}}
  .muted{{color:#333;font-weight:700;background:#e9eef2}}
  .label{{font-weight:700;background:#f6f6f6}}
  .section-title{{font-weight:700;background:#e9eef2;border:1px solid var(--border);border-bottom:none;padding:13px}}
  .small{{font-size:14px}}
  .nowrap{{white-space:nowrap}}
  .center{{text-align:center}}
  .right{{text-align:right}}
  .w-20{{width:20%}}
  .w-30{{width:30%}}
  .w-40{{width:40%}}
  .w-50{{width:50%}}
  .w-60{{width:60%}}
  .w-100{{width:100%}}
  .items{{font-size:15px;margin-top:16px;border-collapse:collapse;width:100%}}
  .items th,.items td{{border:1px solid var(--border);padding:11px 12px;vertical-align:top}}
  .items th{{background:#e9eef2;font-weight:700}}
  .items td.center, .items th.center{{text-align:center}}
  .items td.right, .items th.right{{text-align:right}}
  .note{{font-size:15px;margin-top:16px;border:1px solid var(--border);padding:11px 14px;background:#f6f6f6}}
  .totals{{width:42%;margin-left:auto;margin-top:12px;border-collapse:collapse;font-size:15px}}
  .totals td{{border:1px solid var(--border);padding:11px}}
  .totals td.label{{font-weight:700;background:#f6f6f6;width:60%}}
  .terms{{font-size:15px;margin-top:24px;font-weight:500}}
  .released{{margin-top:75px;display:flex;gap:55px;align-items:flex-start;justify-content:space-between}}
  .stamp{{height:210px;opacity:.95;object-fit:contain}}
  .sign{{height:95px;margin-top:38px;object-fit:contain}}
  .released .label{{background:transparent;border:none;padding:0;font-weight:700;font-size:15px}}
  .footnote{{font-size:14px;margin-top:7px;color:#333}}
  
  @media print {{
    body {{padding:0;background:#fff;}}
    .page {{border:none;box-shadow:none;max-width:100%;}}
  }}
</style>
</head>
<body>
  <div class="page">
    <div class="wrap">
      <div class="top-bar">
        <div>
          <div class="title">TAX INVOICE</div>
          <div class="meta">
            <div class="number"># {data['invoice']['number']}</div>
            <div class="date">{data['invoice']['date_of_issuing']}</div>
          </div>
        </div>
        <img class="logo" src="{logo_path}" alt="Suzanne Code Jewelry logo">
      </div>

      <!-- Issued/Bill grid -->
      <table class="grid">
        <tr>
          <th class="muted center" colspan="2">Issued By:</th>
          <th class="muted center" colspan="2">Bill To:</th>
        </tr>
        <tr>
          <td class="label w-20">{issued_by['company_name']}</td>
          <td class="w-30 small">
            <div><b>TRN:</b> {issued_by['trn']}</div>
            <div><b>Address:</b> {issued_by['address']}</div>
            <div><b>Tel.:</b> {issued_by['tel']}</div>
            <div><b>E-mail:</b> {issued_by['email']}</div>
          </td>
          <td class="label w-20">{data['issued_to']['name']}</td>
          <td class="w-30 small">
            <div><b>TRN:</b> {data['issued_to'].get('trn', '')}</div>
            <div><b>Address:</b> {data['issued_to']['address']}</div>
            <div><b>E-mail:</b> {data['issued_to']['email']}</div>
          </td>
        </tr>
        <tr>
          <th class="muted center" colspan="2">Bank Details:</th>
          <th class="muted center" colspan="2">Terms and Conditions</th>
        </tr>
        <tr>
          <td class="label">{bank_details['bank_name']}</td>
          <td class="small">
            <div><b>IBAN:</b> {bank_details['iban']}</div>
            <div><b>SWIFT:</b> {bank_details['swift']}</div>
            <div><b>Beneficiary:</b> {bank_details['beneficiary']}</div>
          </td>
          <td class="label">Payment Terms:</td>
          <td class="small">Payment on Delivery</td>
        </tr>
      </table>

      <!-- Items table -->
      <table class="items">
        <thead>
          <tr>
            <th class="center" style="width:55px">#</th>
            <th>Description</th>
            <th class="center" style="width:110px">Quantity</th>
            <th class="center" style="width:95px">UOM</th>
            <th class="right" style="width:150px">Price (Incl. VAT), (AED)</th>
            <th class="center" style="width:105px">Discount, %</th>
            <th class="center" style="width:95px">VAT, %</th>
            <th class="right" style="width:150px">VAT Amount, (AED)</th>
            <th class="right" style="width:150px">Amount, (AED)</th>
          </tr>
        </thead>
        <tbody>
{totals['rows']}
          <tr>
            <td class="label center" colspan="9" style="text-align:left">Amount in Words:&nbsp;&nbsp;<span style="font-weight:700">{amount_in_words_text}</span></td>
          </tr>
        </tbody>
      </table>

      <table class="totals">
        <tr>
          <td class="label">Total Discount, (AED):</td>
          <td class="right">{totals['total_discount']}</td>
        </tr>
        <tr>
          <td class="label">Total (Excl. VAT), (AED):</td>
          <td class="right">{totals['total_excl_vat']}</td>
        </tr>
        <tr>
          <td class="label">Total VAT, (AED):</td>
          <td class="right">{totals['total_vat']}</td>
        </tr>
        <tr>
          <td class="label">Total (Incl. VAT), (AED):</td>
          <td class="right"><b>{totals['total_incl_vat']}</b></td>
        </tr>
      </table>

      <div class="terms">Terms and Conditions: Payment on Delivery</div>

      <div class="released">
        <div style="min-width:280px">
          <div class="label">Released By</div>
          <img class="sign" src="{signature_path}" alt="Signature">
        </div>
        <div>
          <img class="stamp" src="{stamp_path}" alt="Company Stamp">
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Generated tax invoice HTML: {output_html}")
    return output_html


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) == 3:
        generate_tax_invoice_html(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python generate_tax_invoice.py <input.json> <output.html>")

