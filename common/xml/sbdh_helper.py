import xml.etree.ElementTree as ET
from datetime import datetime

# invoice_element is the root element of the invoice XML - SCI (UBL)
# ex: <inv:Invoice xmlns:inv="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" ....>....</inv:Invoice>
def create_sovos_document_for_sci_Invoice(invoice_element):
    #<svs:SovosDocument>
    sovos_document = ET.Element("svs:SovosDocument")
    #<sci:SovosCanonicalInvoice>
    canonical_invoice = ET.SubElement(sovos_document, "sci:SovosCanonicalInvoice")
    # Add the provided Invoice element
    canonical_invoice.append(invoice_element)

    return sovos_document

#<sbd:Standard>urn:oasis:names:specification:ubl:schema:xsd:Invoice-2</sbd:Standard>
def create_standard_document_identification(standard):
    element = ET.Element("sbd:Standard")
    element.text = standard

    return element

#<sbd:TypeVersion>2.1</sbd:TypeVersion>
def create_type_version_document_identification(type_version):
    element = ET.Element("sbd:TypeVersion")
    element.text = type_version

    return element

#<sbd:InstanceIdentifier>string</sbd:InstanceIdentifier>
def create_instance_identifier(instance_identifier):
    element = ET.Element("sbd:InstanceIdentifier")
    element.text = instance_identifier

    return element

#<sbd:Type>Invoice</sbd:Type>
def create_type_document_identification(document_type):
    element = ET.Element("sbd:Type")
    element.text = document_type

    return element

#<sbd:MultipleType>false</sbd:MultipleType>
def create_multiple_type_document_identification(multiple):
    element = ET.Element("sbd:MultipleType")
    element.text = multiple

    return element

#<sbd:CreationDateAndTime>2023-06-29T00:00:00Z</sbd:CreationDateAndTime>
def create_creation_date_and_time_document_identification(creation_date_time):
    element = ET.Element("sbd:CreationDateAndTime")
    element.text = creation_date_time

    return element


#<sbd:HeaderVersion>1.0</sbd:HeaderVersion>
def create_header_version_element(version):
    header_version_element = ET.Element("sbd:HeaderVersion")
    header_version_element.text = version

    return header_version_element

#<sbd:Receiver>
#  <sbd:Identifier Authority="IT">03386690170</sbd:Identifier>
#</sbd:Receiver>
def create_receiver_element(countryCode, vat_number):
    receiver_element = ET.Element("sbd:Receiver")
    # Create the Identifier element
    identifier_element = ET.SubElement(receiver_element, "sbd:Identifier", Authority=countryCode)
    identifier_element.text = vat_number

    return receiver_element

#<sbd:Sender>
#  <sbd:Identifier Authority="IT">03386690170</sbd:Identifier>
#</sbd:Sender>
def create_sender_element(countryCode, vat_number):
    sender_element = ET.Element("sbd:Sender")
    # Create the Identifier element
    identifier_element = ET.SubElement(sender_element, "sbd:Identifier", Authority=countryCode)
    identifier_element.text = vat_number

    return sender_element

#<sbd:Scope>
#  <sbd:Type>BusinessProcess</sbd:Type>
#  <sbd:InstanceIdentifier/>
#  <sbd:BusinessService>
#    <sbd:BusinessServiceName>Default</sbd:BusinessServiceName>
#  </sbd:BusinessService>
#</sbd:Scope>
def create_scope_business_process_element (business_service_name):
    scope_element = ET.Element("sbd:Scope")
    
    type_element = ET.SubElement(scope_element, "sbd:Type")
    type_element.text = "BusinessProcess"
    
    instance_element = ET.SubElement(scope_element, "sbd:InstanceIdentifier")
    
    business_service = ET.SubElement(scope_element, "sbd:BusinessService")
    business_service_name_element = ET.SubElement(business_service, "sbd:BusinessServiceName")
    business_service_name_element.text = business_service_name

    return scope_element

#<sbd:Scope>
#  <sbd:Type>Country</sbd:Type>
#  <sbd:InstanceIdentifier/>
#  <sbd:Identifier>IT</sbd:Identifier>
#</sbd:Scope>
def create_scope_element(type, identifier):
    scope_element = ET.Element("sbd:Scope")
    
    type_element = ET.SubElement(scope_element, "sbd:Type")
    type_element.text = type
    
    instance_element = ET.SubElement(scope_element, "sbd:InstanceIdentifier")
    # You can customize the instance identifier here if needed
    
    identifier_element = ET.SubElement(scope_element, "sbd:Identifier")
    identifier_element.text = identifier

    return scope_element

