import xml.etree.ElementTree as ET

def evaluate_xpath(xml_element, xpath, namespaces=None):
    if namespaces is None:
        namespaces = {}

    result = xml_element.find(xpath, namespaces)
    if result is not None:
        return result.text
    else:
        return None

# Example XML string
xml_data = """
<inv:Invoice xmlns="http://uri.etsi.org/01903/v1.4.1#" xmlns:inv="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:CustomizationID>FPR12</cbc:CustomizationID>
    <cbc:ProfileID>FPR12</cbc:ProfileID>
    <cac:PartyIdentification>
        <cbc:ID schemeID="IdFiscaleIVA">IT03386690170</cbc:ID>
    </cac:PartyIdentification>
</inv:Invoice>
"""

# Parse XML string
root = ET.fromstring(xml_data)

# Define namespaces
namespaces = {
    'inv': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
}

# Example XPath expression
xpath_expression = "./cbc:CustomizationID"

tree = ET.ElementTree(root)

r2 = tree.findall(xpath_expression, namespaces)

# Evaluate XPath expression
#result = evaluate_xpath(root, xpath_expression, namespaces)

#print(result)
print(r2.text())
