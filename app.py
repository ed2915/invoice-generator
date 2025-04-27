from flask import Flask, render_template, request, send_file
from io import BytesIO
from weasyprint import HTML

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='usage.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
)


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    data = {
        'business_name': request.form.get('business_name'),
        'business_email': request.form.get('business_email'),
        'business_phone': request.form.get('business_phone'),
        'currency': request.form.get('currency', 'R'),
        'invoice_number': request.form.get('invoice_number'),
        'issue_date': request.form.get('issue_date'),
        'due_date': request.form.get('due_date'),
        'client_name': request.form.get('client_name'),
        'client_email': request.form.get('client_email'),
        'client_address': request.form.get('client_address'),
        'vat_percentage': float(request.form.get('vat_percentage')),
        'bank_name': request.form.get('bank_name'),
        'account_number': request.form.get('account_number'),
        'line_items': [],
        'materials': []
    }

    # Collect line items
    subtotal = 0
    descriptions = request.form.getlist('description')
    rates = request.form.getlist('rate')
    quantities = request.form.getlist('quantity')

    for desc, rate, qty in zip(descriptions, rates, quantities):
        if desc and rate and qty:
            rate = float(rate)
            qty = float(qty)
            total = rate * qty
            subtotal += total
            data['line_items'].append({
                'description': desc,
                'rate': rate,
                'quantity': qty,
                'total': total
            })

    # Collect materials
    materials_total = 0
    material_descriptions = request.form.getlist('material_description')
    material_costs = request.form.getlist('material_cost')

    for desc, cost in zip(material_descriptions, material_costs):
        if desc and cost:
            cost = float(cost)
            materials_total += cost
            data['materials'].append({
                'description': desc,
                'cost': cost
            })

    vat_on_line_items = (subtotal * data['vat_percentage']) / 100
    vat_on_materials = (materials_total * data['vat_percentage']) / 100

    vat = vat_on_line_items + vat_on_materials
    total = subtotal + vat + materials_total

    data['subtotal'] = subtotal
    data['vat_on_line_items'] = vat_on_line_items
    data['vat_on_materials'] = vat_on_materials
    data['vat'] = vat
    data['total'] = total
    data['materials_total'] = materials_total

    # Render HTML and convert to PDF
    html_content = render_template('invoice_template.html', data=data)
    pdf_file = HTML(string=html_content).write_pdf()

    return send_file(BytesIO(pdf_file), as_attachment=True, download_name="invoice.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)
