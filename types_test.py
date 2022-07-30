from project_types import *

import unittest


class TestMousePosition(unittest.TestCase):
    def test_accessors_return_expected(self):
        horizontal = 1
        vertical = 2
        position = MousePosition(horizontal, vertical)

        self.assertEqual(horizontal, position.get_horizontal())
        self.assertEqual(vertical, position.get_vertical())
    def test_one_two_string_as_expected(self):
        horizontal = 1
        vertical = 2
        position = MousePosition(horizontal, vertical)

        expected_string = f'({horizontal}, {vertical})'

        self.assertEqual(str(position), expected_string)
    def test_parses_string_properly(self):
        text = '(1, 2)'
        actual_position = MousePosition.from_text(text)

        expected_position = MousePosition(1, 2)

        self.assertEqual(expected_position.get_horizontal(), actual_position.get_horizontal())
        self.assertEqual(expected_position.get_vertical(), actual_position.get_vertical())
    def test_assign_add(self):
        original = MousePosition(10, 20)
        other = MousePosition(2, 3)

        original += other

        expected_horizontal = 10 + 2
        expected_vertical = 20 + 3

        self.assertEqual(expected_horizontal, original.get_horizontal())
        self.assertEqual(expected_vertical, original.get_vertical())
    def test_add(self):
        original = MousePosition(1, 2)
        other = MousePosition(14, 200)

        result = original + other

        expected_horizontal = 1 + 14
        expected_vertical = 2 + 200

        self.assertEqual(expected_horizontal, result.get_horizontal())
        self.assertEqual(expected_vertical, result.get_vertical())
    def test_assign_sub(self):
        original = MousePosition(10, 20)
        other = MousePosition(1, 2)

        original -= other

        expected_horizontal = 10 - 1
        expected_vertical = 20 - 2

        self.assertEqual(expected_horizontal, original.get_horizontal())
        self.assertEqual(expected_vertical, original.get_vertical())
    def test_sub(self):
        original = MousePosition(1, 2)
        other = MousePosition(239, 175)

        result = original - other

        expected_horizontal = 1 - 239
        expected_vertical = 2 - 175

        self.assertEqual(expected_horizontal, result.get_horizontal())
        self.assertEqual(expected_vertical, result.get_vertical())


if __name__ == '__main__':
    unittest.main()