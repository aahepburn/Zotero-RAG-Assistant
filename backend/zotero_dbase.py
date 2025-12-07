#zotero_dbase.py
import sqlite3
import os
import threading
from contextlib import contextmanager
from backend.zoteroitem import ZoteroItem
from pathlib import Path

class ZoteroLibrary:
    def __init__(self, db_path):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
    
    def _get_connection(self):
        """Get or create thread-local database connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                f'file:{self.db_path}?mode=ro', 
                uri=True, 
                check_same_thread=True  # Changed to True for safety
            )
            # Enable shared cache for read-only connections
            self._local.conn.isolation_level = None
        return self._local.conn
    
    @contextmanager
    def _cursor(self):
        """Context manager for thread-safe cursor access."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def search_parent_items(self, 
                            authors=None, 
                            titles=None, 
                            dates=None, 
                            tags=None, 
                            collections=None):
        filters = []
        params = []

        # Author filter
        if authors:
            filters.append("(" + " OR ".join(["cr.lastName LIKE ?"] * len(authors)) + ")")
            params += [f"%{author}%" for author in authors]
        # Title filter
        if titles:
            filters.append("(" + " OR ".join(["v_title.value LIKE ?"] * len(titles)) + ")")
            params += [f"%{title}%" for title in titles]
        # Date filter
        if dates:
            filters.append("(" + " OR ".join(["v_date.value LIKE ?"] * len(dates)) + ")")
            params += [f"%{date}%" for date in dates]
        # Tag filter
        if tags:
            filters.append("(" + " OR ".join(["t.name LIKE ?"] * len(tags)) + ")")
            params += [f"%{tag}%" for tag in tags]
        # Collection filter
        if collections:
            filters.append("(" + " OR ".join(["c.collectionName LIKE ?"] * len(collections)) + ")")
            params += [f"%{coll}%" for coll in collections]

        where_clause = " AND ".join(filters) if filters else "1"
        query = f"""
        SELECT 
            i.itemID,
            i.key,
            v_title.value AS title,
            v_date.value AS date
        FROM items i
        JOIN itemCreators ic ON i.itemID = ic.itemID
        JOIN creators cr ON ic.creatorID = cr.creatorID
        JOIN itemData d_title ON i.itemID = d_title.itemID AND d_title.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'title')
        JOIN itemDataValues v_title ON d_title.valueID = v_title.valueID
        LEFT JOIN itemData d_date ON i.itemID = d_date.itemID AND d_date.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'date')
        LEFT JOIN itemDataValues v_date ON d_date.valueID = v_date.valueID
        LEFT JOIN itemTags it ON i.itemID = it.itemID
        LEFT JOIN tags t ON it.tagID = t.tagID
        LEFT JOIN collectionItems ci ON i.itemID = ci.itemID
        LEFT JOIN collections c ON ci.collectionID = c.collectionID
        WHERE {where_clause}
        """
        with self._cursor() as cur:
            cur.execute(query, tuple(params))
            return cur.fetchall()
    

    def search_parent_items_with_pdfs(self, 
                                      authors=None, 
                                      titles=None, 
                                      dates=None, 
                                      tags=None, 
                                      collections=None):
        filters = []
        params = []

        # Add filters as needed (same as above for search_parent_items)
        # You can implement the filter logic

        where_clause = " AND ".join(filters) if filters else "1"
        query = f"""
        SELECT 
            i.itemID,
            i.key,
            v_title.value AS title,
            v_date.value AS date,
            GROUP_CONCAT(DISTINCT cr.lastName) AS authors,
            GROUP_CONCAT(DISTINCT t.name) AS tags,
            GROUP_CONCAT(DISTINCT c.collectionName) AS collections,
            att.key AS attachment_key,
            att_path.path AS attachment_path
        FROM items i
        JOIN itemCreators ic ON i.itemID = ic.itemID
        JOIN creators cr ON ic.creatorID = cr.creatorID
        JOIN itemData d_title ON i.itemID = d_title.itemID AND d_title.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'title')
        JOIN itemDataValues v_title ON d_title.valueID = v_title.valueID
        LEFT JOIN itemData d_date ON i.itemID = d_date.itemID AND d_date.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'date')
        LEFT JOIN itemDataValues v_date ON d_date.valueID = v_date.valueID
        LEFT JOIN itemTags it ON i.itemID = it.itemID
        LEFT JOIN tags t ON it.tagID = t.tagID
        LEFT JOIN collectionItems ci ON i.itemID = ci.itemID
        LEFT JOIN collections c ON ci.collectionID = c.collectionID

        LEFT JOIN itemAttachments ia ON i.itemID = ia.parentItemID
        LEFT JOIN items att ON ia.itemID = att.itemID
        LEFT JOIN itemData att_data ON att.itemID = att_data.itemID AND att_data.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'mimeType')
        LEFT JOIN itemDataValues att_mime ON att_data.valueID = att_mime.valueID
        LEFT JOIN itemAttachments att_path ON att.itemID = att_path.itemID

        WHERE {where_clause}
        AND (att_mime.value = 'application/pdf' OR att_path.path LIKE '%.pdf')
        GROUP BY i.itemID
        """

        with self._cursor() as cur:
            cur.execute(query, tuple(params))
            results = cur.fetchall()
        # Use cross-platform path relative to Zotero database location
        # The storage directory is typically at the same level as the database
        db_parent = Path(self.db_path).parent
        storage_dir = str(db_parent / "storage")
        zotero_items = []

        for item in results:
            pdf_full_path = None
            if item[7] and item[8]:
                # Clean the attachment_path to get only the actual filename
                base_filename = item[8]
                # Remove prefixes like 'storage:' if present
                if base_filename and ':' in base_filename:
                    base_filename = base_filename.split(':')[-1]
                # Remove any leading directories or slashes
                base_filename = os.path.basename(base_filename)
                # Now build the correct full path
                pdf_full_path = os.path.join(storage_dir, item[7], base_filename) if base_filename else None

            metadata = {
                'item_id': str(item[0]),
                'key': item[1],
                'title': item[2],
                'date': item[3],
                'authors': item[4],       
                'tags': item[5],           
                'collections': item[6],    
                'attachment_key': item[7],
                'attachment_path': item[8],
                'pdf_path': pdf_full_path
            }
            zotero_items.append(ZoteroItem(filepath=pdf_full_path, metadata=metadata))
        return zotero_items
    
    def close(self):
        """Close thread-local connections. Call this on shutdown."""
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None

