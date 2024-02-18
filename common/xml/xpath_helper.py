# Returns the fist xpath that existis in the xml
def get_element_by_xpath_with_namespaces(xml_sci_element, xpaths, namespaces):
    for xpath in xpaths:
        result_element = xml_sci_element.find(xpath, namespaces)
        if result_element is not None:
            return result_element

    return result_element