"""
Shared test fixtures and utilities for metadata filtering tests.
Place this file in backend/tests/ as conftest.py for pytest auto-discovery.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, List, Any


# ==================== ChromaDB Fixtures ====================

@pytest.fixture
def mock_chroma_empty():
    """Mock empty ChromaDB client."""
    mock = Mock()
    mock.collection = Mock()
    mock.collection.count.return_value = 0
    mock.collection.get.return_value = {
        'ids': [],
        'metadatas': [],
        'documents': []
    }
    return mock


@pytest.fixture
def mock_chroma_v1():
    """Mock ChromaDB with v1 metadata (string year)."""
    mock = Mock()
    mock.collection = Mock()
    mock.collection.count.return_value = 100
    mock.collection.get.return_value = {
        'ids': ['1:0', '2:0', '3:0'],
        'metadatas': [
            {
                'item_id': '1',
                'title': 'Paper 1',
                'year': '2020',  # String
                'authors': 'Smith et al.'
            },
            {
                'item_id': '2',
                'title': 'Paper 2',
                'year': '2021',  # String
                'authors': 'Jones et al.'
            },
            {
                'item_id': '3',
                'title': 'Paper 3',
                'year': '2019',  # String
                'authors': 'Brown et al.'
            }
        ],
        'documents': ['Doc 1', 'Doc 2', 'Doc 3']
    }
    return mock


@pytest.fixture
def mock_chroma_v2():
    """Mock ChromaDB with v2 metadata (int year + tags/collections)."""
    mock = Mock()
    mock.collection = Mock()
    mock.collection.count.return_value = 100
    mock.collection.get.return_value = {
        'ids': ['1:0', '2:0', '3:0'],
        'metadatas': [
            {
                'item_id': '1',
                'title': 'Paper 1',
                'year': 2020,  # Integer
                'authors': 'Smith et al.',
                'tags': 'NLP|Deep Learning',
                'collections': 'Research|PhD'
            },
            {
                'item_id': '2',
                'title': 'Paper 2',
                'year': 2021,  # Integer
                'authors': 'Jones et al.',
                'tags': 'Computer Vision|ML',
                'collections': 'Survey Papers'
            },
            {
                'item_id': '3',
                'title': 'Paper 3',
                'year': 2019,  # Integer
                'authors': 'Brown et al.',
                'tags': 'Reinforcement Learning',
                'collections': 'Research'
            }
        ],
        'documents': ['Doc 1', 'Doc 2', 'Doc 3']
    }
    return mock


@pytest.fixture
def mock_chroma_mixed():
    """Mock ChromaDB with mixed v1/v2 metadata."""
    mock = Mock()
    mock.collection = Mock()
    mock.collection.count.return_value = 100
    mock.collection.get.return_value = {
        'ids': ['1:0', '2:0', '3:0'],
        'metadatas': [
            {
                'item_id': '1',
                'year': '2020',  # v1 (string)
                'tags': 'NLP'
            },
            {
                'item_id': '2',
                'year': 2021,  # v2 (int)
                'tags': 'ML'
            },
            {
                'item_id': '3',
                'year': 2019,  # v2 (int)
                'tags': 'CV'
            }
        ],
        'documents': ['Doc 1', 'Doc 2', 'Doc 3']
    }
    return mock


@pytest.fixture
def mock_chroma_filterable():
    """Mock ChromaDB that responds to where clause queries."""
    mock = Mock()
    mock.collection = Mock()
    
    # Default query response
    def query_side_effect(*args, **kwargs):
        where = kwargs.get('where')
        all_items = [
            {
                'id': '1:0',
                'metadata': {'year': 2020, 'tags': 'NLP|ML', 'collections': 'Research'},
                'document': 'Document about NLP'
            },
            {
                'id': '2:0',
                'metadata': {'year': 2021, 'tags': 'Computer Vision', 'collections': 'Survey'},
                'document': 'Document about CV'
            },
            {
                'id': '3:0',
                'metadata': {'year': 2019, 'tags': 'NLP', 'collections': 'Research'},
                'document': 'Document about NLP'
            },
            {
                'id': '4:0',
                'metadata': {'year': 2022, 'tags': 'Robotics', 'collections': 'PhD'},
                'document': 'Document about robotics'
            }
        ]
        
        # Simple filter simulation
        if where:
            # This is a simplified filter - real ChromaDB is more complex
            filtered = all_items
            # You can add more sophisticated filtering here if needed
        else:
            filtered = all_items
        
        return {
            'ids': [[item['id'] for item in filtered]],
            'metadatas': [[item['metadata'] for item in filtered]],
            'documents': [[item['document'] for item in filtered]]
        }
    
    mock.collection.query.side_effect = query_side_effect
    mock.collection.count.return_value = 4
    
    return mock


# ==================== Zotero Fixtures ====================

@pytest.fixture
def mock_zotero_library():
    """Mock Zotero library with sample items."""
    mock = Mock()
    
    def mock_search(*args, **kwargs):
        return [
            {
                'key': 'ABC123',
                'data': {
                    'title': 'Attention Is All You Need',
                    'date': '2017-06-12',
                    'tags': [{'tag': 'NLP'}, {'tag': 'Transformers'}],
                    'collections': ['XYZ789']
                }
            },
            {
                'key': 'DEF456',
                'data': {
                    'title': 'BERT: Pre-training of Deep Bidirectional Transformers',
                    'date': '2018',
                    'tags': [{'tag': 'NLP'}, {'tag': 'BERT'}],
                    'collections': ['XYZ789']
                }
            },
            {
                'key': 'GHI789',
                'data': {
                    'title': 'ImageNet Classification with Deep CNNs',
                    'date': '2012-12',
                    'tags': [{'tag': 'Computer Vision'}, {'tag': 'CNN'}],
                    'collections': ['ABC123']
                }
            }
        ]
    
    mock.search_parent_items_with_pdfs.side_effect = mock_search
    return mock


@pytest.fixture
def mock_zotero_collection_map():
    """Mock collection ID to name mapping."""
    return {
        'XYZ789': 'NLP Research',
        'ABC123': 'Computer Vision',
        'DEF456': 'PhD Thesis'
    }


# ==================== LLM Provider Fixtures ====================

@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing extraction."""
    mock = Mock()
    
    def mock_chat(*args, **kwargs):
        # Return a generic response
        return {
            'response': '```json\n{"year_min": 2020, "year_max": null, "tags": ["NLP"], "collections": []}\n```',
            'history': []
        }
    
    mock.chat.side_effect = mock_chat
    return mock


