import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("requirements-check.py")
REQUIRED_IMPORTS = (
    "packaging.markers",
    "packaging.requirements",
    "packaging.tags",
    "packaging.utils",
    "packaging.version",
    "pip._internal.index.package_finder",
    "pip._internal.models.link",
    "pip._internal.models.target_python",
)


def load_requirements_check():
    spec = importlib.util.spec_from_file_location("requirements_check", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RequirementsCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for import_name in REQUIRED_IMPORTS:
            try:
                import_found = importlib.util.find_spec(import_name) is not None
            except ModuleNotFoundError:
                import_found = False
            if not import_found:
                raise unittest.SkipTest(f"missing optional dependency: {import_name}")
        cls.module = load_requirements_check()

    def test_parse_version_returns_release_tuple(self):
        self.assertEqual(self.module.parse_version("1.2.3"), (1, 2, 3))
        self.assertIsNone(self.module.parse_version("not-a-version"))

    def test_cleanup_debian_version_strips_distribution_suffix(self):
        self.assertEqual(
            self.module.cleanup_debian_version("2:1.4.5-1ubuntu2"),
            "1.4.5",
        )
        self.assertEqual(
            self.module.cleanup_debian_version("3.2.1+dfsg-4"),
            "3.2.1",
        )

    def test_strip_comment_keeps_requirement_text(self):
        self.assertEqual(
            self.module._strip_comment("requests==2.32.0  # pinned"),
            "requests==2.32.0",
        )
        self.assertEqual(self.module._strip_comment("   # only a comment"), "")


if __name__ == "__main__":
    unittest.main()
