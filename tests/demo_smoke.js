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
assert.equal(demo.hasBlockingLabel({ labels: [{ name: "blocked-upstream" }] }), true);
assert.equal(demo.hasBlockingLabel({ labels: [{ name: "waiting-for-dependency" }] }), true);
assert.equal(demo.isMaintainerBlocked(labelBlocked), true);
assert.equal(demo.isMaintainerBlocked(ready), false);
assert.deepEqual(demo.summarizeItems([ready, risky, labelBlocked]), {
  total: 3,
  reviewNow: 1,
  followUp: 2,
  maintainerBlocked: 1,
  average: 66,
});

const pending = demo.summarizeCheckRuns([{ status: "IN_PROGRESS", conclusion: null }]);
assert.deepEqual(pending, { passed: 0, failed: 0, pending: 1, skipped: 0, total: 1 });

const waitForCi = demo.analyzePullRequest(
  {
    number: 45,
    title: "Refresh generated docs",
    html_url: "https://example.test/pull/45",
    body: "Validation: generated docs preview.",
    updated_at: "2026-06-01T00:00:00Z",
    additions: 12,
    deletions: 4,
    changed_files: 1,
    draft: false,
  },
  [{ filename: "docs/generated.md" }],
  {
    now: new Date("2026-06-01T00:00:00Z"),
    checkRuns: [{ status: "IN_PROGRESS", conclusion: null }],
  }
);

assert.equal(demo.estimateReviewMinutes(ready), 12);
assert.equal(demo.estimateReviewMinutes(risky), 5);
assert.equal(demo.estimateReviewMinutes(waitForCi), 0);
const plan = demo.buildReviewPlan([ready, risky, waitForCi], 15);
assert.equal(plan.plannedMinutes, 12);
assert.deepEqual(plan.planned.map((entry) => entry.item.number), [42]);
assert.deepEqual(plan.deferred.map((entry) => entry.item.number), [43]);
assert.deepEqual(plan.waiting.map((entry) => entry.item.number), [45]);
const planMarkdown = demo.renderReviewPlanMarkdown(
  [ready, risky, waitForCi],
  "example/project",
  30,
  "https://jackspiece.github.io/maintainer-radar/?repo=example%2Fproject"
);
assert.ok(planMarkdown.includes("## Maintainer Radar Review Plan: example/project"));
assert.ok(planMarkdown.includes("- Time budget: 30 minutes"));
assert.ok(planMarkdown.includes("| Order | PR | Action | Est. | Next Step | Why |"));
assert.ok(planMarkdown.includes("[#42 Fix parser cache race](https://example.test/pull/42)"));
assert.ok(planMarkdown.includes("12m"));
assert.ok(planMarkdown.includes("### Watch Only"));
assert.ok(planMarkdown.includes("#45 Refresh generated docs"));

const markdown = demo.renderMarkdownReport(
  [ready, risky],
  "example/project",
  "https://jackspiece.github.io/maintainer-radar/?repo=example%2Fproject"
);
assert.ok(markdown.includes("## Maintainer Radar Preview: example/project"));
assert.ok(markdown.includes("- PRs scanned: 2"));
assert.ok(markdown.includes("- Maintainer blocked: 0"));
assert.ok(markdown.includes("| PR | Action | Next Step | Score | Risk Impact | Signals |"));
assert.ok(markdown.includes("[#42 Fix parser cache race](https://example.test/pull/42)"));
assert.ok(markdown.includes("Review now while the PR appears small, active, and low risk."));
assert.ok(markdown.includes("very large diff (+30 risk)"));
assert.ok(markdown.includes("Generated by Maintainer Radar"));

const blockedMarkdown = demo.renderMarkdownReport(
  [ready, labelBlocked],
  "example/project",
  "https://jackspiece.github.io/maintainer-radar/?repo=example%2Fproject"
);
assert.ok(blockedMarkdown.includes("- Maintainer blocked: 1"));

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
assert.ok(workflow.includes("name: Maintainer Radar Review Plan"));
assert.ok(workflow.includes("uses: JackSpiece/maintainer-radar@v0.16.21"));
assert.ok(workflow.includes("pull-requests: read"));
assert.ok(workflow.includes('review-plan-minutes: "30"'));
assert.ok(workflow.includes("output: review-plan.md"));
assert.ok(workflow.includes("name: review-plan"));
assert.ok(workflow.includes("path: ${{ steps.radar.outputs.report-path }}"));
const fortyFiveMinuteWorkflow = demo.renderActionWorkflow({ budgetMinutes: 45 });
assert.ok(fortyFiveMinuteWorkflow.includes("Build 45 minute review plan"));
assert.ok(fortyFiveMinuteWorkflow.includes('review-plan-minutes: "45"'));

console.log("browser demo smoke checks passed");
