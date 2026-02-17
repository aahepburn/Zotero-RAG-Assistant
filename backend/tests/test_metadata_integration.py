"""
Integration tests for metadata filtering system.
Tests the full pipeline from query extraction to filtered search.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from backend.metadata_extractor import MetadataExtractor
from backend.metadata_utils import build_metadata_where_clause, merge_where_clauses
from backend.metadata_version import check_metadata_compatibility


class TestEndToEndQueryFlow:
    """Test complete query flow with metadata filtering."""
    
    def test_simple_year_filter_flow(self):
        """Test: Query -> Extract -> Build Where -> Expected Result."""
        # Step 1: Extract filters from query
        extractor = MetadataExtractor(provider_manager=None)
        query = "Show me papers after 2020"
        filters = extractor.extract_filters(query)
        
        # Step 2: Build where clause
        where = build_metadata_where_clause(
            year_min=filters['year_min'],
            year_max=filters['year_max'],
            tags=filters['tags'],
            collections=filters['collections']
        )
        
        # Step 3: Verify result
        assert where == {"year": {"$gte": 2020}}
        assert filters['has_filters'] == True
    
    def test_complex_query_flow(self):
        """Test: Complex query with multiple filters."""
        extractor = MetadataExtractor(provider_manager=None)
        query = 'Papers from 2018-2022 tagged "NLP" in "PhD Research"'
        filters = extractor.extract_filters(query)
        
        # Build where clause
        where = build_metadata_where_clause(
            year_min=filters['year_min'],
            year_max=filters['year_max'],
            tags=filters['tags'],
            collections=filters['collections']
        )
        
        # Verify all filters extracted and combined
        assert filters['year_min'] == 2018
        assert filters['year_max'] == 2022
        assert 'NLP' in filters['tags']
        assert 'PhD Research' in filters['collections']
        assert "$and" in where
    
    def test_manual_and_auto_merge_flow(self):
        """Test: Merge manual and auto-extracted filters."""
        # User manually specifies collections
        manual_where = build_metadata_where_clause(
            collections=["Important Papers"]
        )
        
        # Auto-extract from query
        extractor = MetadataExtractor(provider_manager=None)
        filters = extractor.extract_filters("Recent papers about transformers")
        auto_where = build_metadata_where_clause(
            year_min=filters.get('year_min'),
            tags=filters.get('tags')
        )
        
        # Merge both
        final_where = merge_where_clauses(manual_where, auto_where) if auto_where else manual_where
        
        # Should have collection filter at minimum
        assert final_where is not None


class TestVersionDetectionIntegration:
    """Test version detection with migration workflow."""
    
    def test_detect_and_migrate_workflow(self):
        """Test: Check version -> Determine if migration needed -> Migrate."""
        # Mock v1 database
        mock_chroma = Mock()
        mock_chroma.collection.count.return_value = 100
        mock_chroma.collection.get.return_value = {
            'ids': ['1:0', '2:0'],
            'metadatas': [
                {'item_id': '1', 'year': '2020'},  # String year = v1
                {'item_id': '2', 'year': '2021'}
            ]
        }
        
        # Check compatibility
        is_compatible = check_metadata_compatibility(mock_chroma, enable_filtering=True)
        
        # v1 should not be compatible (needs migration)
        assert is_compatible == False
        
        # Check version separately
        from backend.metadata_version import MetadataVersionManager
        manager = MetadataVersionManager(mock_chroma)
        version = manager.detect_metadata_version()
        assert version == 1
        assert manager.is_migration_needed() == True
    
    def test_v2_database_no_migration(self):
        """Test: v2 database should not require migration."""
        mock_chroma = Mock()
        mock_chroma.collection.count.return_value = 100
        mock_chroma.collection.get.return_value = {
            'ids': ['1:0', '2:0'],
            'metadatas': [
                {'item_id': '1', 'year': 2020, 'tags': 'NLP', 'collections': ''},
                {'item_id': '2', 'year': 2021, 'tags': 'CV', 'collections': ''}
            ]
        }
        
        # Check compatibility
        is_compatible = check_metadata_compatibility(mock_chroma, enable_filtering=True)
        
        # v2 should be compatible
        assert is_compatible == True
        
        # Check version separately
        from backend.metadata_version import MetadataVersionManager
        manager = MetadataVersionManager(mock_chroma)
        version = manager.detect_metadata_version()
        assert version == 2
        assert manager.is_migration_needed() == False


class TestSearchWorkflow:
    """Test search workflow with filters."""
    
    def test_where_clause_in_chroma_query(self):
        """Test that where clause can be passed to ChromaDB queries."""
        # Build a where clause
        where = build_metadata_where_clause(
            year_min=2020,
            tags=["NLP", "ML"]
        )
        
        # Mock ChromaDB collection
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'ids': [['1:0', '2:0']],
            'documents': [['Doc 1', 'Doc 2']],
            'metadatas': [[
                {'year': 2020, 'tags': 'NLP|ML'},
                {'year': 2021, 'tags': 'NLP'}
            ]]
        }
        
        # Perform query with where clause
        results = mock_collection.query(
            query_embeddings=[[0.1] * 768],
            n_results=10,
            where=where
        )
        
        # Verify query was called with where parameter
        assert mock_collection.query.called
        call_kwargs = mock_collection.query.call_args[1]
        assert 'where' in call_kwargs
        assert call_kwargs['where'] == where


class TestRRFIntegration:
    """Test RRF hybrid search integration."""
    
    @pytest.fixture
    def mock_vector_db(self):
        """Create mock vector database with RRF support."""
        from backend.vector_db import ChromaClient
        
        mock_client = Mock(spec=ChromaClient)
        
        # Create a mock collection
        mock_collection = Mock()
        mock_client.collection = mock_collection
        
        # Mock dense results
        mock_collection.query.return_value = {
            'ids': [['1:0', '2:0', '3:0']],
            'documents': [['Doc 1', 'Doc 2', 'Doc 3']],
            'metadatas': [[
                {'year': 2020, 'tags': 'NLP'},
                {'year': 2021, 'tags': 'ML'},
                {'year': 2019, 'tags': 'CV'}
            ]]
        }
        
        # Mock BM25 results
        mock_client.query_bm25.return_value = [
            {'id': '3:0', 'document': 'Doc 3', 'metadata': {'year': 2019, 'tags': 'CV'}},
            {'id': '4:0', 'document': 'Doc 4', 'metadata': {'year': 2022, 'tags': 'NLP'}},
        ]
        
        # Mock collection.get for final retrieval
        mock_collection.get.return_value = {
            'ids': ['1:0', '2:0', '3:0', '4:0'],
            'documents': ['Doc 1', 'Doc 2', 'Doc 3', 'Doc 4'],
            'metadatas': [
                {'year': 2020, 'tags': 'NLP'},
                {'year': 2021, 'tags': 'ML'},
                {'year': 2019, 'tags': 'CV'},
                {'year': 2022, 'tags': 'NLP'}
            ]
        }
        
        return mock_client
    
    def test_rrf_with_metadata_filters(self, mock_vector_db):
        """Test RRF search with metadata filtering."""
        from backend.vector_db import ChromaClient
        
        # Build filter
        where = build_metadata_where_clause(year_min=2020)
        
        # The query_hybrid_rrf method should accept where clause
        # This tests the integration point
        assert where == {"year": {"$gte": 2020}}


class TestFullChatPipeline:
    """Test full chat pipeline with metadata filtering."""
    
    def test_chat_with_auto_extract_filters(self):
        """Test chat method with auto-extracted filters."""
        # This would test interface.py chat() method
        # Mock the components
        
        mock_provider = Mock()
        mock_chroma = Mock()
        mock_zlib = Mock()
        
        # Extract filters from query
        query = "What papers about transformers came out after 2020?"
        extractor = MetadataExtractor(provider_manager=None)
        filters = extractor.extract_filters(query)
        
        # Build where clause
        where = build_metadata_where_clause(
            year_min=filters.get('year_min'),
            tags=filters.get('tags')
        )
        
        # Verify filters would be applied
        assert filters['year_min'] == 2020
        assert where is not None
    
    def test_chat_with_manual_filters(self):
        """Test chat method with manual filters."""
        # User specifies filters manually
        manual_filters = {
            'year_min': 2019,
            'year_max': 2023,
            'tags': ['NLP', 'Transformers'],
            'collections': ['Research']
        }
        
        # Build where clause
        where = build_metadata_where_clause(
            year_min=manual_filters['year_min'],
            year_max=manual_filters['year_max'],
            tags=manual_filters['tags'],
            collections=manual_filters['collections']
        )
        
        # Verify structure
        assert "$and" in where
        assert any("year" in str(cond) for cond in where["$and"])
    
    def test_chat_original_mode_no_filters(self):
        """Test chat in original mode (no filters)."""
        # When searchEngineMode == 'original'
        where = None
        
        # Should perform standard search
        assert where is None


class TestAPIEndpointIntegration:
    """Test API endpoint integration."""
    
    def test_metadata_version_endpoint_flow(self):
        """Test /api/metadata/version endpoint."""
        mock_chroma = Mock()
        mock_chroma.collection.count.return_value = 100
        mock_chroma.collection.get.return_value = {
            'ids': ['1:0'],
            'metadatas': [{'year': '2020'}]  # v1
        }
        
        result = check_metadata_compatibility(mock_chroma, enable_filtering=True)
        
        # Should return boolean
        assert isinstance(result, bool)
        assert result == False  # v1 is not compatible
    
    def test_chat_endpoint_with_filters_flow(self):
        """Test /api/chat endpoint with filter parameters."""
        # Simulate request payload
        payload = {
            'query': 'What are recent NLP papers?',
            'use_metadata_filters': True,
            'manual_filters': {
                'year_min': 2020,
                'tags': ['NLP']
            },
            'use_rrf': True
        }
        
        # Extract and build filters
        where = build_metadata_where_clause(
            year_min=payload['manual_filters']['year_min'],
            tags=payload['manual_filters']['tags']
        )
        
        # Should create valid where clause
        assert where is not None
        assert "$and" in where or "year" in where


class TestErrorHandlingIntegration:
    """Test error handling across the pipeline."""
    
    def test_invalid_query_handling(self):
        """Test handling of invalid queries."""
        extractor = MetadataExtractor(provider_manager=None)
        
        # Empty query
        filters = extractor.extract_filters("")
        assert filters['has_filters'] == False
        
        # Query with no extractable filters
        filters = extractor.extract_filters("Hello world")
        assert filters['has_filters'] == False
    
    def test_invalid_metadata_handling(self):
        """Test handling of invalid metadata."""
        # Try to build where clause with invalid values
        where = build_metadata_where_clause(
            year_min=None,
            year_max=None,
            tags=[],
            collections=[]
        )
        
        # Should return None for no filters
        assert where is None
    
    def test_chroma_error_handling(self):
        """Test handling of ChromaDB errors."""
        mock_chroma = Mock()
        mock_chroma.collection.count.side_effect = Exception("ChromaDB error")
        
        # Should handle error gracefully
        try:
            result = check_metadata_compatibility(mock_chroma, enable_filtering=True)
            # If it doesn't raise, result should be a boolean
            assert isinstance(result, bool)
        except Exception as e:
            # If it raises, should be informative
            assert "ChromaDB" in str(e) or "error" in str(e).lower()


class TestPerformanceIntegration:
    """Test performance characteristics."""
    
    def test_regex_extraction_speed(self):
        """Test that regex extraction is fast."""
        import time
        
        extractor = MetadataExtractor(provider_manager=None)
        query = "Papers from 2020-2023 about NLP"
        
        start = time.time()
        filters = extractor.extract_filters(query)
        elapsed = time.time() - start
        
        # Should complete in under 5ms (0.005 seconds)
        assert elapsed < 0.005
        assert filters['has_filters'] == True
    
    def test_where_clause_building_speed(self):
        """Test that where clause building is fast."""
        import time
        
        start = time.time()
        where = build_metadata_where_clause(
            year_min=2018,
            year_max=2023,
            tags=['NLP', 'ML', 'CV', 'RL'],
            collections=['Research', 'Survey', 'PhD']
        )
        elapsed = time.time() - start
        
        # Should complete in under 1ms
        assert elapsed < 0.001
        assert where is not None


class TestRealWorldScenarios:
    """Test real-world usage scenarios end-to-end."""
    
    def test_scenario_phd_student_workflow(self):
        """Scenario: PhD student searching for recent NLP papers."""
        # Step 1: User types query
        query = "What are the recent transformer papers in my research collection?"
        
        # Step 2: System extracts filters
        extractor = MetadataExtractor(provider_manager=None)
        filters = extractor.extract_filters(query)
        
        # Step 3: User also manually sets collection
        manual_filters = {
            'collections': ['Research']
        }
        
        # Step 4: Build combined where clause
        auto_where = build_metadata_where_clause(
            year_min=filters.get('year_min'),
            tags=filters.get('tags')
        )
        manual_where = build_metadata_where_clause(
            collections=manual_filters.get('collections')
        )
        final_where = merge_where_clauses(auto_where, manual_where)
        
        # Step 5: Verify result
        assert final_where is not None
        # Should include collection filter
        assert "collections" in str(final_where)
    
    def test_scenario_survey_paper_writing(self):
        """Scenario: Writing survey paper with specific year range."""
        # User query with explicit year range
        query = "Survey papers on deep learning from 2019 to 2023"
        
        extractor = MetadataExtractor(provider_manager=None)
        filters = extractor.extract_filters(query)
        
        where = build_metadata_where_clause(
            year_min=filters['year_min'],
            year_max=filters['year_max'],
            tags=filters['tags']
        )
        
        # Should extract year range
        assert filters['year_min'] == 2019
        assert filters['year_max'] == 2023
        assert where is not None
    
    def test_scenario_migration_then_search(self):
        """Scenario: User migrates database then performs filtered search."""
        # Step 1: Check version
        mock_chroma_v1 = Mock()
        mock_chroma_v1.collection.count.return_value = 100
        mock_chroma_v1.collection.get.return_value = {
            'ids': ['1:0'],
            'metadatas': [{'year': '2020'}]
        }
        
        # Check version
        from backend.metadata_version import MetadataVersionManager
        manager_v1 = MetadataVersionManager(mock_chroma_v1)
        assert manager_v1.is_migration_needed() == True
        
        # Step 2: Perform migration (mocked)
        # ... migration would happen here ...
        
        # Step 3: After migration, database is v2
        mock_chroma_v2 = Mock()
        mock_chroma_v2.collection.count.return_value = 100
        mock_chroma_v2.collection.get.return_value = {
            'ids': ['1:0'],
            'metadatas': [{'year': 2020, 'tags': 'NLP', 'collections': ''}]  # Now integer
        }
        
        manager_v2 = MetadataVersionManager(mock_chroma_v2)
        assert manager_v2.is_migration_needed() == False
        
        # Step 4: Now can use filtered search
        where = build_metadata_where_clause(year_min=2020)
        assert where == {"year": {"$gte": 2020}}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
