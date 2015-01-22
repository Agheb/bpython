import os
import tempfile
import textwrap

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from bpython import config

TEST_THEME_PATH = os.path.join(os.path.dirname(__file__), "test.theme")

class TestConfig(unittest.TestCase):
    def load_temp_config(self, content, struct=None):
        """Write config to a temporary file and load it."""

        if struct is None:
            struct = config.Struct()

        with tempfile.NamedTemporaryFile() as f:
            f.write(content.encode('utf8'))
            f.flush()

            config.loadini(struct, f.name)

        return struct

    def test_load_theme(self):
        struct = config.Struct()
        struct.color_scheme = dict()
        config.load_theme(struct, TEST_THEME_PATH, struct.color_scheme, dict())
        expected = {"keyword": "y"}
        self.assertEquals(struct.color_scheme, expected)

        defaults = {"name": "c"}
        expected.update(defaults)
        config.load_theme(struct, TEST_THEME_PATH, struct.color_scheme, defaults)
        self.assertEquals(struct.color_scheme, expected)

    def test_keybindings_default_contains_no_duplicates(self):
        struct = self.load_temp_config("")

        keys = (attr for attr in dir(struct) if attr.endswith('_key'))
        mapped_keys = [getattr(struct, key) for key in keys if
                       getattr(struct, key)]

        mapped_keys_set = set(mapped_keys)
        self.assertEqual(len(mapped_keys), len(mapped_keys_set))

    def test_keybindings_use_default(self):
        struct = self.load_temp_config(textwrap.dedent("""
            [keyboard]
            help = F1
            """))

        self.assertEqual(struct.help_key, 'F1')

    def test_keybindings_use_other_default(self):
        struct = self.load_temp_config(textwrap.dedent("""
            [keyboard]
            help = C-h
            """))

        self.assertEqual(struct.help_key, 'C-h')
        self.assertEqual(struct.backspace_key, '')

    def test_keybindings_use_other_default_issue_447(self):
        struct = self.load_temp_config(textwrap.dedent("""
            [keyboard]
            help = F2
            show_source = F9
            """))

        self.assertEqual(struct.help_key, 'F2')
        self.assertEqual(struct.show_source_key, 'F9')

    def test_keybindings_unset(self):
        struct = self.load_temp_config(textwrap.dedent("""
            [keyboard]
            help =
            """))

        self.assertFalse(struct.help_key)

    def test_keybindings_unused(self):
        struct = self.load_temp_config(textwrap.dedent("""
            [keyboard]
            help = F4
            """))

        self.assertEqual(struct.help_key, 'F4')

