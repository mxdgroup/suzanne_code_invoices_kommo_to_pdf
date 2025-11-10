#!/usr/bin/env python3
"""
Tax Invoice HTML Generator
Generates tax invoice HTML (based on proforma structure but labeled as TAX INVOICE)
"""
import json
from generate_proforma_invoice import calculate_proforma_totals, format_number


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
    
    # Get amount paid from terms (dynamic value from JSON)
    amount_paid_value = data['terms']['amount_paid']
    
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
  .note{{
    margin-top:20px;
    padding:14px;
    background:#fef9e8;
    border:1px solid #f0d881;
    font-size:14px;
    line-height:1.5
  }}
  .note b{{color:#c9781f}}
  .totals{{
    width:550px;
    border-collapse:collapse;
    margin:20px 0 20px auto;
    font-size:15px
  }}
  .totals td{{
    border:1px solid var(--border);
    padding:11px 14px
  }}
  .totals td.label{{background:#f6f6f6;font-weight:700}}
  .totals td.right{{text-align:right;font-weight:700}}
  .terms{{
    margin:20px 0;
    padding:14px;
    background:#e9eef2;
    border:1px solid var(--border);
    font-weight:400;
    font-size:15px
  }}
  .released{{
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    margin-top:30px
  }}
  .released .label{{
    background:#f6f6f6;
    border:1px solid var(--border);
    padding:10px 14px;
    font-weight:700;
    margin-bottom:10px
  }}
  .sign{{
    display:block;
    max-width:280px;
    height:auto;
    margin-top:10px
  }}
  .stamp{{
    display:block;
    max-width:200px;
    height:auto
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
            <div class="number">No: {data['invoice']['number']}</div>
            <div>Date: {data['invoice']['date_of_issuing']}</div>
          </div>
        </div>
        <img class="logo" src="{logo_path}" alt="Logo">
      </div>

      <div class="section-title">ISSUED BY</div>
      <table class="grid">
        <tr>
          <td class="muted w-20">Name</td>
          <td class="w-30">{issued_by['company_name']}</td>
          <td class="muted w-20">Address</td>
          <td class="w-30">{issued_by['address']}</td>
        </tr>
        <tr>
          <td class="muted">TRN</td>
          <td>{issued_by['trn']}</td>
          <td class="muted">Tel</td>
          <td>{issued_by['tel']}</td>
        </tr>
        <tr>
          <td class="muted">Email</td>
          <td colspan="3">{issued_by['email']}</td>
        </tr>
      </table>

      <div class="section-title" style="margin-top:20px">ISSUED TO</div>
      <table class="grid">
        <tr>
          <td class="muted w-20">Name</td>
          <td class="w-30">{data['issued_to']['name']}</td>
          <td class="muted w-20">Address</td>
          <td class="w-30">{data['issued_to']['address']}</td>
        </tr>
        <tr>
          <td class="muted">TRN</td>
          <td>{data['issued_to']['trn']}</td>
          <td class="muted">Email</td>
          <td>{data['issued_to']['email']}</td>
        </tr>
      </table>

      <div class="section-title" style="margin-top:20px">BANK DETAILS</div>
      <table class="grid">
        <tr>
          <td class="muted w-20">Bank Name</td>
          <td class="w-30">{bank_details['bank_name']}</td>
          <td class="muted w-20">Beneficiary</td>
          <td class="w-30">{bank_details['beneficiary']}</td>
        </tr>
        <tr>
          <td class="muted">IBAN</td>
          <td>{bank_details['iban']}</td>
          <td class="muted">SWIFT Code</td>
          <td>{bank_details['swift']}</td>
        </tr>
      </table>

      <table class="items">
        <thead>
          <tr>
            <th class="center" style="width:50px">No</th>
            <th style="min-width:280px">Description of Goods</th>
            <th class="center" style="width:80px">Qty</th>
            <th class="center" style="width:80px">Unit</th>
            <th class="right" style="width:120px">Unit Price<br/>(Incl. VAT),<br/>(AED)</th>
            <th class="center" style="width:90px">Discount<br/>(%)</th>
            <th class="center" style="width:80px">VAT<br/>(%)</th>
            <th class="right" style="width:120px">VAT<br/>Amount,<br/>(AED)</th>
            <th class="right" style="width:130px">Total<br/>(Incl. VAT),<br/>(AED)</th>
          </tr>
        </thead>
        <tbody>
{totals['rows']}
          <tr>
            <td class="label center" colspan="9" style="text-align:left">Amount in Words:&nbsp;&nbsp;<span style="font-weight:700">{data['amount_in_words']}</span></td>
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

      <div class="terms">Terms and Conditions: {data['terms']['payment_terms']} <b>{amount_paid_value} AED</b></div>

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