@pytest.fixture
def mock_provider_manager():
    """Mock provider manager with LLM provider."""
    mock_manager = Mock()
    mock_provider = Mock()
    
    def mock_chat(*args, **kwargs):
        return {
            'response': '```json\n{"year_min": 2020, "tags": [], "collections": []}\n```',
            'history': []
        }
    
    mock_provider.chat.side_effect = mock_chat
    mock_manager.get_provider.return_value = mock_provider
    
    return mock_manager


# ==================== Test Data Generators ====================

def create_metadata_v1(item_id: str, year: str, title: str = "Test Paper") -> Dict[str, Any]:
    """Create v1 metadata (string year)."""
    return {
        'item_id': item_id,
        'title': title,
        'year': year,  # String
        'authors': 'Test Author'
    }


def create_metadata_v2(
    item_id: str,
    year: int,
    tags: List[str] = None,
    collections: List[str] = None,
    title: str = "Test Paper"
) -> Dict[str, Any]:
    """Create v2 metadata (int year + tags/collections)."""
    tags_str = '|'.join(tags) if tags else ''
    collections_str = '|'.join(collections) if collections else ''
    
    return {
        'item_id': item_id,
        'title': title,
        'year': year,  # Integer
        'authors': 'Test Author',
        'tags': tags_str,
        'collections': collections_str
    }


def create_zotero_item(
    key: str,
    title: str,
    date: str,
    tags: List[str] = None,
    collections: List[str] = None
) -> Dict[str, Any]:
    """Create a Zotero item dict."""
    tags = tags or []
    collections = collections or []
    
    return {
        'key': key,
        'data': {
            'title': title,
            'date': date,
            'tags': [{'tag': t} for t in tags],
            'collections': collections
        }
    }


# ==================== Assertion Helpers ====================

def assert_metadata_v1_format(metadata: Dict[str, Any]) -> None:
    """Assert metadata is in v1 format."""
    assert 'year' in metadata
    assert isinstance(metadata['year'], str)
    assert 'tags' not in metadata or metadata.get('tags') == ''
    assert 'collections' not in metadata or metadata.get('collections') == ''


def assert_metadata_v2_format(metadata: Dict[str, Any]) -> None:
    """Assert metadata is in v2 format."""
    assert 'year' in metadata
    assert isinstance(metadata['year'], int)
    # tags and collections are optional but should be strings if present
    if 'tags' in metadata:
        assert isinstance(metadata['tags'], str)
    if 'collections' in metadata:
        assert isinstance(metadata['collections'], str)


