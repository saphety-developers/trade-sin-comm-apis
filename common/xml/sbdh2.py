import base64
from datetime import datetime
import xml.etree.ElementTree as ET
from common.console import console_error, console_info, console_warning

from common.xml.ubl_namespaces import FORMAT_ID_LEGAL_RO, FORMAT_ID_LEGAL_SA, FORMAT_ID_SCI, UBL_NAMESPACES_PREFIXES, UBL_NAMESPACES_PREFIXES_ATTR
from common.xml.xpath_helper import XPATHelper

class StandardBusinessDocumentHeader:
    DOCUMENT_IDENTIFICATION_STANDARD_MAPS = {
    "IT": "https://www.fatturapa.gov.it/it/norme-e-regole/documentazione-fattura-elettronica/formato-fatturapa/",
    "SA": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "RO": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "HU": "hu",
    "PO": "po"
    }
    DOCUMENT_IDENTIFICATION_DOCUMENT_TYPE_MAPS = {
        "IT": "FatturaPA",
        "SA": "UBLInvoice",
        "RO": "Factura",
        "HU": "hu",
        "PO": "po"
    }
    DOCUMENT_IDENTIFICATION_TYPE_VERSION_WHEN_USING_SCI = {
        "IT": "2.1",
        "SA": "2.1",
        "RO": "2.1",
        "HU": "hu",
        "PO": "po"
    }
    DOCUMENT_IDENTIFICATION_TYPE_VERSION_WHEN_USING_LEGAL= {
        "IT": "1.2.2",
        "SA": "2.1",
        "RO": "2.1",
        "HU": "hu",
        "PO": "po"
    }
    SCOPE_VERSION_WHEN_USING_SCI = {
        "IT": "1.2.2",
        "SA": "1.0",
        "RO": "1.0",
        "HU": "hu",
        "PO": "po"
    }
    SCOPE_VERSION_WHEN_USING_LEGAL = {
        "IT": "1.2.2",
        "SA": "1.0",
        "RO": "1.0",
        "HU": "hu",
        "PO": "po"
    }
    
    def __init__(self,
                 xml_document,
                 format_id = "SCI",
                 sender_system_id="SystemERP",
                 company_branch=None):
        self.xml_document = xml_document
        self.format_id = format_id
        self.sender_system_id = sender_system_id
        self.company_branch = company_branch
        self.__calculate_sbdh_values()

    def __calculate_sbdh_values(self):
        self.header_version="1.0"
        self.sender_vat = None
        self.receiver_vat = None
        self.sender_vat_country = "XX"
        self.receiver_vat_country = "XX"
        self.sender_company_code = "SenderCompanyCode"
        self.document_identification_standard = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
        self.multiple_type_document_identification = "false"
        self.scope_mapping = 'SCI-TO-LEGAL_INVOICE'
        self.multiple_type_document_identification = False
        self.scope_version_identifier="1.2.2"
        self.document_identification_type_version="2.1"
        self.document_identification_instance_identifier="------"
        self.output_schema_identifier="-----"
        self.process_type_identifier="Outbound"
        self.sender_document_id_identifier=None
        self.document_type="Invoice"
        self.business_service_name="Default"

       # HEre
        format = self.format_id

        sender_vat_xpaths = XPATHelper.get_xpaths_for_property(format, 'sender_vat')
        sender_vat_country_xpaths = XPATHelper.get_xpaths_for_property(format, 'sender_vat_country')
        receiver_vat_xpaths = XPATHelper.get_xpaths_for_property(format, 'receiver_vat')
        receiver_vat_country_xpaths = XPATHelper.get_xpaths_for_property(format, 'receiver_vat_country')
        doc_number_xpaths = XPATHelper.get_xpaths_for_property(format, 'doc_number')


        # Define namespaces
        if format == FORMAT_ID_SCI or format == FORMAT_ID_LEGAL_SA or format == FORMAT_ID_LEGAL_RO:
            namespaces = UBL_NAMESPACES_PREFIXES
        else:
            namespaces = {
            }

        sender_vat_element = XPATHelper.get_element_by_xpaths (self.xml_document, sender_vat_xpaths, namespaces)
        sender_vat_country_element = XPATHelper.get_element_by_xpaths (self.xml_document, sender_vat_country_xpaths, namespaces)
        receiver_vat_element = XPATHelper.get_element_by_xpaths (self.xml_document, receiver_vat_xpaths, namespaces)
        receiver_vat_country_element = XPATHelper.get_element_by_xpaths (self.xml_document, receiver_vat_country_xpaths, namespaces)
        doc_number_element = XPATHelper.get_element_by_xpaths (self.xml_document, doc_number_xpaths, namespaces)

        # validations to check if we have the required elements for SBDH
        if sender_vat_element is None:
            console_error(f'Error: could not extract sender VAT with xpaths {sender_vat_xpaths}')
            return False
        if sender_vat_country_element is None:
            console_error('Error: could not extract sender VAT country with xpaths', sender_vat_country_xpaths)
            return False
        if receiver_vat_element is None:
            console_error('Error: could not extract receiver VAT with xpaths', receiver_vat_xpaths)
            return False
        if receiver_vat_country_element is None:
            console_warning(f'Warning: could not extract receiver VAT country with xpaths {receiver_vat_country_xpaths}')
        if doc_number_element is None:
            console_warning(f'Warning: could not extract document number with xpaths {doc_number_xpaths}')


        # if sender_vat_country len is greater then 2, then we have the country code and the vat number
        #   in this case we get the compnay code from international the vat number
        if sender_vat_country_element is not None and len(sender_vat_country_element.text) > 2:
            self.sender_company_code =  sender_vat_country_element.text[2:]
        else:
            self.sender_company_code =  sender_vat_element.text

        console_info(f"sender_company_code: {self.sender_company_code}")
        
        process_type_identifier = "Outbound"
        self.sender_vat = sender_vat_element.text if sender_vat_element is not None else ""
        self.sender_vat_country = sender_vat_country_element.text if sender_vat_country_element is not None else ""
        self.receiver_vat = receiver_vat_element.text if receiver_vat_element is not None else ""
        self.receiver_vat_country = receiver_vat_country_element.text if receiver_vat_country_element is not None else ""
        doc_number = doc_number_element.text if doc_number_element is not None else ""
        self.sender_document_id_identifier = f"{doc_number}_{self.sender_vat_country[:2]}{self.sender_vat}_{self.receiver_vat_country[:2]}{self.receiver_vat}"
        self.multiple_type_document_identification = "false"


        if format == FORMAT_ID_SCI:
            self.document_identification_type_version = self.DOCUMENT_IDENTIFICATION_TYPE_VERSION_WHEN_USING_SCI.get(self.sender_vat_country[:2])
            self.scope_version_identifier = self.SCOPE_VERSION_WHEN_USING_SCI.get(self.sender_vat_country[:2])
            self.document_identification_standard = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
            self.scope_mapping = 'SCI-TO-LEGAL_INVOICE'
            is_payload_SCI_UBL = True
        else:    
            self.document_identification_type_version = self.DOCUMENT_IDENTIFICATION_TYPE_VERSION_WHEN_USING_LEGAL.get(self.sender_vat_country[:2])
            self.scope_version_identifier = self.SCOPE_VERSION_WHEN_USING_SCI.get(self.sender_vat_country[:2])
            self.document_identification_standard = self.DOCUMENT_IDENTIFICATION_STANDARD_MAPS.get(self.sender_vat_country[:2])
            self.scope_mapping = 'LEGAL-TO-SCI_INVOICE'
            is_payload_SCI_UBL = False

        # document_type
        # Get the local name of the root element without the namespace
        if is_payload_SCI_UBL or format == FORMAT_ID_LEGAL_SA or format == FORMAT_ID_LEGAL_RO:
            root_element_name = self.xml_document.tag.split('}')[1] if '}' in self.xml_document.tag else self.xml_document.tag
            self.document_type = root_element_name
        #if config.format_id == FORMAT_ID_LEGAL_RO:
        #   document_type = COUNTRY_FORMAT_MAPS.get(sender_vat_country[:2])
        else:
            self.document_type = self.DOCUMENT_IDENTIFICATION_DOCUMENT_TYPE_MAPS.get(self.sender_vat_country[:2])
        
        self.output_schema_identifier = self.DOCUMENT_IDENTIFICATION_DOCUMENT_TYPE_MAPS.get(self.sender_vat_country[:2])

    def envelope(self):
        # perform pre calculations required for SBDH
        # Create the SBDH
        #<sbd:StandardBusinessDocument xmlns=....
        root = ET.Element("sbd:StandardBusinessDocument", attrib=UBL_NAMESPACES_PREFIXES_ATTR)
        #<sbd:HeaderVersion>1.0</sbd:HeaderVersion>
        sbd_header = ET.SubElement(root, "sbd:StandardBusinessDocumentHeader")
        header_version_element = self.create_header_version_element(self.header_version)
        sbd_header.append(header_version_element)
        # Create and append elements for Sender and Receiver
        #<sbd:Sender>
        #  <sbd:Identifier Authority="IT">03386690170</sbd:Identifier>
        #</sbd:Sender>
        sender_element = self.create_sender_element(self.sender_vat_country, self.sender_company_code)
        receiver_element = self.create_receiver_element(self.receiver_vat_country, self.receiver_vat)
        sbd_header.append(sender_element)
        sbd_header.append(receiver_element)

        #<sbd:DocumentIdentification>
        document_identification = ET.SubElement(sbd_header, "sbd:DocumentIdentification")
        
        #<sbd:Standard>https://www.fatturapa.gov.it/it/norme-e-regole/documentazione-fattura-elettronica/formato-fatturapa/</sbd:Standard>      
        document_identification.append(self.create_standard_document_identification(self.document_identification_standard))
        #<sbd:TypeVersion>2.1</sbd:TypeVersion>
        document_identification.append(self.create_type_version_document_identification(self.document_identification_type_version))
        #<sbd:InstanceIdentifier>string</sbd:InstanceIdentifier>
        document_identification.append(self.create_instance_identifier(self.document_identification_instance_identifier))
        #<sbd:Type>Invoice</sbd:Type>
        document_identification.append(self.create_type_document_identification(self.document_type))
        #<sbd:MultipleType>false</sbd:MultipleType>
        document_identification.append(self.create_multiple_type_document_identification(self.multiple_type_document_identification))
        #<sbd:CreationDateAndTime>2023-06-29T00:00:00Z</sbd:CreationDateAndTime>
        current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        document_identification.append(self.create_creation_date_and_time_document_identification(current_datetime))

        # Create BusinessScope element with multiple Scope elements
        #<sbd:BusinessScope>
        business_scope = ET.SubElement(sbd_header, "sbd:BusinessScope")

        # is_payload_SCI_UBL
        #<sbd:Scope>
        #  <sbd:Type>Mapping.TransformDocument</sbd:Type>
        #  <sbd:InstanceIdentifier/>
        #  <sbd:Identifier>SCI-TO-LEGAL_INVOICE</sbd:Identifier>
        #</sbd:Scope>
        scope_mapping_element = self.create_scope_element("Mapping.TransformDocument", self.scope_mapping)
        business_scope.append(scope_mapping_element)
        #<sbd:Scope>
        #  <sbd:Type>Mapping.OutputSchema</sbd:Type>
        #  <sbd:InstanceIdentifier/>
        #  <sbd:Identifier>FatturaPA</sbd:Identifier>
        #</sbd:Scope>
        scope_mapping_output_schema = self.create_scope_element("Mapping.OutputSchema", self.output_schema_identifier)
        business_scope.append(scope_mapping_output_schema)
        #<sbd:Scope>
        #  <sbd:Type>Country</sbd:Type>
        #  <sbd:InstanceIdentifier/>
        #  <sbd:Identifier>IT</sbd:Identifier>
        #</sbd:Scope>
        business_scope.append(self.create_scope_element("Country", self.sender_vat_country))
        #<sbd:Scope>
        #  <sbd:Type>SenderSystemId</sbd:Type>
        #  <sbd:InstanceIdentifier/>
        #  <sbd:Identifier>SystemERP</sbd:Identifier>
        #</sbd:Scope>
        business_scope.append(self.create_scope_element("SenderSystemId", self.sender_system_id))
        #<sbd:Scope>
        #  <sbd:Type>CompanyCode</sbd:Type>
        #  <sbd:InstanceIdentifier/>
        #  <sbd:Identifier>03386690170</sbd:Identifier>
        #</sbd:Scope>
        business_scope.append(self.create_scope_element("CompanyCode", self.sender_company_code))
        #<sbd:Scope>
        #  <sbd:Type>SenderDocumentId</sbd:Type>
        #  <sbd:InstanceIdentifier/>
        #  <sbd:Identifier>113482986</sbd:Identifier>
        #</sbd:Scope>
        business_scope.append(self.create_scope_element("SenderDocumentId", self.sender_document_id_identifier))
        #<sbd:Scope>
        #  <sbd:Type>ProcessType</sbd:Type>
        #  <sbd:InstanceIdentifier/>
        #  <sbd:Identifier>Outbound</sbd:Identifier>
        #</sbd:Scope>
        business_scope.append(self.create_scope_element("ProcessType", self.process_type_identifier))
        #<sbd:Scope>
        #  <sbd:Type>Version</sbd:Type>
        #  <sbd:InstanceIdentifier/>
        #  <sbd:Identifier>1.2.2</sbd:Identifier>
        #</sbd:Scope>
        business_scope.append(self.create_scope_element("Version", self.scope_version_identifier))
        #<sbd:Scope>
        #  <sbd:Type>BusinessProcess</sbd:Type>
        #  <sbd:InstanceIdentifier/>
        #  <sbd:BusinessService>
        #    <sbd:BusinessServiceName>Default</sbd:BusinessServiceName>
        #  </sbd:BusinessService>
        #</sbd:Scope>
        business_scope.append(self.create_scope_business_process_element(self.business_service_name))

        if self.company_branch is not None:
            #<sbd:Scope>
            #  <sbd:Type>Branch</sbd:Type>
            #  <sbd:InstanceIdentifier/>
            #  <sbd:Identifier>BranchCode</sbd:Identifier>
            #</sbd:Scope>
            business_scope.append(self.create_scope_element("Branch", self.company_branch))

        # Append the provided invoice_element
        if self.format_id == FORMAT_ID_SCI:
            sovos_document = self.create_sovos_document_for_sci_Invoice(self.xml_document)
        else:
            sovos_document = self.create_sovos_document_for_legal_Invoice(self.xml_document)
        root.append(sovos_document)

        return root

    @staticmethod
    #<sbd:HeaderVersion>1.0</sbd:HeaderVersion>
    def create_header_version_element(version):
        header_version_element = ET.Element("sbd:HeaderVersion")
        header_version_element.text = version

        return header_version_element

    @staticmethod
    #<sbd:Sender>
    #  <sbd:Identifier Authority="IT">03386690170</sbd:Identifier>
    #</sbd:Sender>
    def create_sender_element(countryCode, vat_number):
        sender_element = ET.Element("sbd:Sender")
        # Create the Identifier element
        identifier_element = ET.SubElement(sender_element, "sbd:Identifier", Authority=countryCode)
        identifier_element.text = vat_number

        return sender_element
    @staticmethod
    #<sbd:Receiver>
    #  <sbd:Identifier Authority="IT">03386690170</sbd:Identifier>
    #</sbd:Receiver>
    def create_receiver_element(countryCode, vat_number):
        receiver_element = ET.Element("sbd:Receiver")
        # Create the Identifier element
        identifier_element = ET.SubElement(receiver_element, "sbd:Identifier", Authority=countryCode)
        identifier_element.text = vat_number

        return receiver_element
    
    @staticmethod
    #<sbd:Standard>urn:oasis:names:specification:ubl:schema:xsd:Invoice-2</sbd:Standard>
    def create_standard_document_identification(standard):
        element = ET.Element("sbd:Standard")
        element.text = standard

        return element
    
    @staticmethod
    #<sbd:TypeVersion>2.1</sbd:TypeVersion>
    def create_type_version_document_identification(type_version):
        element = ET.Element("sbd:TypeVersion")
        element.text = type_version

        return element
    
    @staticmethod
    #<sbd:InstanceIdentifier>string</sbd:InstanceIdentifier>
    def create_instance_identifier(instance_identifier):
        element = ET.Element("sbd:InstanceIdentifier")
        element.text = instance_identifier

        return element
    
    @staticmethod
    #<sbd:Type>Invoice</sbd:Type>
    def create_type_document_identification(document_type):
        element = ET.Element("sbd:Type")
        element.text = document_type

        return element

    @staticmethod
    #<sbd:MultipleType>false</sbd:MultipleType>
    def create_multiple_type_document_identification(multiple):
        element = ET.Element("sbd:MultipleType")
        element.text = multiple

        return element

    @staticmethod
    #<sbd:CreationDateAndTime>2023-06-29T00:00:00Z</sbd:CreationDateAndTime>
    def create_creation_date_and_time_document_identification(creation_date_time):
        element = ET.Element("sbd:CreationDateAndTime")
        element.text = creation_date_time

        return element
    
    @staticmethod
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
    
    @staticmethod
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

    @staticmethod
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
    
    @staticmethod
    def create_sovos_document_for_legal_Invoice(invoice_element):
        #<svs:SovosDocument>
        sovos_document = ET.Element("svs:SovosDocument")
        #<svs:SovosLegalDocument>
        sovos_legal_document = ET.SubElement(sovos_document, "svs:SovosLegalDocument")
        #<enc:Base64Document>
        base64_document = ET.SubElement(sovos_legal_document, "enc:Base64Document")
        #<enc:EmbeddedDocument id="1" fileName="invoice-test-legal-insci.xml" mimeCode="application/xml">
        embedded_document = ET.SubElement(base64_document, "enc:EmbeddedDocument", id="1", fileName="invoice-test-legal-insci.xml", mimeCode="application/xml")
        # Add the provided Invoice element as base64 encoded
        xml_string = ET.tostring(invoice_element, encoding="utf-8", method="xml").decode()
        data_in_base64 = base64.b64encode(xml_string.encode('utf-8')).decode('utf-8')
        embedded_document.text = data_in_base64
        return sovos_document
   

