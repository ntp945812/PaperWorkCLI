class Document:
    """The base of a document, manager file by folders in structure as below:
    doc
    |─main-document
    |─reference
    |─scan
    |─sdi
    |─attachment
    |─other
    """
    def __init__(self, path):
        """Document initial by a path
        """