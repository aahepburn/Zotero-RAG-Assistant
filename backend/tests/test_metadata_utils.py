"""
Unit tests for metadata utilities.
Tests functions from metadata_utils.py
"""

import pytest
from backend.metadata_utils import (
    build_metadata_where_clause,
    validate_where_clause,
    merge_where_clauses,
    format_filters_for_display,
)


class TestBuildMetadataWhereClause:
    """Test where clause construction."""
    
    def test_year_min_only(self):
        """Test year minimum filter."""
        where = build_metadata_where_clause(year_min=2020)
        
        assert where == {"year": {"$gte": 2020}}
    
    def test_year_max_only(self):
        """Test year maximum filter."""
        where = build_metadata_where_clause(year_max=2023)
        
        assert where == {"year": {"$lte": 2023}}
    
    def test_year_range(self):
        """Test year range filter."""
        where = build_metadata_where_clause(year_min=2018, year_max=2022)
        
        assert where == {
            "$and": [
                {"year": {"$gte": 2018}},
                {"year": {"$lte": 2022}}
            ]
        }
    
    def test_single_tag(self):
        """Test single tag filter."""
        where = build_metadata_where_clause(tags=["NLP"])
        
        assert where == {"tags": {"$contains": "NLP"}}
    
    def test_multiple_tags(self):
        """Test multiple tags filter (OR logic)."""
        where = build_metadata_where_clause(tags=["NLP", "ML", "CV"])
        
        assert where == {
            "$or": [
                {"tags": {"$contains": "NLP"}},
                {"tags": {"$contains": "ML"}},
                {"tags": {"$contains": "CV"}}
            ]
        }
    
    def test_single_collection(self):
        """Test single collection filter."""
        where = build_metadata_where_clause(collections=["Research"])
        
        assert where == {"collections": {"$contains": "Research"}}
    
    def test_multiple_collections(self):
        """Test multiple collections filter (OR logic)."""
        where = build_metadata_where_clause(collections=["Research", "Papers"])
        
        assert where == {
            "$or": [
                {"collections": {"$contains": "Research"}},
                {"collections": {"$contains": "Papers"}}
            ]
        }
    
    def test_combined_year_and_tags(self):
        """Test combined year and tags filter."""
        where = build_metadata_where_clause(
            year_min=2020,
            tags=["NLP", "ML"]
        )
        
        assert where == {
            "$and": [
                {"year": {"$gte": 2020}},
                {"$or": [
                    {"tags": {"$contains": "NLP"}},
                    {"tags": {"$contains": "ML"}}
                ]}
            ]
        }
    
    def test_combined_all_filters(self):
        """Test all filters combined."""
        where = build_metadata_where_clause(
            year_min=2018,
            year_max=2022,
            tags=["Transformers"],
            collections=["PhD Research"]
        )
        
        expected = {
            "$and": [
                {"year": {"$gte": 2018}},
                {"year": {"$lte": 2022}},
                {"tags": {"$contains": "Transformers"}},
                {"collections": {"$contains": "PhD Research"}}
            ]
        }
        
        assert where == expected
    
    def test_no_filters(self):
        """Test with no filters."""
        where = build_metadata_where_clause()
        
        assert where is None
    
    def test_empty_lists(self):
        """Test with empty lists."""
        where = build_metadata_where_clause(tags=[], collections=[])
        
        assert where is None


