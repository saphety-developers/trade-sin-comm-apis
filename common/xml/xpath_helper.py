

class XPATHelper:
    XPATH_MAPPINGS = {
        'SCI': {
            'sender_vat': [
                                "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']",
                                "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='HQ']",
                                "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='CRN']",
                                "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID"
                            ],
            'sender_vat_country':[
                                    "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']",
                                    "./cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode"
                                ],
            'receiver_vat': [
                                "./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']",
                                "./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='NAT']",
                                "./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID"
                            ],
            'receiver_vat_country': [
                                "./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']",
                                "./cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode",
                                "./Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID"
                                ],
            'doc_number': ["./cbc:ID"]
        },
        'IT': {
            'sender_vat': ["./FatturaElettronicaHeader/CedentePrestatore/DatiAnagrafici/IdFiscaleIVA/IdCodice"],
            'sender_vat_country': ["./FatturaElettronicaHeader/CedentePrestatore/DatiAnagrafici/IdFiscaleIVA/IdPaese"],
            'receiver_vat': ["./FatturaElettronicaHeader/CessionarioCommittente/DatiAnagrafici/IdFiscaleIVA/IdCodice",
                            "./FatturaElettronicaHeader/CessionarioCommittente/DatiAnagrafici/CodiceFiscale"],
            'receiver_vat_country': ["./FatturaElettronicaHeader/CessionarioCommittente/DatiAnagrafici/IdFiscaleIVA/IdPaese"],
            'doc_number': ["./FatturaElettronicaBody/DatiGenerali/DatiGeneraliDocumento/Numero"]
        },
        'SA': {
            'sender_vat': ["./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='CRN']"],
            'sender_vat_country': ["./cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode"],
            'receiver_vat': ["./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='NAT']"],
            'receiver_vat_country': ["./cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode"],
            'doc_number': ["./cbc:ID"]
        },
        'RO': {
            'sender_vat': ["./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"],
            'sender_vat_country': ["./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"],
            'receiver_vat': ["./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"],
            'receiver_vat_country': ["./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"],
            'doc_number': ["./cbc:ID"]
        },
        'FR': {
            'sender_vat': ['/party/emisseur/id'],
            'receiver_vat': ['/party/recepteur/id'],
        }
    }

    @classmethod
    def get_xpaths_for_property(cls, format, attribute) :
        return cls.XPATH_MAPPINGS[format][attribute]
    # Returns the fist xpath that existis in the xml
    @classmethod
    def get_element_by_xpaths(cls, xml_invoice_element, xpaths, namespaces):
        for xpath in xpaths:
            result_element = xml_invoice_element.find(xpath, namespaces)
            if result_element is not None:
                return result_element

        return result_element