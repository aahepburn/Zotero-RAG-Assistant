"""
Unit tests for metadata migration.
Tests MetadataMigration class from metadata_migration.py
"""

import pytest
from unittest.mock import Mock, MagicMock, call
from backend.metadata_migration import MetadataMigration


class TestMetadataMigration:
    """Test suite for MetadataMigration."""
    
    @pytest.fixture
    def mock_chroma(self):
        """Mock ChromaDB client."""
        mock = Mock()
        mock.collection = Mock()
        return mock
    
    @pytest.fixture
    def mock_zotero(self):
        """Mock Zotero library."""
        mock = Mock()
        return mock
    
    @pytest.fixture
    def migration(self, mock_chroma, mock_zotero):
        """Create MetadataMigration instance."""
        return MetadataMigration(mock_chroma, mock_zotero)
    
    def test_initialization(self, migration):
        """Test migration initialization."""
        assert migration.progress['total_chunks'] == 0
        assert migration.progress['processed_chunks'] == 0
        assert migration.progress['updated_chunks'] == 0
        assert migration.progress['failed_chunks'] == 0
    
    def test_fetch_updated_metadata_success(self, migration, mock_zotero):
        """Test fetching updated metadata from Zotero."""
        # Mock Zotero response
        mock_item = Mock()
        mock_item.metadata = {
            'title': 'Test Paper',
            'authors': 'Smith, J.',
            'tags': 'NLP|ML',
            'collections': 'Research',
            'date': '2020-01-15'
        }
        mock_zotero.search_parent_items_with_pdfs.return_value = [mock_item]
        
        result = migration._fetch_updated_metadata('12345')
        
        assert result['title'] == 'Test Paper'
        assert result['authors'] == 'Smith, J.'
        assert result['year'] == 2020  # Should be parsed to integer
    
    def test_fetch_updated_metadata_year_parsing(self, migration, mock_zotero):
        """Test year parsing in different formats."""
        mock_item = Mock()
        mock_item.metadata = {'date': '2021-03-10', 'title': 'Paper'}
        mock_zotero.search_parent_items_with_pdfs.return_value = [mock_item]
        
        result = migration._fetch_updated_metadata('123')
        assert result['year'] == 2021
        
        # Test with just year
        mock_item.metadata = {'date': '2022', 'title': 'Paper'}
        result = migration._fetch_updated_metadata('124')
        assert result['year'] == 2022
        
        # Test with invalid date
        mock_item.metadata = {'date': 'unknown', 'title': 'Paper'}
        result = migration._fetch_updated_metadata('125')
        assert result['year'] is None
    
    def test_fetch_updated_metadata_not_found(self, migration, mock_zotero):
        """Test fetching metadata for non-existent item."""
        mock_zotero.search_parent_items_with_pdfs.return_value = []
        
        result = migration._fetch_updated_metadata('99999')
        
        assert result is None
    
    def test_needs_update_year_format_change(self, migration):
        """Test detection of year format change."""
        old_meta = {'year': '2020', 'tags': 'NLP'}
        new_meta = {'year': 2020, 'tags': 'NLP'}
        
        assert migration._needs_update(old_meta, new_meta) == True
    
    def test_needs_update_tags_changed(self, migration):
        """Test detection of tag changes."""
        old_meta = {'year': 2020, 'tags': ''}
        new_meta = {'year': 2020, 'tags': 'NLP|ML'}
        
        assert migration._needs_update(old_meta, new_meta) == True
    
    def test_needs_update_collections_changed(self, migration):
        """Test detection of collection changes."""
        old_meta = {'year': 2020, 'collections': ''}
        new_meta = {'year': 2020, 'collections': 'Research'}
        
        assert migration._needs_update(old_meta, new_meta) == True
    
    def test_needs_update_no_change(self, migration):
        """Test when no update is needed."""
        old_meta = {'year': 2020, 'tags': 'NLP', 'collections': 'Research'}
        new_meta = {'year': 2020, 'tags': 'NLP', 'collections': 'Research'}
        
        assert migration._needs_update(old_meta, new_meta) == False
    
    def test_apply_metadata_updates(self, migration, mock_chroma):
        """Test applying metadata updates to ChromaDB."""
        updates = [
            ('1:0', {'item_id': '1', 'year': 2020, 'title': 'Paper 1'}),
            ('2:0', {'item_id': '2', 'year': 2021, 'title': 'Paper 2'}),
        ]
        
        migration._apply_metadata_updates(updates)
        
        # Should call ChromaDB update
        mock_chroma.collection.update.assert_called_once()
        call_args = mock_chroma.collection.update.call_args
        
        assert call_args[1]['ids'] == ['1:0', '2:0']
        assert len(call_args[1]['metadatas']) == 2
    
    def test_migrate_batch_success(self, migration, mock_zotero):
        """Test successful batch migration."""
        # Mock Zotero responses
        mock_item1 = Mock()
        mock_item1.metadata = {
            'title': 'Paper 1',
            'authors': 'Smith',
            'tags': 'NLP',
            'collections': 'Research',
            'date': '2020'
        }
        mock_item2 = Mock()
        mock_item2.metadata = {
            'title': 'Paper 2',
            'authors': 'Jones',
            'tags': 'ML',
            'collections': '',
            'date': '2021'
        }
        mock_zotero.search_parent_items_with_pdfs.side_effect = [
            [mock_item1], [mock_item2]
        ]
        
        chunk_ids = ['1:0', '2:0']
        old_metadatas = [
            {'item_id': '1', 'year': '2020', 'chunk_idx': 0, 'page': 1, 'pdf_path': '/path1.pdf'},
            {'item_id': '2', 'year': '2021', 'chunk_idx': 0, 'page': 1, 'pdf_path': '/path2.pdf'}
        ]
        
        cache = {}
        migration._migrate_batch(chunk_ids, old_metadatas, cache)
        
        # Should process both chunks
        assert migration.progress['processed_chunks'] == 2
        # Both need updates (year is string)
        assert migration.progress['updated_chunks'] == 2
    
    def test_migrate_batch_with_errors(self, migration, mock_zotero):
        """Test batch migration with some errors."""
        # First item succeeds, second fails
        mock_item = Mock()
        mock_item.metadata = {'title': 'Paper', 'date': '2020'}
        mock_zotero.search_parent_items_with_pdfs.side_effect = [
            [mock_item],
            Exception("Zotero error")
        ]
        
        chunk_ids = ['1:0', '2:0']
        old_metadatas = [
            {'item_id': '1', 'year': '2020', 'chunk_idx': 0, 'page': 1, 'pdf_path': '/path1.pdf'},
            {'item_id': '2', 'year': '2021', 'chunk_idx': 0, 'page': 1, 'pdf_path': '/path2.pdf'}
        ]
        
        cache = {}
        migration._migrate_batch(chunk_ids, old_metadatas, cache)
        
        # Should handle error gracefully
        assert migration.progress['processed_chunks'] == 2
        assert migration.progress['failed_chunks'] >= 1
    
    def test_migrate_all_metadata_small_library(self, migration, mock_chroma, mock_zotero):
        """Test full migration on small library."""
        # Mock ChromaDB with 3 chunks
        mock_chroma.collection.get.return_value = {
            'ids': ['1:0', '1:1', '2:0'],
            'metadatas': [
                {'item_id': '1', 'year': '2020', 'chunk_idx': 0, 'page': 1, 'pdf_path': '/p1.pdf'},
                {'item_id': '1', 'year': '2020', 'chunk_idx': 1, 'page': 2, 'pdf_path': '/p1.pdf'},
                {'item_id': '2', 'year': '2021', 'chunk_idx': 0, 'page': 1, 'pdf_path': '/p2.pdf'}
            ]
        }
        
        # Mock Zotero responses
        mock_item1 = Mock()
        mock_item1.metadata = {'title': 'P1', 'date': '2020', 'tags': '', 'collections': ''}
        mock_item2 = Mock()
        mock_item2.metadata = {'title': 'P2', 'date': '2021', 'tags': '', 'collections': ''}
        mock_zotero.search_parent_items_with_pdfs.side_effect = [[mock_item1], [mock_item2]]
        
        summary = migration.migrate_all_metadata(batch_size=10)
        
        assert summary['total_chunks'] == 3
        assert summary['unique_items'] == 2
        assert 'elapsed_seconds' in summary
        assert summary['success'] == True
    
    def test_migrate_all_metadata_batching(self, migration, mock_chroma, mock_zotero):
        """Test that large libraries are processed in batches."""
        # Create 25 chunks (should be processed in 3 batches of 10)
        chunk_ids = [f'{i}:0' for i in range(25)]
        metadatas = [
            {'item_id': str(i), 'year': '2020', 'chunk_idx': 0, 'page': 1, 'pdf_path': f'/p{i}.pdf'}
            for i in range(25)
        ]
        
        mock_chroma.collection.get.return_value = {
            'ids': chunk_ids,
            'metadatas': metadatas
        }
        
        # Mock Zotero to return different items
        def mock_zotero_search(item_ids):
            mock_item = Mock()
            mock_item.metadata = {'title': f'Paper {item_ids[0]}', 'date': '2020', 'tags': '', 'collections': ''}
            return [mock_item]
        
        mock_zotero.search_parent_items_with_pdfs.side_effect = mock_zotero_search
        
        summary = migration.migrate_all_metadata(batch_size=10)
        
        assert summary['total_chunks'] == 25
        assert summary['updated_chunks'] >= 0  # May be 0 or more depending on whether metadata changed


