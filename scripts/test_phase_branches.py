"""Regression checks for current-source isolation, not historical reconstruction."""

import ast
import unittest

from prepare_phase_branches import API, WEB, dependencies, owner, scoped_main


class PhaseSelectionTests(unittest.TestCase):
    def test_feature_ownership_precedes_general_ui_rules(self):
        self.assertEqual(owner(WEB + "components/infrastructure-plan-workspace.tsx"), 11)
        self.assertEqual(owner(WEB + "components/streaming-workspace.tsx"), 10)
        self.assertEqual(owner(WEB + "components/agent-memory-workspace.tsx"), 9)
        self.assertEqual(owner("labs/python/python-mastery/run.py"), 2)

    def test_main_keeps_only_selected_optional_router_and_core(self):
        raw = ("from atlas_api.dataset_routes import router as dataset_router\n"
               "from atlas_api.deployment_routes import router as deployment_router\n"
               "app.include_router(dataset_router)\napp.include_router(deployment_router)\n"
               "# Owned security comment must survive extraction.\ncore = 1\n").encode()
        result = scoped_main(raw, 11).decode()
        self.assertNotIn("dataset_router", result)
        self.assertIn("deployment_router", result)
        self.assertIn("Owned security comment", result)
        ast.parse(result)

    def test_local_imports_include_python_and_typescript_shared_dependencies(self):
        files = {API + "atlas_api/config.py": ("100644", "fixture"),
                 WEB + "lib/utils.ts": ("100644", "fixture"),
                 WEB + "components/ui/card.tsx": ("100644", "fixture")}
        self.assertEqual(dependencies(API + "atlas_api/auth.py",
                         b"from .config import Settings", files),
                         {API + "atlas_api/config.py"})
        self.assertEqual(dependencies(WEB + "components/workspace.tsx",
                         b'import { cn } from "@/lib/utils"; import { Card } from "./ui/card";',
                         files), {WEB + "lib/utils.ts", WEB + "components/ui/card.tsx"})

    def test_missing_frontend_dependency_fails_instead_of_publishing_broken_scope(self):
        with self.assertRaises(ValueError):
            dependencies(WEB + "components/workspace.tsx", b'import "@/lib/missing";', {})

    def test_next_generated_route_types_are_not_uploaded_as_source(self):
        self.assertEqual(dependencies("apps/web/next-env.d.ts",
                         b'import "./.next/types/routes.d.ts";', {}), set())

    def test_nodenext_javascript_specifier_resolves_typescript_source(self):
        files = {"apps/api-node/src/protocols.ts": ("100644", "fixture")}
        self.assertEqual(dependencies("apps/api-node/src/server.ts",
                         b'import { app } from "./protocols.js";', files), set(files))


if __name__ == "__main__":
    unittest.main()
