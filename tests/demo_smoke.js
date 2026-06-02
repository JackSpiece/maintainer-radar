const assert = require("node:assert/strict");
const demo = require("../docs/assets/demo.js");

assert.equal(demo.normalizeRepository("python/cpython"), "python/cpython");
assert.equal(demo.normalizeRepository("https://github.com/python/cpython/pulls"), "python/cpython");
assert.equal(demo.normalizeRepository("github.com/vercel/next.js/pull/123"), "vercel/next.js");
assert.equal(demo.normalizeRepository("not a repo"), "");
assert.equal(demo.repositoryFromSearch("?repo=python/cpython"), "python/cpython");
assert.equal(
  demo.repositoryFromSearch("?repo=https%3A%2F%2Fgithub.com%2Fpython%2Fcpython%2Fpulls"),
  "python/cpython"
);
assert.equal(demo.repositoryFromSearch("?q=python/cpython"), "");
assert.equal(demo.groupByActionFromSearch("?repo=python/cpython&group=action"), true);
assert.equal(demo.groupByActionFromSearch("?repo=python/cpython&group-by=action"), true);
assert.equal(demo.groupByActionFromSearch("?repo=python/cpython"), false);
assert.equal(
  demo.shareUrlForRepository("https://jackspiece.github.io/maintainer-radar/?x=1", "python/cpython"),
  "https://jackspiece.github.io/maintainer-radar/?x=1&repo=python%2Fcpython"
);
assert.equal(
  demo.shareUrlForRepository("https://jackspiece.github.io/maintainer-radar/?x=1", "python/cpython", {
    groupByAction: true,
  }),
  "https://jackspiece.github.io/maintainer-radar/?x=1&repo=python%2Fcpython&group=action"
);
assert.equal(
  demo.shareUrlForRepository(
    "https://jackspiece.github.io/maintainer-radar/?group=action",
    "python/cpython"
  ),
  "https://jackspiece.github.io/maintainer-radar/?repo=python%2Fcpython"
);
assert.equal(demo.shareUrlForRepository("https://example.test/", "not a repo"), "");
assert.equal(
  demo.renderBadgeMarkdown(
    "python/cpython",
    "https://jackspiece.github.io/maintainer-radar/?repo=python%2Fcpython&group=action"
  ),
  [
    "[![Maintainer Radar PR triage]",
    "(https://img.shields.io/badge/Maintainer%20Radar-PR%20triage-1d4ed8)]",
    "(https://jackspiece.github.io/maintainer-radar/?repo=python%2Fcpython&group=action)",
  ].join("")
);
assert.equal(demo.renderBadgeMarkdown("not a repo", "https://example.test/"), "");
assert.equal(demo.renderBadgeMarkdown("python/cpython", ""), "");
assert.equal(
  demo.renderCliCommand("python/cpython"),
  "maintainer-radar repo python/cpython --hydrate --sort action"
);
assert.equal(
  demo.renderCliCommand("python/cpython", { groupByAction: true }),
  "maintainer-radar repo python/cpython --hydrate --sort action --group-by action"
);
assert.equal(demo.renderCliCommand("not a repo"), "");

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
  {
    now: new Date("2026-06-01T00:00:00Z"),
    checkRuns: [
      { status: "COMPLETED", conclusion: "SUCCESS" },
      { status: "COMPLETED", conclusion: "SUCCESS" },
    ],
  }
);

assert.equal(ready.action, "review now");
assert.equal(ready.reviewability, 100);
assert.equal(ready.nextStep, "Review now while the PR appears small, active, and low risk.");
assert.deepEqual(ready.flags, []);
assert.ok(ready.signals.includes("CI passed"));
assert.ok(ready.signals.includes("test plan present"));
assert.ok(ready.signals.includes("tests changed"));
assert.ok(demo.formatImpact(ready.scoreBreakdown).includes("CI passed (-8 risk)"));

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
  {
    now: new Date("2026-06-01T00:00:00Z"),
    checkRuns: [{ status: "COMPLETED", conclusion: "FAILURE" }],
  }
);

assert.equal(risky.action, "ask for CI fix");
assert.equal(risky.reviewability, 7);
assert.equal(risky.nextStep, "Ask the author to get failing checks green before deeper review.");
assert.ok(risky.flags.includes("very large diff"));
assert.ok(risky.flags.includes("CI failing"));
assert.ok(risky.flags.includes("stale 22 days"));
assert.ok(risky.flags.includes("no test plan found"));
assert.ok(risky.flags.includes("code changed without tests"));
assert.ok(demo.formatImpact(risky.scoreBreakdown).includes("very large diff (+30 risk)"));

const labelBlocked = demo.analyzePullRequest(
  {
    number: 44,
    title: "Add parser fast path",
    html_url: "https://example.test/pull/44",
    body: "Test plan: unit tests.",
    updated_at: "2026-06-01T00:00:00Z",
    additions: 60,
    deletions: 12,
    changed_files: 2,
    draft: false,
    labels: [{ name: "waiting-on-author" }],
  },
  [{ filename: "src/parser/fast_path.py" }, { filename: "tests/test_fast_path.py" }],
  {
    now: new Date("2026-06-01T00:00:00Z"),
    checkRuns: [{ status: "COMPLETED", conclusion: "SUCCESS" }],
  }
);

assert.equal(labelBlocked.action, "needs author follow-up");
assert.equal(
  labelBlocked.nextStep,
  "Ask the author to respond to unresolved maintainer feedback."
);
assert.ok(labelBlocked.flags.includes("maintainer blocking label"));
assert.equal(demo.hasBlockingLabel({ labels: ["documentation"] }), false);

const pending = demo.summarizeCheckRuns([{ status: "IN_PROGRESS", conclusion: null }]);
assert.deepEqual(pending, { passed: 0, failed: 0, pending: 1, skipped: 0, total: 1 });

const markdown = demo.renderMarkdownReport(
  [ready, risky],
  "example/project",
  "https://jackspiece.github.io/maintainer-radar/?repo=example%2Fproject"
);
assert.ok(markdown.includes("## Maintainer Radar Preview: example/project"));
assert.ok(markdown.includes("- PRs scanned: 2"));
assert.ok(markdown.includes("| PR | Action | Next Step | Score | Risk Impact | Signals |"));
assert.ok(markdown.includes("[#42 Fix parser cache race](https://example.test/pull/42)"));
assert.ok(markdown.includes("Review now while the PR appears small, active, and low risk."));
assert.ok(markdown.includes("very large diff (+30 risk)"));
assert.ok(markdown.includes("Generated by Maintainer Radar"));

const groupedMarkdown = demo.renderMarkdownReport(
  [ready, risky],
  "example/project",
  "",
  { groupByAction: true }
);
assert.ok(groupedMarkdown.includes("### review now (1 PR)"));
assert.ok(groupedMarkdown.includes("### ask for CI fix (1 PR)"));
assert.deepEqual(
  demo.groupItemsByAction([ready, risky]).map((group) => group.action),
  ["review now", "ask for CI fix"]
);

const workflow = demo.renderActionWorkflow();
assert.ok(workflow.includes("name: Maintainer Radar"));
assert.ok(workflow.includes("uses: JackSpiece/maintainer-radar@v0.16.14"));
assert.ok(workflow.includes("pull-requests: read"));
assert.ok(workflow.includes("group-by: action"));
assert.ok(workflow.includes("path: ${{ steps.radar.outputs.report-path }}"));

console.log("browser demo smoke checks passed");
