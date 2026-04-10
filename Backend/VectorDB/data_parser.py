import json
import os

def parse_glow_data(file_path: str):
    """
    Parses the Glow_Rag.json file and returns a list of dictionaries with 'id', 'text', and 'metadata'.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Assumes structure: {"product_rag_file": { ... } }
    product_data = data.get("product_rag_file", {})
    if not product_data:
        raise ValueError("Invalid format: missing 'product_rag_file' key.")

    chunks = []
    
    # 1. Basic Identity
    basic = product_data.get("basic_identity", {})
    product_name = basic.get("product_name", "Unknown Product")
    chunks.append({
        "id": f"{product_name}_basic_identity",
        "text": f"Basic Identity for {product_name}: {json.dumps(basic, indent=2)}",
        "metadata": {"section": "basic_identity", "product": product_name}
    })

    # 2. Description
    desc = product_data.get("description", {})
    chunks.append({
        "id": f"{product_name}_description",
        "text": f"Description for {product_name}: {json.dumps(desc, indent=2)}",
        "metadata": {"section": "description", "product": product_name}
    })

    # 3. Ingredients
    ingredients = product_data.get("ingredients", {})
    chunks.append({
        "id": f"{product_name}_ingredients",
        "text": f"Ingredients for {product_name}: {json.dumps(ingredients, indent=2)}",
        "metadata": {"section": "ingredients", "product": product_name}
    })

    # 4. Manufacturing
    manufacturing = product_data.get("manufacturing_regulatory", {})
    chunks.append({
        "id": f"{product_name}_manufacturing",
        "text": f"Manufacturing & Regulatory info for {product_name}: {json.dumps(manufacturing, indent=2)}",
        "metadata": {"section": "manufacturing_regulatory", "product": product_name}
    })

    # 5. Usage & Storage
    usage = product_data.get("usage_storage_safety", {})
    chunks.append({
        "id": f"{product_name}_usage",
        "text": f"Usage, Storage & Safety for {product_name}: {json.dumps(usage, indent=2)}",
        "metadata": {"section": "usage_storage_safety", "product": product_name}
    })

    # 6. Claims & Benefits
    claims = product_data.get("claims_benefits", {})
    chunks.append({
        "id": f"{product_name}_claims",
        "text": f"Claims and Benefits for {product_name}: {json.dumps(claims, indent=2)}",
        "metadata": {"section": "claims_benefits", "product": product_name}
    })

    # 7. Sustainability & Ethics
    sustainability = product_data.get("sustainability_ethics", {})
    chunks.append({
        "id": f"{product_name}_sustainability",
        "text": f"Sustainability & Ethics for {product_name}: {json.dumps(sustainability, indent=2)}",
        "metadata": {"section": "sustainability_ethics", "product": product_name}
    })

    # 8. Pricing & Availability
    pricing = product_data.get("pricing_availability", {})
    chunks.append({
        "id": f"{product_name}_pricing",
        "text": f"Pricing and Availability for {product_name}: {json.dumps(pricing, indent=2)}",
        "metadata": {"section": "pricing_availability", "product": product_name}
    })

    return chunks

if __name__ == "__main__":
    # Test the parser
    sample_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'RAG', 'Glow_Rag.json'))
    try:
        results = parse_glow_data(sample_file)
        print(f"Parsed {len(results)} chunks.")
        for r in results[:2]:
            print(f"- {r['id']}: {len(r['text'])} chars")
    except Exception as e:
        print("Error parsing:", e)
