"""
Tests for external API utilities.

Tests Google Books and Semantic Scholar API integrations with
proper error handling and fallback scenarios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.external_api_utils import (
    fetch_google_book_reviews,
    fetch_semantic_scholar_data,
    _match_paper_by_author
)


class TestGoogleBooksAPI:
    """Tests for Google Books API integration."""
    
    def test_missing_isbn_raises_error(self):
        """Test that missing ISBN raises ValueError."""
        with pytest.raises(ValueError, match="ISBN is required"):
            fetch_google_book_reviews("", "test_key")
    
    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            fetch_google_book_reviews("1234567890", "")
    
    @patch('backend.external_api_utils.requests.get')
    def test_successful_isbn_lookup(self, mock_get):
        """Test successful ISBN lookup returns book data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [{
                'volumeInfo': {
                    'title': 'Test Book',
                    'authors': ['Test Author'],
                    'description': 'Test description',
                    'previewLink': 'http://preview.com',
                    'infoLink': 'http://info.com'
                }
            }]
        }
        mock_get.return_value = mock_response
        
        result = fetch_google_book_reviews("1234567890", "test_key")
        
        assert len(result) == 1
        assert result[0]['title'] == 'Test Book'
        assert result[0]['authors'] == ['Test Author']
    
    @patch('backend.external_api_utils.requests.get')
    def test_no_results_returns_empty_list(self, mock_get):
        """Test that no results returns empty list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response
        
        result = fetch_google_book_reviews("0000000000", "test_key")
        
        assert result == []
    
    @patch('backend.external_api_utils.requests.get')
    def test_timeout_returns_empty_list(self, mock_get):
        """Test that timeout returns empty list."""
        mock_get.side_effect = Exception("Timeout")
        
        result = fetch_google_book_reviews("1234567890", "test_key")
        
        assert result == []
    
    @patch('backend.external_api_utils.requests.get')
    def test_http_error_returns_empty_list(self, mock_get):
        """Test that HTTP error returns empty list."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_get.return_value = mock_response
        
        result = fetch_google_book_reviews("1234567890", "test_key")
        
        assert result == []


