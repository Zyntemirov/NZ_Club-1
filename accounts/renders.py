from rest_framework_xml.renderers import XMLRenderer


class MyXMLRenderer(XMLRenderer):
    root_tag_name = 'response'