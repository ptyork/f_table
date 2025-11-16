"""Tests for from_dataframe adapter with pandas and polars DataFrames."""

import unittest


class TestFromDataframe(unittest.TestCase):
    """Test from_dataframe edge cases and error conditions."""

    def setUp(self):
        """Check if pandas/polars are available."""
        try:
            import pandas as pd

            self.pd = pd
            self.pandas_available = True
        except ImportError:
            self.pandas_available = False

        try:
            import polars as pl

            self.pl = pl
            self.polars_available = True
        except ImportError:
            self.polars_available = False

    def test_pandas_basic(self):
        """Test with pandas DataFrame."""
        if not self.pandas_available:
            self.skipTest("Pandas not available")

        from craftable.adapters import from_dataframe

        df = self.pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        rows, headers = from_dataframe(df)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])

    def test_pandas_column_filtering(self):
        """Test filtering columns."""
        if not self.pandas_available:
            self.skipTest("Pandas not available")

        from craftable.adapters import from_dataframe

        df = self.pd.DataFrame(
            {"name": ["Alice", "Bob"], "age": [30, 25], "city": ["LA", "NYC"]}
        )
        rows, headers = from_dataframe(df, columns=["name", "city"])

        self.assertEqual(headers, ["name", "city"])
        self.assertEqual(rows, [["Alice", "LA"], ["Bob", "NYC"]])

    def test_pandas_with_index(self):
        """Test including index."""
        if not self.pandas_available:
            self.skipTest("Pandas not available")

        from craftable.adapters import from_dataframe

        df = self.pd.DataFrame({"name": ["Alice", "Bob"]}, index=[10, 20])
        rows, headers = from_dataframe(df, include_index=True)

        self.assertEqual(headers, ["index", "name"])
        self.assertEqual(rows, [[10, "Alice"], [20, "Bob"]])

    def test_non_dataframe_type_raises(self):
        """Test that non-DataFrame types raise TypeError."""
        from craftable.adapters import from_dataframe

        # Should raise TypeError for non-DataFrame objects
        with self.assertRaises(TypeError):
            from_dataframe([["Alice", 30], ["Bob", 25]])

        with self.assertRaises(TypeError):
            from_dataframe({"name": "Alice", "age": 30})

    def test_pandas_include_index_with_named_index(self):
        """Test including a named index."""
        if not self.pandas_available:
            self.skipTest("Pandas not available")

        from craftable.adapters import from_dataframe

        df = self.pd.DataFrame(
            {"name": ["Alice", "Bob"]}, index=self.pd.Index([10, 20], name="user_id")
        )
        rows, headers = from_dataframe(df, include_index=True)

        # Named index should appear as column
        self.assertEqual(headers[0], "user_id")
        self.assertEqual(rows[0][0], 10)
        self.assertEqual(rows[1][0], 20)

    def test_pandas_column_filtering_nonexistent_column(self):
        """Test column filtering with columns that don't exist."""
        if not self.pandas_available:
            self.skipTest("Pandas not available")

        from craftable.adapters import from_dataframe

        df = self.pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})

        # Filter with mix of existing and non-existing columns
        rows, headers = from_dataframe(df, columns=["name", "nonexistent", "age"])

        # Should only include existing columns
        self.assertEqual(headers, ["name", "age"])

    def test_pandas_empty_dataframe(self):
        """Test with an empty DataFrame."""
        if not self.pandas_available:
            self.skipTest("Pandas not available")

        from craftable.adapters import from_dataframe

        df = self.pd.DataFrame({"name": [], "age": []})
        rows, headers = from_dataframe(df)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [])

    def test_polars_basic(self):
        """Test with Polars DataFrame."""
        if not self.polars_available:
            self.skipTest("Polars not available")

        from craftable.adapters import from_dataframe

        df = self.pl.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        rows, headers = from_dataframe(df)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(len(rows), 2)

    def test_polars_column_filtering(self):
        """Test Polars with column filtering."""
        if not self.polars_available:
            self.skipTest("Polars not available")

        from craftable.adapters import from_dataframe

        df = self.pl.DataFrame(
            {"name": ["Alice", "Bob"], "age": [30, 25], "city": ["LA", "NYC"]}
        )
        rows, headers = from_dataframe(df, columns=["name", "city"])

        # Should filter to requested columns
        self.assertEqual(headers, ["name", "city"])
        self.assertEqual(len(rows), 2)

    def test_unsupported_dataframe_subtype(self):
        """Test handling of unsupported DataFrame-like types."""
        from craftable.adapters import from_dataframe

        # Create a mock object with DataFrame in name but wrong interface
        class CustomDataFrame:
            pass

        obj = CustomDataFrame()

        # Should raise TypeError for unsupported type
        with self.assertRaises(TypeError) as ctx:
            from_dataframe(obj)

        self.assertIn("Unsupported DataFrame type", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