def assert_valid_where_clause(where: Dict[str, Any]) -> None:
    """Assert where clause is valid ChromaDB format."""
    if where is None:
        return  # None is valid (no filters)
    
    assert isinstance(where, dict)
    
    # Check for valid keys
    valid_keys = {'year', 'tags', 'collections', '$and', '$or'}
    for key in where.keys():
        assert key in valid_keys or key.startswith('$'), f"Invalid key: {key}"
    
    # Check operators
    if 'year' in where:
        assert isinstance(where['year'], dict)
        year_ops = where['year']
        valid_ops = {'$gte', '$lte', '$eq', '$gt', '$lt'}
        for op in year_ops.keys():
            assert op in valid_ops, f"Invalid year operator: {op}"


def assert_filters_extracted(filters: Dict[str, Any]) -> None:
    """Assert that extracted filters have expected structure."""
    required_keys = ['year_min', 'year_max', 'tags', 'collections', 'has_filters']
    for key in required_keys:
        assert key in filters, f"Missing key: {key}"
    
    # Type checks
    assert filters['year_min'] is None or isinstance(filters['year_min'], int)
    assert filters['year_max'] is None or isinstance(filters['year_max'], int)
    assert isinstance(filters['tags'], list)
    assert isinstance(filters['collections'], list)
    assert isinstance(filters['has_filters'], bool)


# ==================== Mock Factory Functions ====================

def create_mock_chroma_with_data(items: List[Dict[str, Any]]) -> Mock:
    """Create a mock ChromaDB client with custom data."""
    mock = Mock()
    mock.collection = Mock()
    mock.collection.count.return_value = len(items)
    
    ids = [item['id'] for item in items]
    metadatas = [item['metadata'] for item in items]
    documents = [item.get('document', 'Test document') for item in items]
    
    mock.collection.get.return_value = {
        'ids': ids,
        'metadatas': metadatas,
        'documents': documents
    }
    
    return mock


def create_mock_zotero_with_items(items: List[Dict[str, Any]]) -> Mock:
    """Create a mock Zotero library with custom items."""
    mock = Mock()
    mock.search_parent_items_with_pdfs.return_value = items
    return mock


# ==================== Sample Test Queries ====================

SAMPLE_QUERIES = {
    'simple_year': "Papers after 2020",
    'year_range': "Papers from 2018 to 2022",
    'with_tags': 'Papers tagged "NLP"',
    'with_collections': 'Papers in "Research" collection',
    'complex': 'Recent NLP papers in my PhD collection from the last 3 years',
    'no_filters': "What is attention mechanism?",
    'implicit_year': "Recent papers about transformers",
}


# ==================== Performance Helpers ====================

def time_function(func, *args, **kwargs):
    """Time a function execution."""
    import time
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed


# ==================== Debugging Helpers ====================

def print_where_clause(where: Dict[str, Any], indent: int = 0) -> None:
    """Pretty print a where clause for debugging."""
    if where is None:
        print(" " * indent + "None")
        return
    
    for key, value in where.items():
        if isinstance(value, dict):
            print(" " * indent + f"{key}:")
            print_where_clause(value, indent + 2)
        elif isinstance(value, list):
            print(" " * indent + f"{key}: [{len(value)} items]")
            for item in value:
                if isinstance(item, dict):
                    print_where_clause(item, indent + 2)
                else:
                    print(" " * (indent + 2) + str(item))
        else:
            print(" " * indent + f"{key}: {value}")


if __name__ == '__main__':
    print("This file contains shared fixtures for pytest.")
    print("Rename to conftest.py in the tests directory for auto-discovery.")
    print("\nAvailable fixtures:")
    print("  - mock_chroma_empty: Empty ChromaDB")
    print("  - mock_chroma_v1: v1 metadata (string year)")
    print("  - mock_chroma_v2: v2 metadata (int year + tags)")
    print("  - mock_chroma_mixed: Mixed v1/v2 metadata")
    print("  - mock_chroma_filterable: ChromaDB with query filtering")
    print("  - mock_zotero_library: Zotero library with sample items")
    print("  - mock_llm_provider: LLM provider for extraction")
    print("  - mock_provider_manager: Provider manager")
    print("\nHelper functions:")
    print("  - create_metadata_v1/v2: Generate test metadata")
    print("  - create_zotero_item: Generate test Zotero items")
    print("  - assert_metadata_v1/v2_format: Assert metadata format")
    print("  - assert_valid_where_clause: Validate where clause")
    print("  - create_mock_chroma_with_data: Custom ChromaDB mock")
