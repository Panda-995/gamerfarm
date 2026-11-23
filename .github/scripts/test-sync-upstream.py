"""Exercise real Git merges without contacting or modifying GitHub."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("sync-upstream.sh").resolve()


class SyncUpstreamTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="gamerfarm-sync-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.upstream = self.root / "upstream"
        self.fork = self.root / "fork"
        self.origin = self.root / "origin.git"
        self.git(self.root, "init", "--initial-branch=main", str(self.upstream))
        self.configure(self.upstream)
        self.commit(self.upstream, {"README.md": "English introduction\n", "app.txt": "version one\n"})
        self.git(self.root, "clone", "--bare", str(self.upstream), str(self.origin))
        self.git(self.root, "clone", str(self.origin), str(self.fork))
        self.configure(self.fork)
        self.commit(self.fork, {"README.md": "中文项目介绍\n", "README.upstream.md": "English introduction\n"})
        self.git(self.fork, "push", "origin", "main")

    def git(self, cwd, *args, check=True):
        return subprocess.run(
            ["git", "-C", str(cwd), *args],
            check=check, text=True, encoding="utf-8", capture_output=True,
        )

    def configure(self, repo):
        self.git(repo, "config", "user.name", "Sync test")
        self.git(repo, "config", "user.email", "sync-test@example.invalid")
        self.git(repo, "config", "core.autocrlf", "false")

    def commit(self, repo, files):
        for name, text in files.items():
            (repo / name).write_text(text, encoding="utf-8")
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-m", "test change")

    def sync(self):
        # CI supplies the upstream and output paths explicitly; no real token is used.
        script = self.root / "sync-upstream.sh"
        shutil.copyfile(SCRIPT, script)
        output = self.root / "outputs"
        env = os.environ.copy()
        env.update(UPSTREAM_URL=self.upstream.as_posix(), GITHUB_OUTPUT=output.as_posix())
        env.pop("GITHUB_STEP_SUMMARY", None)
        result = subprocess.run(
            [shutil.which("bash"), script.as_posix()], cwd=self.fork, env=env,
            text=True, encoding="utf-8", capture_output=True,
        )
        values = dict(line.split("=", 1) for line in output.read_text().splitlines()) if output.exists() else {}
        return result, values

    def test_upstream_readme_conflict_keeps_chinese_and_updates_code(self):
        self.commit(self.upstream, {"README.md": "Updated English introduction\n", "app.txt": "version two\n"})
        result, values = self.sync()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.fork / "README.md").read_text(encoding="utf-8"), "中文项目介绍\n")
        self.assertEqual((self.fork / "README.upstream.md").read_text(), "Updated English introduction\n")
        self.assertEqual((self.fork / "app.txt").read_text(), "version two\n")
        self.assertEqual(values["changed"], "true")
        upstream_sha = self.git(self.upstream, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(values["upstream_revision"], upstream_sha)
        self.git(self.fork, "merge-base", "--is-ancestor", upstream_sha, "HEAD")
        self.assertEqual(self.git(self.origin, "rev-parse", "main").stdout.strip(), values["revision"])

    def test_no_upstream_changes_does_not_create_a_commit(self):
        before = self.git(self.fork, "rev-parse", "HEAD").stdout.strip()
        result, values = self.sync()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(values["changed"], "false")
        self.assertEqual(values["revision"], before)

    def test_application_conflict_aborts_without_pushing(self):
        self.commit(self.fork, {"app.txt": "fork customization\n"})
        self.git(self.fork, "push", "origin", "main")
        before = self.git(self.origin, "rev-parse", "main").stdout.strip()
        self.commit(self.upstream, {"app.txt": "incompatible upstream change\n"})
        result, _ = self.sync()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unresolved upstream conflict: app.txt", result.stderr)
        self.assertEqual(self.git(self.origin, "rev-parse", "main").stdout.strip(), before)
        self.assertEqual(self.git(self.fork, "status", "--porcelain").stdout, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
