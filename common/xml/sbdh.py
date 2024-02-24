import base64
from datetime import datetime
import xml.etree.ElementTree as ET

from common.xml.ubl_namespaces import UBL_NAMESPACES_PREFIXES_ATTR

class StandardBusinessDocumentHeader:
    def __init__(self, header_version="1.0",
                 sender_vat=None,
                 receiver_vat=None,
                 sender_vat_country="XX",
                 receiver_vat_country="XX",
                 sender_company_code="SenderCompanyCode",
                 document_identification_standard="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
                 multiple_type_document_identification="false", 
                 scope_mapping='SCI-TO-LEGAL_INVOICE',
                 is_payload_SCI_UBL=True,
                 scope_version_identifier="1.2.2",
                 document_identification_type_version="2.1",
                 document_identification_instance_identifier="------",
                 output_schema_identifier="-----", 
                 process_type_identifier='Outbound',
                 sender_document_id_identifier=None,
                 document_type="Invoice",
                 sender_system_id="SystemERP",
                 business_service_name="Default",
                 company_branch=None):
        self.header_version = header_version
        self.sender_vat = sender_vat
        self.receiver_vat = receiver_vat
        self.sender_vat_country = sender_vat_country
        self.receiver_vat_country = receiver_vat_country
        self.sender_company_code = sender_company_code
        self.document_identification_standard = document_identification_standard
        self.multiple_type_document_identification = multiple_type_document_identification
        self.scope_mapping = scope_mapping
        self.is_payload_SCI_UBL = is_payload_SCI_UBL
        self.scope_version_identifier = scope_version_identifier
        self.document_identification_type_version = document_identification_type_version
        self.document_identification_instance_identifier = document_identification_instance_identifier
        self.output_schema_identifier = output_schema_identifier
        self.process_type_identifier = process_type_identifier
        self.sender_document_id_identifier = sender_document_id_identifier
        self.document_type = document_type
        self.sender_system_id = sender_system_id
        self.business_service_name = business_service_name
        self.company_branch = company_branch

    def envelope(self, invoice_element):
            #<sbd:StandardBusinessDocument xmlns=....
            root = ET.Element("sbd:StandardBusinessDocument", attrib=UBL_NAMESPACES_PREFIXES_ATTR)
            #<sbd:HeaderVersion>1.0</sbd:HeaderVersion>
            sbd_header = ET.SubElement(root, "sbd:StandardBusinessDocumentHeader")
            header_version = self.create_header_version_element(self.header_version)
            sbd_header.append(header_version)
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
            if self.is_payload_SCI_UBL:
                sovos_document = self.create_sovos_document_for_sci_Invoice(invoice_element)
            else:
                sovos_document = self.create_sovos_document_for_legal_Invoice(invoice_element)
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
   