class TestSemanticScholarAPI:
    """Tests for Semantic Scholar API integration."""
    
    def test_missing_doi_and_title_returns_none(self):
        """Test that missing both DOI and title returns None."""
        result = fetch_semantic_scholar_data()
        assert result is None
    
    @patch('backend.external_api_utils.SemanticScholar')
    def test_successful_doi_lookup(self, mock_sch_class):
        """Test successful DOI lookup returns paper data."""
        mock_sch = Mock()
        mock_paper = {
            'title': 'Test Paper',
            'abstract': 'Test abstract',
            'year': 2023,
            'authors': [{'name': 'Test Author'}],
            'citationCount': 10,
            'citations': [],
            'references': [],
            'url': 'http://test.com',
            'externalIds': {'DOI': '10.1234/test'}
        }
        mock_sch.get_paper.return_value = mock_paper
        mock_sch_class.return_value = mock_sch
        
        result = fetch_semantic_scholar_data(doi="10.1234/test")
        
        assert result is not None
        assert result['title'] == 'Test Paper'
        assert result['abstract'] == 'Test abstract'
        assert result['year'] == 2023
        assert len(result['authors']) == 1
        assert result['authors'][0] == 'Test Author'
        assert result['citation_count'] == 10
    
    @patch('backend.external_api_utils.SemanticScholar')
    def test_doi_failure_fallback_to_title(self, mock_sch_class):
        """Test fallback to title search when DOI lookup fails."""
        mock_sch = Mock()
        # DOI lookup fails
        mock_sch.get_paper.side_effect = Exception("DOI not found")
        # Title search succeeds
        mock_paper = {
            'title': 'Test Paper',
            'abstract': 'Test abstract',
            'year': 2023,
            'authors': [{'name': 'Test Author'}],
            'citationCount': 5,
            'citations': [],
            'references': [],
            'url': 'http://test.com',
            'externalIds': None
        }
        mock_sch.search_paper.return_value = [mock_paper]
        mock_sch_class.return_value = mock_sch
        
        result = fetch_semantic_scholar_data(
            doi="invalid:doi",
            title="Test Paper"
        )
        
        assert result is not None
        assert result['title'] == 'Test Paper'
    
    @patch('backend.external_api_utils.SemanticScholar')
    def test_title_search_with_author_matching(self, mock_sch_class):
        """Test title search with author matching."""
        mock_sch = Mock()
        mock_papers = [
            {
                'title': 'Wrong Paper',
                'abstract': '',
                'year': 2022,
                'authors': [{'name': 'Wrong Author'}],
                'citationCount': 0,
                'citations': [],
                'references': [],
                'url': 'http://wrong.com',
                'externalIds': None
            },
            {
                'title': 'Correct Paper',
                'abstract': 'Correct abstract',
                'year': 2023,
                'authors': [{'name': 'Test Author'}],
                'citationCount': 10,
                'citations': [],
                'references': [],
                'url': 'http://correct.com',
                'externalIds': None
            }
        ]
        mock_sch.search_paper.return_value = mock_papers
        mock_sch_class.return_value = mock_sch
        
        result = fetch_semantic_scholar_data(
            title="Test Paper",
            authors="Test Author"
        )
        
        assert result is not None
        assert result['title'] == 'Correct Paper'
    
    @patch('backend.external_api_utils.SemanticScholar')
    def test_not_found_returns_none(self, mock_sch_class):
        """Test that paper not found returns None."""
        mock_sch = Mock()
        mock_sch.get_paper.side_effect = Exception("Not found")
        mock_sch.search_paper.return_value = []
        mock_sch_class.return_value = mock_sch
        
        result = fetch_semantic_scholar_data(
            doi="10.9999/nonexistent",
            title="Nonexistent Paper"
        )
        
        assert result is None
    
    @patch('backend.external_api_utils.SemanticScholar')
    def test_limits_citations_and_references(self, mock_sch_class):
        """Test that citations and references are limited to 50."""
        mock_sch = Mock()
        mock_paper = {
            'title': 'Popular Paper',
            'abstract': '',
            'year': 2020,
            'authors': [],
            'citationCount': 200,
            'citations': [{'id': i} for i in range(100)],  # 100 citations
            'references': [{'id': i} for i in range(100)],  # 100 references
            'url': 'http://test.com',
            'externalIds': None
        }
        mock_sch.get_paper.return_value = mock_paper
        mock_sch_class.return_value = mock_sch
        
        result = fetch_semantic_scholar_data(doi="10.1234/popular")
        
        assert result is not None
        assert len(result['citations']) == 50
        assert len(result['references']) == 50


class TestAuthorMatching:
    """Tests for author matching helper function."""
    
    def test_match_by_single_author_name(self):
        """Test matching by single author name."""
        results = [
            {'authors': [{'name': 'Wrong Person'}]},
            {'authors': [{'name': 'John Smith'}]},
        ]
        
        matched = _match_paper_by_author(results, "John Smith")
        
        assert matched == results[1]
    
    def test_match_by_partial_author_name(self):
        """Test matching by partial author name."""
        results = [
            {'authors': [{'name': 'Jane Doe'}]},
            {'authors': [{'name': 'John Smith'}]},
        ]
        
        matched = _match_paper_by_author(results, "Smith")
        
        assert matched == results[1]
    
    def test_no_match_returns_first_result(self):
        """Test that no match returns first result."""
        results = [
            {'authors': [{'name': 'Author One'}]},
            {'authors': [{'name': 'Author Two'}]},
        ]
        
        matched = _match_paper_by_author(results, "Nonexistent Author")
        
        assert matched == results[0]
    
    def test_empty_results_returns_none(self):
        """Test that empty results returns None."""
        matched = _match_paper_by_author([], "Test Author")
        assert matched is None


# Integration test markers for real API calls
@pytest.mark.integration
@pytest.mark.skip(reason="Requires real API calls and rate limiting")
class TestRealAPICalls:
    """Integration tests with real API calls (run manually)."""
    
    def test_real_semantic_scholar_doi_lookup(self):
        """Test real DOI lookup (requires internet)."""
        # Example: Nature paper
        result = fetch_semantic_scholar_data(doi="10.1038/nature12373")
        
        assert result is not None
        assert 'abstract' in result
        assert len(result.get('authors', [])) > 0
    
    def test_real_semantic_scholar_title_search(self):
        """Test real title search (requires internet)."""
        result = fetch_semantic_scholar_data(
            title="Attention Is All You Need"
        )
        
        assert result is not None
        assert 'Transformer' in result.get('abstract', '')
        assert result.get('citation_count', 0) > 1000  # Well-cited paper
