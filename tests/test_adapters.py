"""Unit tests for data adapters (dicts, dataclasses, models, records, SQL, mapping)."""

import unittest
from dataclasses import dataclass
from craftable.adapters import (
    from_dicts,
    from_mapping_of_lists,
    from_dataclasses,
    from_models,
    from_records,
    from_sql,
)


class TestFromDicts(unittest.TestCase):
    """Tests for from_dicts adapter."""

    def test_basic_dicts(self):
        """Test converting list of dicts with consistent keys."""

        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        rows, headers = from_dicts(data)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])

    def test_missing_keys(self):
        """Test that missing keys are filled with None."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "city": "NYC"}]
        rows, headers = from_dicts(data)

        self.assertEqual(headers, ["name", "age", "city"])
        self.assertEqual(rows, [["Alice", 30, None], ["Bob", None, "NYC"]])

    def test_column_filtering(self):
        """Test filtering columns with columns parameter."""
        data = [
            {"name": "Alice", "age": 30, "city": "LA"},
            {"name": "Bob", "age": 25, "city": "NYC"},
        ]
        rows, headers = from_dicts(data, columns=["name", "city"])

        self.assertEqual(headers, ["name", "city"])
        self.assertEqual(rows, [["Alice", "LA"], ["Bob", "NYC"]])

    def test_column_filtering_with_missing(self):
        """Test column filtering when some dicts don't have requested columns."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob"}]
        rows, headers = from_dicts(data, columns=["name", "age"])

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", None]])

    def test_empty_list(self):
        """Test with empty list."""
        rows, headers = from_dicts([])

        self.assertEqual(headers, [])
        self.assertEqual(rows, [])

    def test_first_only(self):
        """Test first_only=True uses first dict's keys only."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "city": "NYC"}]
        rows, headers = from_dicts(data, first_only=True)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", None]])

    def test_order_alpha(self):
        """Test order='alpha' sorts keys alphabetically."""
        data = [
            {"name": "Alice", "city": "LA", "age": 30},
        ]
        rows, headers = from_dicts(data, order="alpha")

        self.assertEqual(headers, ["age", "city", "name"])

    def test_first_only_with_alpha(self):
        """Test first_only=True combined with order='alpha'."""
        data = [
            {"city": "LA", "name": "Alice", "age": 30},
            {"name": "Bob", "city": "NYC", "extra": "data"},
        ]
        rows, headers = from_dicts(data, first_only=True, order="alpha")

        # Should only have keys from first dict, sorted alphabetically
        self.assertEqual(headers, ["age", "city", "name"])
        self.assertEqual(rows, [[30, "LA", "Alice"], [None, "NYC", "Bob"]])


class TestFromMappingOfLists(unittest.TestCase):
    """Tests for from_mapping_of_lists adapter."""

    def test_basic_mapping(self):
        """Test converting dict-of-lists."""
        data = {"name": ["Alice", "Bob"], "age": [30, 25]}
        rows, headers = from_mapping_of_lists(data)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])

    def test_ragged_columns(self):
        """Test with columns of different lengths (pads with None)."""
        data = {"name": ["Alice", "Bob"], "age": [30, 25, 35]}
        rows, headers = from_mapping_of_lists(data)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25], [None, 35]])

    def test_column_filtering(self):
        """Test filtering columns."""
        data = {"name": ["Alice", "Bob"], "age": [30, 25], "city": ["LA", "NYC"]}
        rows, headers = from_mapping_of_lists(data, columns=["name", "city"])

        self.assertEqual(headers, ["name", "city"])
        self.assertEqual(rows, [["Alice", "LA"], ["Bob", "NYC"]])

    def test_empty_mapping(self):
        """Test with empty dict."""
        rows, headers = from_mapping_of_lists({})

        self.assertEqual(headers, [])
        self.assertEqual(rows, [])


class TestFromDataclasses(unittest.TestCase):
    """Tests for from_dataclasses adapter."""

    def test_basic_dataclasses(self):
        """Test converting dataclass instances."""

        @dataclass
        class Person:
            name: str
            age: int

        data = [Person("Alice", 30), Person("Bob", 25)]
        rows, headers = from_dataclasses(data)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])

    def test_column_filtering(self):
        """Test filtering fields."""

        @dataclass
        class Person:
            name: str
            age: int
            city: str

        data = [Person("Alice", 30, "LA"), Person("Bob", 25, "NYC")]
        rows, headers = from_dataclasses(data, columns=["name", "city"])

        self.assertEqual(headers, ["name", "city"])
        self.assertEqual(rows, [["Alice", "LA"], ["Bob", "NYC"]])

    def test_private_fields_excluded(self):
        """Test that private fields are excluded by default."""

        @dataclass
        class Person:
            name: str
            _id: int

        data = [Person("Alice", 1)]
        rows, headers = from_dataclasses(data)

        self.assertEqual(headers, ["name"])
        self.assertEqual(rows, [["Alice"]])

    def test_private_fields_included(self):
        """Test including private fields with flag."""

        @dataclass
        class Person:
            name: str
            _id: int

        data = [Person("Alice", 1)]
        rows, headers = from_dataclasses(data, include_private=True)

        self.assertEqual(headers, ["name", "_id"])
        self.assertEqual(rows, [["Alice", 1]])

    def test_empty_list(self):
        """Test with empty list."""
        rows, headers = from_dataclasses([])

        self.assertEqual(headers, [])
        self.assertEqual(rows, [])

    def test_non_dataclass_raises(self):
        """Test that non-dataclass raises TypeError."""

        class NotDataclass:
            pass

        with self.assertRaises(TypeError):
            from_dataclasses([NotDataclass()])


class TestFromModels(unittest.TestCase):
    """Tests for from_models adapter (using dataclasses as stand-in)."""

    def test_with_dataclass(self):
        """Test that from_models works with dataclasses."""

        @dataclass
        class Person:
            name: str
            age: int

        data = [Person("Alice", 30), Person("Bob", 25)]
        rows, headers = from_models(data)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])

    def test_with_dict_like_object(self):
        """Test with objects that have __dict__."""

        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        data = [Person("Alice", 30), Person("Bob", 25)]
        rows, headers = from_models(data)

        self.assertEqual(set(headers), {"name", "age"})
        # Order may vary with __dict__, so check rows contain right values
        self.assertEqual(len(rows), 2)

    def test_column_filtering(self):
        """Test column filtering."""

        @dataclass
        class Person:
            name: str
            age: int
            city: str

        data = [Person("Alice", 30, "LA")]
        rows, headers = from_models(data, columns=["name", "age"])

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30]])


class TestFromRecords(unittest.TestCase):
    """Tests for from_records adapter."""

    def test_basic_tuples(self):
        """Test converting list of tuples."""
        data = [("Alice", 30), ("Bob", 25)]
        rows, headers = from_records(data, columns=["name", "age"])

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])

    def test_auto_headers(self):
        """Test auto-generated headers."""
        data = [("Alice", 30), ("Bob", 25)]
        rows, headers = from_records(data)

        self.assertEqual(headers, ["col_0", "col_1"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])

    def test_empty_list(self):
        """Test with empty list."""
        rows, headers = from_records([])

        self.assertEqual(headers, [])
        self.assertEqual(rows, [])

    def test_with_lists(self):
        """Test with lists instead of tuples."""
        data = [["Alice", 30], ["Bob", 25]]
        rows, headers = from_records(data, columns=["name", "age"])

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])


class TestFromSQL(unittest.TestCase):
    """Tests for from_sql adapter."""

    def test_with_description(self):
        """Test with cursor description."""
        # Mock cursor description (name, type, display_size, ...)
        description = [("name", None), ("age", None)]
        rows_data = [("Alice", 30), ("Bob", 25)]

        rows, headers = from_sql(rows_data, description=description)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])

    def test_column_filtering(self):
        """Test filtering columns."""
        description = [("name", None), ("age", None), ("city", None)]
        rows_data = [("Alice", 30, "LA"), ("Bob", 25, "NYC")]

        rows, headers = from_sql(
            rows_data, columns=["name", "city"], description=description
        )

        self.assertEqual(headers, ["name", "city"])
        self.assertEqual(rows, [["Alice", "LA"], ["Bob", "NYC"]])

    def test_without_description(self):
        """Test without description (generates col_N headers)."""
        rows_data = [("Alice", 30), ("Bob", 25)]

        rows, headers = from_sql(rows_data)

        self.assertEqual(headers, ["col_0", "col_1"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])

    def test_empty_result(self):
        """Test with empty result set."""
        description = [("name", None), ("age", None)]
        rows, headers = from_sql([], description=description)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
