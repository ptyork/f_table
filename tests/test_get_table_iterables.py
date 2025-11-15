import unittest
from craftable import get_table


class TestIterableTypes(unittest.TestCase):
    def test_values_as_tuples(self):
        data = [("Alice", 30, "Engineer"), ("Bob", 25, "Designer"), ("Charlie", 35, "Manager")]
        self.assertIn("Alice", get_table(data))

    def test_generator_for_values(self):
        data = ((n, a) for n, a in [("Alice", 30), ("Bob", 25)])
        self.assertIn("Bob", get_table(data))

    def test_nested_generator_with_tuple_rows(self):
        def gen():
            for n, a in [("Alice", 30), ("Bob", 25)]:
                yield (n, a, a * 1000)
        out = get_table(gen(), header_row=("Name", "Age", "Salary"))
        self.assertIn("30000", out)

    def test_map_object_for_values(self):
        raw = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
        data = map(lambda x: list(x), raw)
        out = get_table(data)
        self.assertIn("Alice", out)
        self.assertIn("Bob", out)

    def test_filter_object_for_values(self):
        raw = [["Alice", 30], ["Bob", 25], ["Charlie", 35], ["Diana", 20]]
        data = filter(lambda r: r[1] >= 25, raw)
        out = get_table(data)
        self.assertIn("Alice", out)
        self.assertIn("Charlie", out)
        self.assertNotIn("Diana", out)

    def test_zip_object_for_values(self):
        names = ["Alice", "Bob", "Charlie"]
        ages = [30, 25, 35]
        data = zip(names, ages)
        out = get_table(data)
        self.assertIn("Alice", out)
        self.assertIn("30", out)

    def test_generator_function_for_values(self):
        def gen():
            yield ["Alice", 30]
            yield ["Bob", 25]
        out = get_table(gen())
        self.assertIn("Bob", out)