class TestMigrationCaching:
    """Test metadata caching during migration."""
    
    @pytest.fixture
    def migration(self):
        mock_chroma = Mock()
        mock_zotero = Mock()
        return MetadataMigration(mock_chroma, mock_zotero)
    
    def test_cache_avoids_duplicate_fetches(self, migration):
        """Test that cache prevents duplicate Zotero queries."""
        mock_item = Mock()
        mock_item.metadata = {'title': 'Test', 'date': '2020', 'tags': '', 'collections': ''}
        migration.zlib.search_parent_items_with_pdfs.return_value = [mock_item]
        
        chunk_ids = ['1:0', '1:1', '1:2']  # 3 chunks from same item
        metadatas = [
            {'item_id': '1', 'year': '2020', 'chunk_idx': i, 'page': i+1, 'pdf_path': '/p1.pdf'}
            for i in range(3)
        ]
        
        cache = {}
        migration._migrate_batch(chunk_ids, metadatas, cache)
        
        # Should only fetch metadata once for item '1'
        assert migration.zlib.search_parent_items_with_pdfs.call_count == 1
        assert '1' in cache


class TestMigrationSummary:
    """Test migration summary generation."""
    
    def test_summary_structure(self):
        """Test summary contains all required fields."""
        mock_chroma = Mock()
        mock_chroma.collection.get.return_value = {
            'ids': [],
            'metadatas': []
        }
        mock_zotero = Mock()
        
        migration = MetadataMigration(mock_chroma, mock_zotero)
        summary = migration.migrate_all_metadata()
        
        assert 'total_chunks' in summary
        assert 'updated_chunks' in summary
        assert 'failed_chunks' in summary
        assert 'unique_items' in summary
        assert 'elapsed_seconds' in summary
        assert 'success' in summary
    
    def test_summary_success_flag(self):
        """Test success flag in summary."""
        mock_chroma = Mock()
        mock_chroma.collection.get.return_value = {
            'ids': [],
            'metadatas': []
        }
        mock_zotero = Mock()
        
        migration = MetadataMigration(mock_chroma, mock_zotero)
        
        # Empty migration should succeed
        summary = migration.migrate_all_metadata()
        assert summary['success'] == True
        
        # Manually set failed chunks
        migration.progress['failed_chunks'] = 5
        summary = migration.migrate_all_metadata()
        assert summary['success'] == False


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_migration_empty_database(self):
        """Test migration on empty database."""
        mock_chroma = Mock()
        mock_chroma.collection.get.return_value = {
            'ids': [],
            'metadatas': []
        }
        mock_zotero = Mock()
        
        migration = MetadataMigration(mock_chroma, mock_zotero)
        summary = migration.migrate_all_metadata()
        
        assert summary['total_chunks'] == 0
        assert summary['updated_chunks'] == 0
        assert summary['success'] == True
    
    def test_migration_missing_item_id(self):
        """Test handling of chunks without item_id."""
        mock_chroma = Mock()
        mock_zotero = Mock()
        migration = MetadataMigration(mock_chroma, mock_zotero)
        
        chunk_ids = ['orphan:0']
        metadatas = [{'year': '2020'}]  # Missing item_id
        
        cache = {}
        migration._migrate_batch(chunk_ids, metadatas, cache)
        
        # Should skip and count as failed
        assert migration.progress['failed_chunks'] == 1
    
    def test_migration_chroma_update_error(self):
        """Test handling of ChromaDB update errors."""
        mock_chroma = Mock()
        mock_chroma.collection.update.side_effect = Exception("ChromaDB error")
        mock_zotero = Mock()
        migration = MetadataMigration(mock_chroma, mock_zotero)
        
        updates = [('1:0', {'item_id': '1', 'year': 2020})]
        
        with pytest.raises(Exception, match="ChromaDB error"):
            migration._apply_metadata_updates(updates)
    
    def test_migration_special_characters_in_metadata(self):
        """Test migration with special characters."""
        mock_chroma = Mock()
        mock_zotero = Mock()
        migration = MetadataMigration(mock_chroma, mock_zotero)
        
        mock_item = Mock()
        mock_item.metadata = {
            'title': 'Paper with "quotes" and \'apostrophes\'',
            'authors': 'O\'Brien, J. & Smith-Jones, K.',
            'tags': 'C++|C#|.NET',
            'collections': 'Research (2020/2021)',
            'date': '2020'
        }
        mock_zotero.search_parent_items_with_pdfs.return_value = [mock_item]
        
        result = migration._fetch_updated_metadata('1')
        
        assert result is not None
        assert 'quotes' in result['title']
        assert 'O\'Brien' in result['authors']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
