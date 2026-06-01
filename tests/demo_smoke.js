const assert = require("node:assert/strict");
const demo = require("../docs/assets/demo.js");

assert.equal(demo.normalizeRepository("python/cpython"), "python/cpython");
assert.equal(demo.normalizeRepository("https://github.com/python/cpython/pulls"), "python/cpython");
assert.equal(demo.normalizeRepository("github.com/vercel/next.js/pull/123"), "vercel/next.js");
assert.equal(demo.normalizeRepository("not a repo"), "");

const ready = demo.analyzePullRequest(
  {
    number: 42,
    title: "Fix parser cache race",
    html_url: "https://example.test/pull/42",
    body: "Test plan: local repro and unit tests.",
    updated_at: "2026-06-01T00:00:00Z",
    additions: 42,
    deletions: 18,
    changed_files: 2,
    draft: false,
  },
  [{ filename: "src/parser/cache.py" }, { filename: "tests/test_parser_cache.py" }],
  new Date("2026-06-01T00:00:00Z")
);

assert.equal(ready.action, "review now");
assert.equal(ready.reviewability, 100);
assert.deepEqual(ready.flags, []);
assert.ok(ready.signals.includes("test plan present"));
assert.ok(ready.signals.includes("tests changed"));

const risky = demo.analyzePullRequest(
  {
    number: 43,
    title: "Add universal plugin system",
    html_url: "https://example.test/pull/43",
    body: "Implementation update.",
    updated_at: "2026-05-10T00:00:00Z",
    additions: 2200,
    deletions: 120,
    changed_files: 40,
    draft: false,
  },
  [{ filename: "src/plugin/runtime.ts" }],
  new Date("2026-06-01T00:00:00Z")
);

assert.equal(risky.action, "request smaller PR");
assert.equal(risky.reviewability, 37);
assert.ok(risky.flags.includes("very large diff"));
assert.ok(risky.flags.includes("stale 22 days"));
assert.ok(risky.flags.includes("no test plan found"));
assert.ok(risky.flags.includes("code changed without tests"));
assert.ok(demo.formatImpact(risky.scoreBreakdown).includes("very large diff (+30 risk)"));

console.log("browser demo smoke checks passed");
