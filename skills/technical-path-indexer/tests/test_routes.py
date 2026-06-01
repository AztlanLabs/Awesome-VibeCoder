from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from python.repository import discover_files
from python.routes import extract_routes


class RouteTests(unittest.TestCase):
    def test_nextjs_support_files_are_skipped_and_route_files_are_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "app" / "blog" / "[slug]").mkdir(parents=True)
            (root / "pages" / "api").mkdir(parents=True)
            (root / "app" / "layout.tsx").write_text("export default function Layout() {}", encoding="utf-8")
            (root / "app" / "blog" / "[slug]" / "page.tsx").write_text("export default function Page() {}", encoding="utf-8")
            (root / "pages" / "_app.tsx").write_text("export default function App() {}", encoding="utf-8")
            (root / "pages" / "api" / "users.ts").write_text("export default function handler() {}", encoding="utf-8")

            files = discover_files(root)
            routes, unresolved, skipped = extract_routes(root, files)

            self.assertFalse(unresolved)
            indexed_routes = {(route.kind, route.route) for route in routes}
            self.assertIn(("filesystem-nextjs-app", "/blog/:slug"), indexed_routes)
            self.assertIn(("filesystem-nextjs-pages", "/api/users"), indexed_routes)

            skipped_lookup = {(item.path, item.reason, item.detail) for item in skipped}
            self.assertIn(("app/layout.tsx", "framework-support-file", "nextjs-app"), skipped_lookup)
            self.assertIn(("pages/_app.tsx", "framework-support-file", "nextjs-pages"), skipped_lookup)


if __name__ == "__main__":
    unittest.main()