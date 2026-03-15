import pandas as pd
import io
import os

def generate_rfq_excel(materials: list) -> bytes:
    """
    Generates an RFQ Excel file with columns:
    Material Description, Specification, Quantity, Unit, Remarks
    """
    data = []
    for m in materials:
        data.append({
            "Material Description": m.get("description", ""),
            "Specification": m.get("specification", ""),
            "Quantity": m.get("quantity", 0),
            "Unit": m.get("unit", ""),
            "Remarks": "" # Empty for vendor quotation
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='RFQ', index=False)
    
    return output.getvalue()
