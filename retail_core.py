import csv
from collections import defaultdict

def parse_transaction(line):
    """
    Parses a single CSV line.
    Expected format: InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country
    Returns a dictionary of parsed values or None if parsing fails.
    """
    try:
        # Handle simple CSV parsing (assumes comma separation without complex embedded commas)
        # For a more robust parser in standard library, csv.reader is used on list of lines
        parts = line.strip().split(',')
        if len(parts) < 8:
            return None
        
        # Extract fields
        invoice_no = parts[0].strip()
        stock_code = parts[1].strip()
        description = parts[2].strip()
        quantity = int(parts[3].strip())
        invoice_date = parts[4].strip()
        unit_price = float(parts[5].strip())
        customer_id = parts[6].strip()
        country = parts[7].strip()
        
        # Filter out invalid or negative transactions (e.g. returns/cancellations)
        if quantity <= 0 or unit_price <= 0:
            return None
            
        revenue = quantity * unit_price
        
        return {
            'invoice_no': invoice_no,
            'stock_code': stock_code,
            'description': description,
            'quantity': quantity,
            'invoice_date': invoice_date,
            'unit_price': unit_price,
            'customer_id': customer_id,
            'country': country,
            'revenue': revenue
        }
    except Exception:
        return None

def aggregate_transactions(lines):
    """
    Aggregates a list of raw transaction lines.
    Returns a dictionary containing aggregated metrics.
    """
    total_revenue = 0.0
    total_quantity = 0
    revenue_by_country = defaultdict(float)
    revenue_by_product = defaultdict(lambda: {'description': '', 'revenue': 0.0})
    processed_count = 0
    
    for line in lines:
        tx = parse_transaction(line)
        if tx:
            total_revenue += tx['revenue']
            total_quantity += tx['quantity']
            revenue_by_country[tx['country']] += tx['revenue']
            
            p_id = tx['stock_code']
            revenue_by_product[p_id]['revenue'] += tx['revenue']
            if not revenue_by_product[p_id]['description'] and tx['description']:
                revenue_by_product[p_id]['description'] = tx['description']
            processed_count += 1
            
    return {
        'total_revenue': round(total_revenue, 2),
        'total_quantity': total_quantity,
        'revenue_by_country': dict(revenue_by_country),
        'revenue_by_product': dict(revenue_by_product),
        'processed_count': processed_count
    }

def merge_results(results_list):
    """
    Merges multiple aggregated results dictionaries into one.
    """
    merged_revenue = 0.0
    merged_quantity = 0
    merged_country = defaultdict(float)
    merged_product = defaultdict(lambda: {'description': '', 'revenue': 0.0})
    merged_count = 0
    
    for res in results_list:
        merged_revenue += res['total_revenue']
        merged_quantity += res['total_quantity']
        merged_count += res['processed_count']
        
        for country, rev in res['revenue_by_country'].items():
            merged_country[country] += rev
            
        for stock_code, prod_info in res['revenue_by_product'].items():
            merged_product[stock_code]['revenue'] += prod_info['revenue']
            if prod_info['description']:
                merged_product[stock_code]['description'] = prod_info['description']
                
    # Sort and take top 10 products
    top_products = sorted(
        merged_product.items(),
        key=lambda x: x[1]['revenue'],
        reverse=True
    )[:10]
    
    # Convert top products back to dict
    top_products_dict = {
        code: {
            'description': info['description'],
            'revenue': round(info['revenue'], 2)
        } for code, info in top_products
    }
    
    # Format country revenue
    formatted_country = {k: round(v, 2) for k, v in merged_country.items()}
    
    return {
        'total_revenue': round(merged_revenue, 2),
        'total_quantity': merged_quantity,
        'revenue_by_country': formatted_country,
        'top_10_products': top_products_dict,
        'processed_count': merged_count
    }