class TestValidateWhereClause:
    """Test where clause validation."""
    
    def test_validate_none(self):
        """Test validation of None."""
        assert validate_where_clause(None) == True
    
    def test_validate_simple_condition(self):
        """Test validation of simple condition."""
        where = {"year": {"$gte": 2020}}
        assert validate_where_clause(where) == True
    
    def test_validate_and_condition(self):
        """Test validation of AND condition."""
        where = {
            "$and": [
                {"year": {"$gte": 2020}},
                {"tags": {"$contains": "NLP"}}
            ]
        }
        assert validate_where_clause(where) == True
    
    def test_validate_or_condition(self):
        """Test validation of OR condition."""
        where = {
            "$or": [
                {"tags": {"$contains": "NLP"}},
                {"tags": {"$contains": "ML"}}
            ]
        }
        assert validate_where_clause(where) == True
    
    def test_validate_nested_conditions(self):
        """Test validation of nested conditions."""
        where = {
            "$and": [
                {"year": {"$gte": 2020}},
                {
                    "$or": [
                        {"tags": {"$contains": "NLP"}},
                        {"tags": {"$contains": "ML"}}
                    ]
                }
            ]
        }
        assert validate_where_clause(where) == True
    
    def test_validate_invalid_type(self):
        """Test validation of invalid type."""
        assert validate_where_clause("not a dict") == False
        assert validate_where_clause(123) == False
    
    def test_validate_invalid_logical_op(self):
        """Test validation of invalid logical operator value."""
        where = {"$and": "not a list"}
        assert validate_where_clause(where) == False
    
    def test_validate_all_operators(self):
        """Test validation with all comparison operators."""
        where = {
            "$and": [
                {"field1": {"$eq": 1}},
                {"field2": {"$ne": 2}},
                {"field3": {"$gt": 3}},
                {"field4": {"$gte": 4}},
                {"field5": {"$lt": 5}},
                {"field6": {"$lte": 6}},
                {"field7": {"$contains": "test"}},
                {"field8": {"$in": [1, 2, 3]}},
                {"field9": {"$nin": [4, 5, 6]}}
            ]
        }
        assert validate_where_clause(where) == True


class TestMergeWhereClauses:
    """Test where clause merging."""
    
    def test_merge_both_none(self):
        """Test merging two None clauses."""
        result = merge_where_clauses(None, None)
        assert result is None
    
    def test_merge_first_none(self):
        """Test merging with first clause None."""
        clause2 = {"year": {"$gte": 2020}}
        result = merge_where_clauses(None, clause2)
        assert result == clause2
    
    def test_merge_second_none(self):
        """Test merging with second clause None."""
        clause1 = {"year": {"$gte": 2020}}
        result = merge_where_clauses(clause1, None)
        assert result == clause1
    
    def test_merge_two_simple(self):
        """Test merging two simple clauses."""
        clause1 = {"year": {"$gte": 2020}}
        clause2 = {"tags": {"$contains": "NLP"}}
        result = merge_where_clauses(clause1, clause2)
        
        expected = {
            "$and": [
                {"year": {"$gte": 2020}},
                {"tags": {"$contains": "NLP"}}
            ]
        }
        assert result == expected
    
    def test_merge_complex_clauses(self):
        """Test merging complex clauses."""
        clause1 = {
            "$and": [
                {"year": {"$gte": 2018}},
                {"year": {"$lte": 2022}}
            ]
        }
        clause2 = {
            "$or": [
                {"tags": {"$contains": "NLP"}},
                {"tags": {"$contains": "ML"}}
            ]
        }
        result = merge_where_clauses(clause1, clause2)
        
        expected = {
            "$and": [clause1, clause2]
        }
        assert result == expected


