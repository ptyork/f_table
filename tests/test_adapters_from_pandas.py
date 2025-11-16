"""Tests for from_numpy adapter with NumPy arrays (optional dependency)."""

import unittest


# Optional: NumPy tests (only run if numpy available)
class TestFromNumpy(unittest.TestCase):
    """Tests for from_numpy adapter."""

    def setUp(self):
        """Check if numpy is available."""
        try:
            import numpy as np

            self.np = np
            self.numpy_available = True
        except ImportError:
            self.numpy_available = False

    def test_1d_array(self):
        """Test with 1D array."""
        if not self.numpy_available:
            self.skipTest("NumPy not available")

        from craftable.adapters import from_numpy

        arr = self.np.array([1, 2, 3])
        rows, headers = from_numpy(arr)

        self.assertEqual(headers, ["value"])
        self.assertEqual(rows, [[1], [2], [3]])

    def test_2d_array(self):
        """Test with 2D array."""
        if not self.numpy_available:
            self.skipTest("NumPy not available")

        from craftable.adapters import from_numpy

        arr = self.np.array([[1, 2], [3, 4]])
        rows, headers = from_numpy(arr)

        self.assertEqual(headers, ["0", "1"])
        self.assertEqual(rows, [[1, 2], [3, 4]])

    def test_with_index(self):
        """Test including index column."""
        if not self.numpy_available:
            self.skipTest("NumPy not available")

        from craftable.adapters import from_numpy

        arr = self.np.array([10, 20])
        rows, headers = from_numpy(arr, include_index=True)

        self.assertEqual(headers, ["index", "value"])
        self.assertEqual(rows, [[0, 10], [1, 20]])

    def test_structured_array(self):
        """Test with structured array (has field names)."""
        if not self.numpy_available:
            self.skipTest("NumPy not available")

        from craftable.adapters import from_numpy

        dtype = [("name", "U10"), ("age", "i4")]
        arr = self.np.array([("Alice", 30), ("Bob", 25)], dtype=dtype)
        rows, headers = from_numpy(arr)

        self.assertEqual(headers, ["name", "age"])
        self.assertEqual(rows, [["Alice", 30], ["Bob", 25]])


if __name__ == "__main__":
    unittest.main()
