import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "python" / "main.py"
MODULE_SPEC = importlib.util.spec_from_file_location("universal_code_analyzer_main", MODULE_PATH)
MODULE = importlib.util.module_from_spec(MODULE_SPEC)
assert MODULE_SPEC.loader is not None
MODULE_SPEC.loader.exec_module(MODULE)

UniversalCodeAnalyzer = MODULE.UniversalCodeAnalyzer
map_repository = MODULE.map_repository


class UniversalCodeAnalyzerTests(unittest.TestCase):
    def test_extracts_symbols_and_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "app.py"
            file_path.write_text(
                "\n".join(
                    [
                        "import os",
                        "from project.auth import AuthManager",
                        "",
                        "class Service:",
                        "    pass",
                        "",
                        "def process_data():",
                        "    return './local_helper.py'",
                    ]
                ),
                encoding="utf-8",
            )

            analyzer = UniversalCodeAnalyzer(str(file_path))
            results = analyzer.analyze()

            self.assertIn("os", results["libraries_used"])
            self.assertIn("project.auth", results["libraries_used"])
            self.assertEqual(results["classes_objects"][0]["name"], "Service")
            self.assertEqual(results["functions_methods"][0]["name"], "process_data")
            self.assertIn("./local_helper.py", results["linked_files"])

    def test_repository_map_includes_directories_and_skips_ignored_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "src" / "db").mkdir(parents=True)
            (project_root / "node_modules").mkdir()
            (project_root / ".git").mkdir()

            (project_root / "src" / "db" / "auth.js").write_text(
                "\n".join(
                    [
                        "const helper = require('./helper');",
                        "class AuthManager {}",
                        "function connect() {}",
                    ]
                ),
                encoding="utf-8",
            )
            (project_root / "src" / "db" / "helper.js").write_text(
                "export const helper = () => {};",
                encoding="utf-8",
            )
            (project_root / "node_modules" / "ignored.js").write_text(
                "function ignored() {}",
                encoding="utf-8",
            )

            output_file = project_root / "repo_map.json"
            repo_map = map_repository(str(project_root), str(output_file))

            self.assertTrue(output_file.exists())
            loaded_map = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(repo_map["root"], loaded_map["root"])
            self.assertIn("src/db", repo_map["directories"])
            self.assertIn("src/db/auth.js", repo_map["files"])
            self.assertNotIn("node_modules/ignored.js", repo_map["files"])
            self.assertEqual(repo_map["directories"]["src/db"]["file_count"], 2)


if __name__ == "__main__":
    unittest.main()