#<sbd:StandardBusinessDocument xmlns:sbd="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader">....</sbd:StandardBusinessDocument>
def create_standard_business_document(header_version = "1.0",
                                      sender_vat = None,
                                      receiver_vat = None,
                                      sender_vat_country = "XX",
                                      receiver_vat_country = "XX",
                                      sender_company_code = "SenderCompanyCode",
                                      document_identification_standard = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
                                      multiple_type_document_identification = "false",
                                      scope_mapping = 'SCI-TO-LEGAL_INVOICE',
                                      is_payload_SCI_UBL = True,
                                      scope_version_identifier = "1.2.2",
                                      document_identification_type_version = "2.1",
                                      document_identification_instance_identifier = "------",
                                      output_schema_identifier = "-----",
                                      process_type_identifier = 'Outbound',
                                      sender_document_id_identifier = None, 
                                      document_type = "Invoice",
                                      sender_system_id = "SystemERP",
                                      business_service_name = "Default",
                                      invoice_element = None):
    # Create the root element with namespaces
    root = ET.Element("sbd:StandardBusinessDocument", 
                    attrib={"xmlns": "http://uri.etsi.org/01903/v1.4.1#",
                            "xmlns:sbd": "http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader",
                            "xmlns:xades": "http://uri.etsi.org/01903/v1.3.2#",
                            "xmlns:ad": "http://www.sovos.com/namespaces/additionalData",
                            "xmlns:sci": "http://www.sovos.com/namespaces/sovosCanonicalInvoice",
                            "xmlns:svs": "http://www.sovos.com/namespaces/sovosDocument",
                            "xmlns:sov": "http://www.sovos.com/namespaces/sovosExtensions",
                            "xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
                            "xmlns:cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
                            "xmlns:cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                            "xmlns:ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
                            "xmlns:inv": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"}
                    )

    # Create StandardBusinessDocumentHeader element
    sbd_header = ET.SubElement(root, "sbd:StandardBusinessDocumentHeader")
    header_version = create_header_version_element(header_version)
    sbd_header.append(header_version)

    # Create and append elements for Sender and Receiver
    #<sbd:Sender>
    #  <sbd:Identifier Authority="IT">03386690170</sbd:Identifier>
    #</sbd:Sender>
    sender_element = create_sender_element(sender_vat_country, sender_vat)
    receiver_element = create_receiver_element(receiver_vat_country, receiver_vat)
    sbd_header.append(sender_element)
    sbd_header.append(receiver_element)

    # Create DocumentIdentification element
    #<sbd:DocumentIdentification>
    document_identification = ET.SubElement(sbd_header, "sbd:DocumentIdentification")
    
    #<sbd:Standard>https://www.fatturapa.gov.it/it/norme-e-regole/documentazione-fattura-elettronica/formato-fatturapa/</sbd:Standard>      
    document_identification.append(create_standard_document_identification(document_identification_standard))
    #<sbd:TypeVersion>2.1</sbd:TypeVersion>
    document_identification.append(create_type_version_document_identification(document_identification_type_version))
    #<sbd:InstanceIdentifier>string</sbd:InstanceIdentifier>
    document_identification.append(create_instance_identifier(document_identification_instance_identifier))
    #<sbd:Type>Invoice</sbd:Type>
    document_identification.append(create_type_document_identification(document_type))
    #<sbd:MultipleType>false</sbd:MultipleType>
    document_identification.append(create_multiple_type_document_identification(multiple_type_document_identification))
    #<sbd:CreationDateAndTime>2023-06-29T00:00:00Z</sbd:CreationDateAndTime>
    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    document_identification.append(create_creation_date_and_time_document_identification(current_datetime))

    # Create BusinessScope element with multiple Scope elements
    #<sbd:BusinessScope>
    business_scope = ET.SubElement(sbd_header, "sbd:BusinessScope")

    # is_payload_SCI_UBL
    #<sbd:Scope>
    #  <sbd:Type>Mapping.TransformDocument</sbd:Type>
    #  <sbd:InstanceIdentifier/>
    #  <sbd:Identifier>SCI-TO-LEGAL_INVOICE</sbd:Identifier>
    #</sbd:Scope>
    scope_mapping_element = create_scope_element("Mapping.TransformDocument", scope_mapping)
    business_scope.append(scope_mapping_element)
    #<sbd:Scope>
    #  <sbd:Type>Mapping.OutputSchema</sbd:Type>
    #  <sbd:InstanceIdentifier/>
    #  <sbd:Identifier>FatturaPA</sbd:Identifier>
    #</sbd:Scope>
    scope_mapping_output_schema = create_scope_element("Mapping.OutputSchema", output_schema_identifier)
    business_scope.append(scope_mapping_output_schema)
    #<sbd:Scope>
    #  <sbd:Type>Country</sbd:Type>
    #  <sbd:InstanceIdentifier/>
    #  <sbd:Identifier>IT</sbd:Identifier>
    #</sbd:Scope>
    business_scope.append(create_scope_element("Country", sender_vat_country))
    #<sbd:Scope>
    #  <sbd:Type>SenderSystemId</sbd:Type>
    #  <sbd:InstanceIdentifier/>
    #  <sbd:Identifier>SystemERP</sbd:Identifier>
    #</sbd:Scope>
    business_scope.append(create_scope_element("SenderSystemId", sender_system_id))
    #<sbd:Scope>
    #  <sbd:Type>CompanyCode</sbd:Type>
    #  <sbd:InstanceIdentifier/>
    #  <sbd:Identifier>03386690170</sbd:Identifier>
    #</sbd:Scope>
    business_scope.append(create_scope_element("CompanyCode", sender_company_code))
    #<sbd:Scope>
    #  <sbd:Type>SenderDocumentId</sbd:Type>
    #  <sbd:InstanceIdentifier/>
    #  <sbd:Identifier>113482986</sbd:Identifier>
    #</sbd:Scope>
    business_scope.append(create_scope_element("SenderDocumentId", sender_document_id_identifier))
    #<sbd:Scope>
    #  <sbd:Type>ProcessType</sbd:Type>
    #  <sbd:InstanceIdentifier/>
    #  <sbd:Identifier>Outbound</sbd:Identifier>
    #</sbd:Scope>
    business_scope.append(create_scope_element("ProcessType", process_type_identifier))
    #<sbd:Scope>
    #  <sbd:Type>Version</sbd:Type>
    #  <sbd:InstanceIdentifier/>
    #  <sbd:Identifier>1.2.2</sbd:Identifier>
    #</sbd:Scope>
    business_scope.append(create_scope_element("Version", scope_version_identifier))
    #<sbd:Scope>
    #  <sbd:Type>BusinessProcess</sbd:Type>
    #  <sbd:InstanceIdentifier/>
    #  <sbd:BusinessService>
    #    <sbd:BusinessServiceName>Default</sbd:BusinessServiceName>
    #  </sbd:BusinessService>
    #</sbd:Scope>
    business_scope.append(create_scope_business_process_element(business_service_name))

    #append to the root element the SovosDocument
    if is_payload_SCI_UBL:
        sovos_document = create_sovos_document_for_sci_Invoice(invoice_element)
        root.append(sovos_document)
   
    return root


def get_element_by_xpath_in_SCI(xml_sci_element, xpath):
    # Define namespaces
    sci_namespaces = {
        'inv': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'sbd': 'http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader',
        'xades': 'http://uri.etsi.org/01903/v1.3.2#',
        'ad': 'http://www.sovos.com/namespaces/additionalData',
        'sci': 'http://www.sovos.com/namespaces/sovosCanonicalInvoice',
        'svs': 'http://www.sovos.com/namespaces/sovosDocument',
        'sov': 'http://www.sovos.com/namespaces/sovosExtensions',
        'ds': 'http://www.w3.org/2000/09/xmldsig#',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
    }
    result_element = xml_sci_element.find(xpath, sci_namespaces)

    return result_element


def evaluate_xpath(element, xpath, namespaces=None):
    if namespaces is None:
        namespaces = {}
    
    result = element.find(xpath, namespaces)
    if result is not None:
        return result.text
    else:
        return None

