import csv
import random
from datetime import datetime, timedelta

def generate_mock_retail_csv(filename="OnlineRetail.csv", num_rows=15000):
    """
    Generates a realistic OnlineRetail.csv dataset for benchmarking.
    Columns: InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country
    """
    countries = ["United Kingdom", "France", "Germany", "EIRE", "Spain", "Netherlands", "Belgium", "Switzerland", "Portugal", "Australia"]
    country_weights = [0.85, 0.03, 0.03, 0.02, 0.015, 0.015, 0.01, 0.01, 0.01, 0.01]
    
    products = [
        ("85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 2.55),
        ("22423", "REGENCY CAKESTAND 3 TIER", 12.75),
        ("84879", "ASSORTED COLOUR BIRD ORNAMENT", 1.69),
        ("47566", "PARTY BUNTING", 4.95),
        ("84997D", "CHILDRENS CUTLERY POLKADOT PINK", 4.15),
        ("22720", "SET OF 3 CAKE TINS PANTRY DESIGN", 4.95),
        ("23084", "RABBIT NIGHT LIGHT", 1.79),
        ("22197", "POPCORN HOLDER", 0.85),
        ("22086", "PAPER CHAIN KIT 50'S CHRISTMAS", 2.95),
        ("22960", "JAM MAKING SET WITH JARS", 3.75),
        ("22386", "JUMBO BAG PINK POLKADOT", 1.95),
        ("85099B", "JUMBO BAG RED RETROSPOT", 1.95),
        ("20725", "LUNCH BAG RED RETROSPOT", 1.65),
        ("20727", "LUNCH BAG WOODLAND", 1.65),
        ("POST", "POSTAGE", 18.00),
    ]
    
    start_date = datetime(2025, 1, 1, 8, 0, 0)
    
    print(f"Generating mock dataset with {num_rows} rows...")
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"])
        
        invoice_num = 536365
        current_invoice_rows = 0
        max_rows_per_invoice = 5
        
        current_customer = random.randint(12346, 18287)
        current_country = random.choices(countries, weights=country_weights)[0]
        current_date = start_date
        
        for i in range(num_rows):
            # Roll for new invoice
            if current_invoice_rows >= max_rows_per_invoice or random.random() < 0.2:
                invoice_num += 1
                current_invoice_rows = 0
                max_rows_per_invoice = random.randint(1, 10)
                current_customer = random.randint(12346, 18287)
                current_country = random.choices(countries, weights=country_weights)[0]
                current_date += timedelta(minutes=random.randint(5, 120))
            
            # Select product
            stock_code, description, base_price = random.choice(products)
            
            # Unit price variation (±10%)
            unit_price = round(base_price * random.uniform(0.9, 1.1), 2)
            
            # Quantity
            quantity = random.randint(1, 100)
            if random.random() < 0.02:  # 2% chance of bulk order
                quantity = random.randint(100, 1000)
                
            # Randomly introduce some noise rows (e.g. empty fields or invalid values) to test robustness
            if random.random() < 0.005:  # 0.5% chance of invalid row
                writer.writerow([f"C{invoice_num}", stock_code, description, -quantity, current_date.strftime("%m/%d/%Y %H:%M"), unit_price, current_customer, current_country])
            else:
                writer.writerow([invoice_num, stock_code, description, quantity, current_date.strftime("%m/%d/%Y %H:%M"), unit_price, current_customer, current_country])
                
            current_invoice_rows += 1
            
    print(f"Dataset saved successfully to: {filename}")

if __name__ == "__main__":
    generate_mock_retail_csv()
