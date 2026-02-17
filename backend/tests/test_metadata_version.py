"""
Unit tests for metadata version detection.
Tests MetadataVersionManager class from metadata_version.py
"""

import pytest
from unittest.mock import Mock, MagicMock
from backend.metadata_version import MetadataVersionManager, check_metadata_compatibility


class TestMetadataVersionManager:
    """Test suite for MetadataVersionManager."""
    
    @pytest.fixture
    def mock_chroma_empty(self):
        """Mock ChromaDB client with empty collection."""
        mock = Mock()
        mock.collection.count.return_value = 0
        mock.collection.get.return_value = {
            'ids': [],
            'metadatas': [],
            'documents': []
        }
        return mock
    
    @pytest.fixture
    def mock_chroma_v1(self):
        """Mock ChromaDB client with v1 metadata (string year)."""
        mock = Mock()
        mock.collection.count.return_value = 100
        mock.collection.get.return_value = {
            'ids': ['1:0', '2:0', '3:0', '4:0', '5:0'],
            'metadatas': [
                {'item_id': '1', 'year': '2020', 'title': 'Paper 1'},
                {'item_id': '2', 'year': '2019', 'title': 'Paper 2'},
                {'item_id': '3', 'year': '2021', 'title': 'Paper 3'},
                {'item_id': '4', 'year': '2018', 'title': 'Paper 4'},
                {'item_id': '5', 'year': '', 'title': 'Paper 5'},
            ]
        }
        return mock
    
    @pytest.fixture
    def mock_chroma_v2(self):
        """Mock ChromaDB client with v2 metadata (integer year + tags + collections)."""
        mock = Mock()
        mock.collection.count.return_value = 100
        mock.collection.get.return_value = {
            'ids': ['1:0', '2:0', '3:0', '4:0', '5:0'],
            'metadatas': [
                {'item_id': '1', 'year': 2020, 'tags': 'NLP|ML', 'collections': 'Research', 'title': 'Paper 1'},
                {'item_id': '2', 'year': 2019, 'tags': 'CV', 'collections': '', 'title': 'Paper 2'},
                {'item_id': '3', 'year': 2021, 'tags': '', 'collections': 'PhD', 'title': 'Paper 3'},
                {'item_id': '4', 'year': 2018, 'tags': 'NLP', 'collections': 'Research|Survey', 'title': 'Paper 4'},
                {'item_id': '5', 'year': None, 'tags': '', 'collections': '', 'title': 'Paper 5'},
            ]
        }
        return mock
    
    @pytest.fixture
    def mock_chroma_mixed(self):
        """Mock ChromaDB client with mixed v1/v2 metadata."""
        mock = Mock()
        mock.collection.count.return_value = 100
        mock.collection.get.return_value = {
            'ids': ['1:0', '2:0', '3:0', '4:0', '5:0'],
            'metadatas': [
                {'item_id': '1', 'year': 2020, 'tags': 'NLP', 'collections': '', 'title': 'Paper 1'},  # v2
                {'item_id': '2', 'year': '2019', 'title': 'Paper 2'},  # v1
                {'item_id': '3', 'year': 2021, 'tags': 'ML', 'collections': 'Research', 'title': 'Paper 3'},  # v2
                {'item_id': '4', 'year': '2018', 'title': 'Paper 4'},  # v1
                {'item_id': '5', 'year': 2022, 'tags': '', 'collections': '', 'title': 'Paper 5'},  # v2
            ]
        }
        return mock
    
    def test_detect_version_empty(self, mock_chroma_empty):
        """Test version detection on empty database."""
        manager = MetadataVersionManager(mock_chroma_empty)
        version = manager.detect_metadata_version()
        assert version == 0
    
    def test_detect_version_v1(self, mock_chroma_v1):
        """Test version detection on v1 database (string year)."""
        manager = MetadataVersionManager(mock_chroma_v1)
        version = manager.detect_metadata_version()
        assert version == 1
    
    def test_detect_version_v2(self, mock_chroma_v2):
        """Test version detection on v2 database (integer year)."""
        manager = MetadataVersionManager(mock_chroma_v2)
        version = manager.detect_metadata_version()
        assert version == 2
    
    def test_detect_version_mixed(self, mock_chroma_mixed):
        """Test version detection on mixed database (majority wins)."""
        manager = MetadataVersionManager(mock_chroma_mixed)
        version = manager.detect_metadata_version()
        # 3 v2 chunks vs 2 v1 chunks, should return v2
        assert version == 2
    
    def test_is_migration_needed_empty(self, mock_chroma_empty):
        """Test migration check on empty database."""
        manager = MetadataVersionManager(mock_chroma_empty)
        # Empty database (version 0) technically needs migration to version 2
        assert manager.is_migration_needed() == True
    
    def test_is_migration_needed_v1(self, mock_chroma_v1):
        """Test migration check on v1 database."""
        manager = MetadataVersionManager(mock_chroma_v1)
        assert manager.is_migration_needed() == True
    
    def test_is_migration_needed_v2(self, mock_chroma_v2):
        """Test migration check on v2 database."""
        manager = MetadataVersionManager(mock_chroma_v2)
        assert manager.is_migration_needed() == False
    
    def test_get_migration_message_v0(self, mock_chroma_empty):
        """Test migration message for empty database."""
        manager = MetadataVersionManager(mock_chroma_empty)
        message = manager.get_migration_message()
        # Empty database should return None
        assert message is None
    
    def test_get_migration_message_v1(self, mock_chroma_v1):
        """Test migration message for v1 database."""
        manager = MetadataVersionManager(mock_chroma_v1)
        message = manager.get_migration_message()
        # v1 should have upgrade/migration message
        assert message is not None
        assert "metadata" in message.lower()
        assert "filtering" in message.lower()
    
    def test_get_migration_message_v2(self, mock_chroma_v2):
        """Test migration message for v2 database."""
        manager = MetadataVersionManager(mock_chroma_v2)
        message = manager.get_migration_message()
        # v2 should return None (already up to date)
        assert message is None
    
    def test_version_caching(self, mock_chroma_v2):
        """Test that version is cached after first detection."""
        manager = MetadataVersionManager(mock_chroma_v2)
        
        # First call
        version1 = manager.detect_metadata_version()
        
        # Second call should use cache
        version2 = manager.detect_metadata_version()
        
        assert version1 == version2
        # get should only be called once due to caching
        assert mock_chroma_v2.collection.get.call_count == 1
    
    def test_check_metadata_compatibility_v1(self, mock_chroma_v1):
        """Test compatibility check function for v1."""
        result = check_metadata_compatibility(mock_chroma_v1, enable_filtering=True)
        
        # v1 format should return False (not compatible with filtering)
        assert result == False
    
    def test_check_metadata_compatibility_v2(self, mock_chroma_v2):
        """Test compatibility check function for v2."""
        result = check_metadata_compatibility(mock_chroma_v2, enable_filtering=True)
        
        # v2 format should return True (compatible with filtering)
        assert result == True
    
    def test_sample_size_limit(self, mock_chroma_v2):
        """Test that sample size is limited to 10 chunks."""
        manager = MetadataVersionManager(mock_chroma_v2)
        manager.detect_metadata_version()
        
        # Verify get was called with limit=10
        mock_chroma_v2.collection.get.assert_called_once()
        call_kwargs = mock_chroma_v2.collection.get.call_args[1]
        assert call_kwargs.get('limit') == 10
    
    def test_version_voting_logic(self):
        """Test version voting with custom metadata."""
        mock = Mock()
        mock.collection.count.return_value = 100
        mock.collection.get.return_value = {
            'ids': ['1:0', '2:0', '3:0', '4:0', '5:0', '6:0', '7:0'],
            'metadatas': [
                {'year': 2020, 'tags': 'A'},  # v2
                {'year': 2020, 'tags': 'B'},  # v2
                {'year': '2020'},              # v1
                {'year': '2020'},              # v1
                {'year': '2020'},              # v1
                {'year': '2020'},              # v1
                {'year': 2020, 'tags': 'C'},  # v2
            ]
        }
        
        manager = MetadataVersionManager(mock)
        version = manager.detect_metadata_version()
        
        # 4 v1 vs 3 v2, should return v1
        assert version == 1


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_malformed_metadata(self):
        """Test handling of malformed metadata."""
        mock = Mock()
        mock.collection.count.return_value = 10
        mock.collection.get.return_value = {
            'ids': ['1:0', '2:0'],
            'metadatas': [
                {'item_id': '1'},  # Missing year
                None,              # Null metadata
            ]
        }
        
        manager = MetadataVersionManager(mock)
        # Should not crash, should default to v0 or v1
        version = manager.detect_metadata_version()
        assert version in [0, 1, 2]
    
    def test_empty_get_response(self):
        """Test handling of empty get response."""
        mock = Mock()
        mock.collection.count.return_value = 100
        mock.collection.get.return_value = {
            'ids': [],
            'metadatas': []
        }
        
        manager = MetadataVersionManager(mock)
        version = manager.detect_metadata_version()
        assert version == 0  # Should treat as empty
    
    def test_chroma_error_handling(self):
        """Test handling of ChromaDB errors."""
        mock = Mock()
        mock.collection.count.side_effect = Exception("ChromaDB error")
        
        manager = MetadataVersionManager(mock)
        # Should handle error gracefully
        try:
            version = manager.detect_metadata_version()
            # If it doesn't raise, it should return a safe default
            assert version in [0, 1, 2]
        except Exception as e:
            # If it does raise, it should be the original error
            assert "ChromaDB error" in str(e)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
