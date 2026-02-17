"""
ChromaDB metadata format versioning system.
Ensures backward compatibility during metadata schema changes.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

CURRENT_METADATA_VERSION = 2  # Version 2 = year as integer
LEGACY_METADATA_VERSION = 1   # Version 1 = year as string

class MetadataVersionManager:
    """Manage ChromaDB metadata format versions."""
    
    def __init__(self, chroma_client):
        self.chroma = chroma_client
        self._cached_version = None
    
    def detect_metadata_version(self) -> int:
        """
        Detect which metadata format version is in ChromaDB.
        
        Returns:
            1 = Legacy format (year as string, may lack tags/collections)
            2 = Current format (year as integer, all fields present)
            0 = Empty or corrupted database
        """
        if self._cached_version is not None:
            return self._cached_version
        
        try:
            # Sample a few chunks to detect format
            results = self.chroma.collection.get(limit=10)
            
            if not results or not results.get('metadatas'):
                logger.warning("ChromaDB appears empty")
                self._cached_version = 0
                return 0
            
            # Check multiple chunks for consistency
            version_votes = []
            
            for meta in results['metadatas'][:10]:
                if not meta:
                    continue
                
                year = meta.get('year')
                has_tags = 'tags' in meta
                has_collections = 'collections' in meta
                
                # Version 2: year is int (including -1 sentinel) or missing, has tags/collections keys
                # Note: ChromaDB strips None values, so missing keys might indicate None was set
                if (isinstance(year, int) or year is None) and has_tags and has_collections:
                    version_votes.append(2)
                # Version 1: year is string or missing required keys
                elif isinstance(year, str) or not (has_tags and has_collections):
                    version_votes.append(1)
            
            if not version_votes:
                logger.warning("Could not determine metadata version")
                self._cached_version = 0
                return 0
            
            # Majority vote
            detected_version = max(set(version_votes), key=version_votes.count)
            self._cached_version = detected_version
            
            logger.info(f"Detected ChromaDB metadata version: {detected_version}")
            return detected_version
            
        except Exception as e:
            logger.error(f"Error detecting metadata version: {e}")
            self._cached_version = 0
            return 0
    
    def is_migration_needed(self) -> bool:
        """Check if migration is needed to use metadata filtering."""
        current_version = self.detect_metadata_version()
        return current_version < CURRENT_METADATA_VERSION
    
    def get_migration_message(self) -> Optional[str]:
        """Get user-friendly message about migration requirements."""
        version = self.detect_metadata_version()
        
        if version == 0:
            return None  # Empty DB, no message needed
        elif version == 1:
            return (
                "⚠️ Metadata Filtering Upgrade Available\n\n"
                "Your ChromaDB uses an older metadata format. To enable advanced "
                "filtering features (search by tags, collections, years), please:\n\n"
                "1. Click 'Sync Metadata' for quick update (5-10 min), or\n"
                "2. Full reindex for best results (may take longer)\n\n"
                "Current features will continue to work normally."
            )
        else:
            return None  # Already up to date


def check_metadata_compatibility(chroma_client, enable_filtering: bool = True) -> bool:
    """
    Check if metadata filtering can be safely enabled.
    
    Args:
        chroma_client: ChromaDB client instance
        enable_filtering: Whether user wants to enable filtering
    
    Returns:
        True if filtering can be enabled, False otherwise
    """
    if not enable_filtering:
        return True  # No compatibility check needed
    
    manager = MetadataVersionManager(chroma_client)
    version = manager.detect_metadata_version()
    
    if version == CURRENT_METADATA_VERSION:
        logger.info("✅ Metadata format compatible with filtering")
        return True
    elif version == LEGACY_METADATA_VERSION:
        logger.warning("⚠️ Metadata filtering disabled: legacy format detected")
        logger.warning("   Run migration to enable filtering features")
        return False
    else:
        logger.warning("⚠️ Metadata filtering disabled: unknown format")
        return False
