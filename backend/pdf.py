#pdf.py
import fitz


class PDF:
    """
    Handles PDF file operations for Zotero library items, including text extraction, metadata access, and page/annotation utilities.

    This class can be instantiated with either a ZoteroItem object or a direct file path. All standard PDF operations (extracting full or chunked text, reading metadata, counting pages, and fetching annotations) are available. When a ZoteroItem is provided, richer metadata and integration with the library are supported.

    Attributes:
        filepath (str): Path to the PDF file on disk.
        metadata (dict): Optional metadata from Zotero or PDF.
        zitem (ZoteroItem, optional): If provided, the ZoteroItem associated with this file.

    Methods:
        open(): Opens the PDF file for further operations.
        extract_text(max_chars=2000): Extracts up to `max_chars` of the PDF's text content.
        num_pages(): Returns the number of pages in the PDF.
        extract_text_by_page(page_number): Extracts text from the specified page.
        get_metadata(): Returns metadata from the ZoteroItem (preferred) or directly from the PDF file.
        extract_all_text(): Extracts and returns text of all pages in the PDF as a list of strings.
        get_annotations(): Returns a list of annotations present in the PDF.

    Typical usage:
        pdf = PDF(zotero_item)
        text = pdf.extract_text()
        meta = pdf.get_metadata()
    """

    def __init__(self, zotero_item_or_path):
        if hasattr(zotero_item_or_path, "filepath"):
            self.filepath = zotero_item_or_path.filepath
            self.metadata = getattr(zotero_item_or_path, "metadata", {})
            self.zitem = zotero_item_or_path
        else:
            self.filepath = zotero_item_or_path
            self.metadata = {}
            self.zitem = None
        self.doc = None

    def open(self):
        self.doc = fitz.open(self.filepath)

    def extract_text(self, max_chars=2000):
        self.doc = fitz.open(self.filepath)
        text = ""
        for page in self.doc:
            text += page.get_text()
            if len(text) >= max_chars:
                break
        self.doc.close()
        return text[:max_chars]
    
    def num_pages(self):
        self.doc = fitz.open(self.filepath)
        count = len(self.doc)
        self.doc.close()
        return count

    def extract_text_by_page(self, page_number):
        self.doc = fitz.open(self.filepath)
        text = self.doc[page_number].get_text()
        self.doc.close()
        return text
    
    def get_metadata(self):
        if self.zitem and self.zitem.metadata:
            return self.zitem.metadata
        self.doc = fitz.open(self.filepath)
        metadata = self.doc.metadata
        self.doc.close()
        return metadata  # return a dict
    
    def extract_all_text(self):
        """Retrieves all the text of the PDF by page. stored by page too."""
        self.doc = fitz.open(self.filepath)
        text_chunks = [page.get_text() for page in self.doc]
        self.doc.close()
        return text_chunks  # list of strings, one per page
    
    def extract_text_with_pages(self):
        """Extract text from PDF with page numbers preserved.
        
        Returns:
            List of dicts with 'page_num' and 'text' keys
        """
        self.doc = fitz.open(self.filepath)
        pages_data = []
        for i, page in enumerate(self.doc):
            text = page.get_text()
            if text.strip():  # Only include pages with text
                pages_data.append({
                    'page_num': i + 1,  # 1-indexed page numbers
                    'text': text
                })
        self.doc.close()
        return pages_data
    
    def get_annotations(self):
        self.doc = fitz.open(self.filepath)
        annots = []
        for page in self.doc:
            for annot in page.annots():
                annots.append(annot.info)
        self.doc.close()
        return annots  # list of annotation dicts

    def extract_text_for_items(items):
        enriched_items = []
        for zitem in items:
            if hasattr(zitem, "filepath"):  # Ensure it's a ZoteroItem
                pdf = PDF(zitem)
                text = pdf.extract_text()
                if text:
                    zitem.metadata['text'] = text
                    enriched_items.append(zitem)
        return enriched_items

    