class TestFormatFiltersForDisplay:
    """Test filter display formatting."""
    
    def test_format_year_range(self):
        """Test formatting year range."""
        display = format_filters_for_display(year_min=2018, year_max=2022)
        assert display == "Year: 2018-2022"
    
    def test_format_year_single(self):
        """Test formatting single year."""
        display = format_filters_for_display(year_min=2020, year_max=2020)
        assert display == "Year: 2020"
    
    def test_format_year_min_only(self):
        """Test formatting year minimum only."""
        display = format_filters_for_display(year_min=2020)
        assert display == "Year: 2020+"
    
    def test_format_year_max_only(self):
        """Test formatting year maximum only."""
        display = format_filters_for_display(year_max=2023)
        assert display == "Year: ≤2023"
    
    def test_format_tags(self):
        """Test formatting tags."""
        display = format_filters_for_display(tags=["NLP", "ML", "CV"])
        assert display == "Tags: NLP, ML, CV"
    
    def test_format_collections(self):
        """Test formatting collections."""
        display = format_filters_for_display(collections=["Research", "Papers"])
        assert display == "Collections: Research, Papers"
    
    def test_format_combined(self):
        """Test formatting combined filters."""
        display = format_filters_for_display(
            year_min=2018,
            year_max=2022,
            tags=["NLP"],
            collections=["Research"]
        )
        
        assert "Year: 2018-2022" in display
        assert "Tags: NLP" in display
        assert "Collections: Research" in display
        assert " | " in display  # Parts separated by pipe
    
    def test_format_no_filters(self):
        """Test formatting with no filters."""
        display = format_filters_for_display()
        assert display == "No filters"
    
    def test_format_empty_lists(self):
        """Test formatting with empty lists."""
        display = format_filters_for_display(tags=[], collections=[])
        assert display == "No filters"


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_where_clause_with_special_characters(self):
        """Test where clause with special characters in strings."""
        where = build_metadata_where_clause(
            tags=["C++", "C#", ".NET"],
            collections=["Papers (2020-2023)"]
        )
        
        # Should handle special characters
        assert where is not None
        assert validate_where_clause(where)
    
    def test_where_clause_with_unicode(self):
        """Test where clause with unicode characters."""
        where = build_metadata_where_clause(
            tags=["深度学习", "機械学習"]
        )
        
        assert where is not None
        assert validate_where_clause(where)
    
    def test_year_boundary_values(self):
        """Test year boundary values."""
        where = build_metadata_where_clause(year_min=1900, year_max=2100)
        
        assert where == {
            "$and": [
                {"year": {"$gte": 1900}},
                {"year": {"$lte": 2100}}
            ]
        }
    
    def test_single_item_lists(self):
        """Test single-item lists don't create unnecessary OR."""
        where = build_metadata_where_clause(tags=["NLP"])
        
        # Should be simple, not wrapped in $or
        assert where == {"tags": {"$contains": "NLP"}}
        assert "$or" not in where
    
    def test_large_tag_list(self):
        """Test handling of large tag list."""
        tags = [f"tag{i}" for i in range(100)]
        where = build_metadata_where_clause(tags=tags)
        
        assert where is not None
        assert "$or" in where
        assert len(where["$or"]) == 100
    
    def test_validation_deeply_nested(self):
        """Test validation of deeply nested conditions."""
        where = {
            "$and": [
                {
                    "$or": [
                        {
                            "$and": [
                                {"field1": {"$gte": 1}},
                                {"field2": {"$lte": 2}}
                            ]
                        },
                        {"field3": {"$eq": 3}}
                    ]
                },
                {"field4": {"$contains": "test"}}
            ]
        }
        assert validate_where_clause(where) == True


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_scenario_phd_research(self):
        """Scenario: PhD student researching NLP papers from last 5 years."""
        where = build_metadata_where_clause(
            year_min=2019,
            tags=["NLP", "Natural Language Processing", "Transformers"],
            collections=["PhD Research", "Literature Review"]
        )
        
        assert where is not None
        assert validate_where_clause(where)
        
        display = format_filters_for_display(
            year_min=2019,
            tags=["NLP", "Natural Language Processing", "Transformers"],
            collections=["PhD Research", "Literature Review"]
        )
        assert "2019+" in display
    
    def test_scenario_survey_paper(self):
        """Scenario: Writing survey paper on recent CV advances."""
        where = build_metadata_where_clause(
            year_min=2020,
            year_max=2024,
            tags=["Computer Vision", "Deep Learning"],
            collections=["Survey Papers"]
        )
        
        assert where is not None
        assert validate_where_clause(where)
    
    def test_scenario_historical_analysis(self):
        """Scenario: Analyzing historical papers before deep learning era."""
        where = build_metadata_where_clause(
            year_max=2012,
            tags=["Machine Learning", "Neural Networks"]
        )
        
        assert where is not None
        display = format_filters_for_display(
            year_max=2012,
            tags=["Machine Learning", "Neural Networks"]
        )
        assert "≤2012" in display
    
    def test_scenario_merge_user_and_auto_filters(self):
        """Scenario: Merge user-specified and auto-extracted filters."""
        # User manually set collections
        user_where = build_metadata_where_clause(
            collections=["Research Papers"]
        )
        
        # Auto-extracted from query
        auto_where = build_metadata_where_clause(
            year_min=2020,
            tags=["Transformers"]
        )
        
        # Merge both
        merged = merge_where_clauses(user_where, auto_where)
        
        assert merged is not None
        assert validate_where_clause(merged)
        assert "$and" in merged


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
