from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from python.pipeline import build_index


class PipelineTests(unittest.TestCase):
    def test_build_index_supports_scope_batches_and_evidence_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "app" / "blog" / "[slug]").mkdir(parents=True)
            (root / "src").mkdir(parents=True)
            (root / "app" / "layout.tsx").write_text("export default function Layout() {}", encoding="utf-8")
            (root / "app" / "blog" / "[slug]" / "page.tsx").write_text("export default function Page() {}", encoding="utf-8")
            (root / "src" / "main.ts").write_text('import helper from "./missing";', encoding="utf-8")

            result = build_index(root, scope_paths=["app", "src"], batch_size=1)

            self.assertEqual("scoped-scan", result["scope"]["mode"])
            self.assertEqual(["app", "src"], result["scope"]["paths"])
            self.assertGreaterEqual(result["summary"]["batch_count"], 2)
            self.assertEqual(0, result["summary"]["skipped_file_count"])
            self.assertIn("batches", result)
            self.assertIn("skipped_files", result)
            self.assertNotIn("file_scores", result)
            self.assertNotIn("path_scores", result)
            self.assertNotIn("unresolved", result)
            self.assertNotIn("references", result)
            self.assertEqual(
                {"file", "language", "size"},
                set(result["files"][0].keys()),
            )
            self.assertTrue(all(isinstance(item, str) for item in result["skipped_files"]))

    def test_build_index_compact_mode_keeps_minimal_file_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir(parents=True)
            (root / "src" / "util.ts").write_text("export const util = true;", encoding="utf-8")
            (root / "src" / "main.ts").write_text(
                '\n'.join([
                    'import { util } from "./util";',
                    'import { util as utilAgain } from "./util";',
                ]),
                encoding="utf-8",
            )

            result = build_index(root, scope_paths=["src"], compact=True)

            self.assertTrue(result["scope"]["compact"])
        self.assertNotIn("references", result)
        self.assertEqual({"file", "language", "size"}, set(result["files"][0].keys()))

    def test_build_index_summary_omits_reference_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir(parents=True)
            (root / "src" / "util.ts").write_text("export const util = true;", encoding="utf-8")
            (root / "src" / "main.ts").write_text(
                '\n'.join([
                    'import { util } from "./util";',
                    'import { util as utilAgain } from "./util";',
                ]),
                encoding="utf-8",
            )

            result = build_index(root, scope_paths=["src"])

            self.assertNotIn("reference_count", result["summary"])


if __name__ == "__main__":
    unittest.main()