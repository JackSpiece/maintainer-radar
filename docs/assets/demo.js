(() => {
  const MAX_PULLS = 5;
  const ACTION_VERSION = "v0.17.1";
  const DEFAULT_SESSION_MINUTES = 60;
  const CODE_EXTENSIONS = [
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
  ];
  const TEST_HINTS = ["/test/", "/tests/", "__tests__", ".spec.", ".test.", "_test.", "test_"];
  const DOC_HINTS = [".md", ".mdx", "/docs/", "docs/", "readme", "changelog", "license"];
  const GENERATED_HINTS = [
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "cargo.lock",
    "go.sum",
    "dist/",
    "build/",
    "vendor/",
    "generated",
  ];
  const TEST_PLAN_RE = /\b(test plan|tests?|validation|verified|repro|manual test|ci)\b/i;
  const LABEL_BLOCKER_RE =
    /\b(blocked|blocker|do not merge|dnm|changes requested|needs? changes?|needs? tests?|missing tests?|waiting on author|needs? author|author action|author follow up|waiting on dependency|waiting for dependency|needs? dependency|dependency blocked|blocked upstream|blocked by upstream|upstream blocked)\b/i;
  const PLAN_ACTION_PRIORITY = {
    "review now": 0,
    "review with caution": 1,
    "needs author follow-up": 2,
    "ask for CI fix": 3,
    "request smaller PR": 4,
    "needs triage": 5,
    "wait for CI": 6,
    "wait for author": 7,
  };
  const FOLLOW_UP_ACTIONS = new Set([
    "ask for CI fix",
    "needs author follow-up",
    "request smaller PR",
    "wait for author",
  ]);

  function normalizeRepository(value) {
    const cleaned = String(value || "")
      .trim()
      .replace(/^https:\/\/github\.com\//i, "")
      .replace(/^github\.com\//i, "")
      .replace(/\/pulls?(\/.*)?$/i, "")
      .replace(/\/$/, "");
    const match = cleaned.match(/^([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)$/);
    return match ? `${match[1]}/${match[2]}` : "";
  }

  function repositoryFromSearch(search) {
    const params = new URLSearchParams(String(search || "").replace(/^\?/, ""));
    return normalizeRepository(params.get("repo"));
  }

  function groupByActionFromSearch(search) {
    const params = new URLSearchParams(String(search || "").replace(/^\?/, ""));
    const group = String(params.get("group") || params.get("group-by") || "").toLowerCase();
    return group === "action";
  }

  function normalizePlanMinutes(value, fallback = 30) {
    const number = Number(value);
    if (Number.isFinite(number) && number >= 1) {
      return Math.trunc(number);
    }
    const fallbackNumber = Number(fallback);
    if (Number.isFinite(fallbackNumber) && fallbackNumber >= 1) {
      return Math.trunc(fallbackNumber);
    }
    return 0;
  }

  function planMinutesFromSearch(search) {
    const params = new URLSearchParams(String(search || "").replace(/^\?/, ""));
    const value =
      params.get("plan") ?? params.get("plan-minutes") ?? params.get("review-plan-minutes");
    return value === null ? "" : normalizePlanMinutes(value, 30);
  }

  function shareUrlForRepository(baseUrl, value, options = {}) {
    const repository = normalizeRepository(value);
    if (!repository) {
      return "";
    }
    const url = new URL(
      String(baseUrl || "https://jackspiece.github.io/maintainer-radar/"),
      "https://jackspiece.github.io/maintainer-radar/"
    );
    url.searchParams.set("repo", repository);
    if (options.groupByAction) {
      url.searchParams.set("group", "action");
    } else {
      url.searchParams.delete("group");
      url.searchParams.delete("group-by");
    }
    if (Object.prototype.hasOwnProperty.call(options, "planMinutes")) {
      const planMinutes = normalizePlanMinutes(options.planMinutes, 0);
      if (planMinutes) {
        url.searchParams.set("plan", String(planMinutes));
      } else {
        url.searchParams.delete("plan");
      }
      url.searchParams.delete("plan-minutes");
      url.searchParams.delete("review-plan-minutes");
    }
    return url.toString();
  }

  function renderBadgeMarkdown(repository, shareUrl) {
    const normalized = normalizeRepository(repository);
    if (!normalized || !shareUrl) {
      return "";
    }
    const badgeUrl = "https://img.shields.io/badge/Maintainer%20Radar-PR%20triage-1d4ed8";
    return `[![Maintainer Radar PR triage](${badgeUrl})](${shareUrl})`;
  }

  function renderCliCommand(repository, options = {}) {
    const normalized = normalizeRepository(repository);
    if (!normalized) {
      return "";
    }
    const parts = ["maintainer-radar", "repo", normalized, "--hydrate", "--sort", "action"];
    if (options.groupByAction) {
      parts.push("--group-by", "action");
    }
    return parts.join(" ");
  }

  function summarizeFiles(files) {
    let codeFiles = 0;
    let docFiles = 0;
    let testFiles = 0;
    let generatedFiles = 0;

    for (const file of files || []) {
      const path = String(file.filename || file.path || "").toLowerCase();
      if (!path) {
        continue;
      }
      if (TEST_HINTS.some((hint) => path.includes(hint))) {
        testFiles += 1;
      }
      if (DOC_HINTS.some((hint) => path.endsWith(hint) || path.includes(hint))) {
        docFiles += 1;
      }
      if (GENERATED_HINTS.some((hint) => path.includes(hint))) {
        generatedFiles += 1;
      }
      if (CODE_EXTENSIONS.some((ext) => path.endsWith(ext))) {
        codeFiles += 1;
      }
    }

    return {
      codeFiles,
      docFiles,
      testFiles,
      generatedFiles,
      totalFiles: (files || []).length,
    };
  }

  function summarizeCheckRuns(checkRuns) {
    let passed = 0;
    let failed = 0;
    let pending = 0;
    let skipped = 0;

    for (const item of checkRuns || []) {
      const status = String(item.status || "").toUpperCase();
      const conclusion = String(item.conclusion || "").toUpperCase();
      if (status && status !== "COMPLETED") {
        pending += 1;
      } else if (conclusion === "SUCCESS" || conclusion === "NEUTRAL") {
        passed += 1;
      } else if (conclusion === "SKIPPED") {
        skipped += 1;
      } else if (["FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED"].includes(conclusion)) {
        failed += 1;
      } else if (conclusion) {
        pending += 1;
      }
    }

    return {
      passed,
      failed,
      pending,
      skipped,
      total: passed + failed + pending + skipped,
    };
  }

  function labelNames(pr) {
    const labels = pr && Array.isArray(pr.labels) ? pr.labels : [];
    return labels
      .map((label) => {
        if (typeof label === "string") {
          return label;
        }
        return String((label && label.name) || "");
      })
      .filter(Boolean);
  }

  function normalizeLabelName(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/[-_:/]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function hasBlockingLabel(pr) {
    return labelNames(pr).some((label) => LABEL_BLOCKER_RE.test(normalizeLabelName(label)));
  }

  function mergeStateStatus(pr) {
    return String(
      (pr && (pr.mergeStateStatus || pr.merge_state_status || pr.mergeable_state)) || ""
    )
      .toUpperCase()
      .replace(/[-\s]+/g, "_");
  }

  function mergeableState(pr) {
    const value = pr && pr.mergeable;
    if (typeof value === "boolean") {
      return value ? "MERGEABLE" : "CONFLICTING";
    }
    return String(value || "")
      .toUpperCase()
      .replace(/[-\s]+/g, "_");
  }

  function reviewRequestCount(pr) {
    let count = 0;
    for (const key of [
      "reviewRequests",
      "review_requests",
      "requested_reviewers",
      "requestedReviewers",
    ]) {
      const value = pr && pr[key];
      if (Array.isArray(value)) {
        count += value.length;
      } else if (value && typeof value === "object") {
        for (const nestedKey of ["nodes", "items"]) {
          if (Array.isArray(value[nestedKey])) {
            count += value[nestedKey].length;
            break;
          }
        }
      }
    }
    for (const key of ["requested_teams", "requestedTeams"]) {
      const value = pr && pr[key];
      if (Array.isArray(value)) {
        count += value.length;
      }
    }
    return count;
  }

  function daysSince(value, now = new Date()) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return null;
    }
    return Math.max(0, Math.floor((now.getTime() - date.getTime()) / 86400000));
  }

  function addImpact(scoreBreakdown, label, riskDelta, kind) {
    scoreBreakdown.push({ label, riskDelta, kind });
  }

  function clampRisk(value) {
    return Math.max(0, Math.min(100, value));
  }

  function resolveAnalysisOptions(value) {
    if (value instanceof Date) {
      return { now: value, checkRuns: null };
    }
    return {
      now: value && value.now ? value.now : new Date(),
      checkRuns: value && Array.isArray(value.checkRuns) ? value.checkRuns : null,
    };
  }

  function analyzePullRequest(pr, files, optionsValue = {}) {
    const options = resolveAnalysisOptions(optionsValue);
    const fileSummary = summarizeFiles(files);
    const checkSummary = summarizeCheckRuns(options.checkRuns);
    const additions = Number(pr.additions || 0);
    const deletions = Number(pr.deletions || 0);
    const changedFiles = Number(pr.changed_files || fileSummary.totalFiles || 0);
    const totalDiff = additions + deletions;
    const staleDays = daysSince(pr.updated_at, options.now);
    const hasBody = Object.prototype.hasOwnProperty.call(pr, "body");
    const hasTestPlan = TEST_PLAN_RE.test(String(pr.body || ""));
    const isDraft = Boolean(pr.draft);
    const hasCheckData = Array.isArray(options.checkRuns);
    const hasLabelBlocker = hasBlockingLabel(pr);
    const mergeState = mergeStateStatus(pr);
    const mergeable = mergeableState(pr);
    const reviewRequests = reviewRequestCount(pr);

    let risk = 0;
    const signals = [];
    const flags = [];
    const scoreBreakdown = [];

    if (isDraft) {
      risk += 25;
      flags.push("draft PR");
      addImpact(scoreBreakdown, "draft PR", 25, "flag");
    }

    if (totalDiff > 1500 || changedFiles > 25) {
      risk += 30;
      flags.push("very large diff");
      addImpact(scoreBreakdown, "very large diff", 30, "flag");
    } else if (totalDiff > 500 || changedFiles > 10) {
      risk += 15;
      flags.push("large diff");
      addImpact(scoreBreakdown, "large diff", 15, "flag");
    }

    if (hasCheckData) {
      if (checkSummary.total === 0) {
        risk += 8;
        flags.push("no visible checks");
        addImpact(scoreBreakdown, "no visible checks", 8, "flag");
      } else if (checkSummary.failed) {
        risk += 30;
        flags.push("CI failing");
        addImpact(scoreBreakdown, "CI failing", 30, "flag");
      } else if (checkSummary.pending) {
        risk += 10;
        flags.push("CI pending");
        addImpact(scoreBreakdown, "CI pending", 10, "flag");
      } else if (checkSummary.passed) {
        risk -= 8;
        signals.push("CI passed");
        addImpact(scoreBreakdown, "CI passed", -8, "signal");
      }
    }

    if (staleDays !== null) {
      if (staleDays >= 14) {
        const label = `stale ${staleDays} days`;
        risk += 15;
        flags.push(label);
        addImpact(scoreBreakdown, label, 15, "flag");
      } else if (staleDays >= 7) {
        const label = `quiet ${staleDays} days`;
        risk += 8;
        flags.push(label);
        addImpact(scoreBreakdown, label, 8, "flag");
      }
    }

    if (hasBody && !hasTestPlan && fileSummary.codeFiles) {
      risk += 8;
      flags.push("no test plan found");
      addImpact(scoreBreakdown, "no test plan found", 8, "flag");
    } else if (hasTestPlan) {
      signals.push("test plan present");
    }

    if (hasLabelBlocker) {
      risk += 18;
      flags.push("maintainer blocking label");
      addImpact(scoreBreakdown, "maintainer blocking label", 18, "flag");
    }

    if (mergeable === "CONFLICTING" || mergeState === "DIRTY") {
      risk += 20;
      flags.push("merge conflicts");
      addImpact(scoreBreakdown, "merge conflicts", 20, "flag");
    } else if (mergeState === "BEHIND") {
      risk += 8;
      flags.push("branch behind base");
      addImpact(scoreBreakdown, "branch behind base", 8, "flag");
    } else if (mergeState === "BLOCKED") {
      risk += 6;
      flags.push("merge blocked by repo rules");
      addImpact(scoreBreakdown, "merge blocked by repo rules", 6, "flag");
    } else if (mergeState === "UNSTABLE" && !checkSummary.total) {
      risk += 12;
      flags.push("merge checks unstable");
      addImpact(scoreBreakdown, "merge checks unstable", 12, "flag");
    } else if (mergeState === "CLEAN" || mergeable === "MERGEABLE") {
      signals.push("mergeable");
    }

    if (reviewRequests) {
      signals.push(reviewRequests === 1 ? "review requested" : `${reviewRequests} reviews requested`);
    }

    if (fileSummary.codeFiles && !fileSummary.testFiles) {
      risk += 10;
      flags.push("code changed without tests");
      addImpact(scoreBreakdown, "code changed without tests", 10, "flag");
    } else if (fileSummary.testFiles) {
      signals.push("tests changed");
    }

    if (fileSummary.generatedFiles) {
      const generatedRisk = Math.min(12, fileSummary.generatedFiles * 3);
      risk += generatedRisk;
      flags.push("generated or lockfile changes");
      addImpact(scoreBreakdown, "generated or lockfile changes", generatedRisk, "flag");
    }

    if (!fileSummary.codeFiles && fileSummary.docFiles) {
      risk -= 6;
      signals.push("docs-only shape");
      addImpact(scoreBreakdown, "docs-only shape", -6, "signal");
    }

    const rawRisk = risk;
    risk = clampRisk(risk);
    const reviewability = 100 - risk;
    const action = chooseAction({
      reviewability,
      isDraft,
      checks: checkSummary,
      hasCheckData,
      hasLabelBlocker,
      hasMergeConflict: flags.includes("merge conflicts"),
      isBranchBehind: flags.includes("branch behind base"),
      totalDiff,
      changedFiles,
    });

    return {
      number: pr.number,
      title: pr.title || "Untitled",
      url: pr.html_url || "",
      action,
      nextStep: recommendNextStep({ action, flags, signals }),
      reviewability,
      risk,
      rawRisk,
      signals,
      flags,
      scoreBreakdown,
      additions,
      deletions,
      changedFiles,
      staleDays,
      mergeStateStatus: mergeState,
      mergeable,
      reviewRequests,
    };
  }

  function chooseAction({
    reviewability,
    isDraft,
    checks,
    hasCheckData,
    hasLabelBlocker,
    hasMergeConflict,
    isBranchBehind,
    totalDiff,
    changedFiles,
  }) {
    if (isDraft) {
      return "wait for author";
    }
    if (hasCheckData && checks && checks.failed) {
      return "ask for CI fix";
    }
    if (hasCheckData && checks && checks.pending) {
      return "wait for CI";
    }
    if (hasMergeConflict || isBranchBehind) {
      return "needs author follow-up";
    }
    if (hasLabelBlocker) {
      return "needs author follow-up";
    }
    if (totalDiff > 1500 || changedFiles > 25) {
      return "request smaller PR";
    }
    if (reviewability >= 75) {
      return "review now";
    }
    if (reviewability >= 55) {
      return "review with caution";
    }
    return "needs triage";
  }

  function recommendNextStep({ action, flags = [], signals = [] }) {
    if (action === "wait for author") {
      return "Wait for the author to mark the PR ready for review.";
    }
    if (action === "ask for CI fix") {
      return "Ask the author to get failing checks green before deeper review.";
    }
    if (action === "wait for CI") {
      return "Wait for checks to finish before spending review time.";
    }
    if (action === "needs author follow-up") {
      if (flags.includes("merge conflicts")) {
        return "Ask the author to resolve merge conflicts before another review pass.";
      }
      if (flags.includes("branch behind base")) {
        return "Ask the author to update the branch with the base branch before review.";
      }
      if (flags.includes("maintainer blocker language") || flags.includes("maintainer blocking label")) {
        return "Ask the author to respond to unresolved maintainer feedback.";
      }
      return "Ask the author to address requested changes before another review pass.";
    }
    if (action === "request smaller PR") {
      return "Ask for a smaller split or a clear scope explanation.";
    }
    if (action === "review now") {
      if (signals.includes("docs-only shape")) {
        return "Review now as a likely low-risk docs-only change.";
      }
      return "Review now while the PR appears small, active, and low risk.";
    }
    if (action === "review with caution") {
      return "Review, but inspect the risk flags before approving.";
    }
    return "Triage manually before assigning reviewer time.";
  }

  function formatDelta(value) {
    const delta = Number(value || 0);
    return delta > 0 ? `+${delta}` : String(delta);
  }

  function formatImpact(scoreBreakdown) {
    if (!scoreBreakdown || !scoreBreakdown.length) {
      return "no score changes";
    }
    const visible = scoreBreakdown
      .slice(0, 3)
      .map((entry) => `${entry.label} (${formatDelta(entry.riskDelta)} risk)`);
    const hiddenCount = scoreBreakdown.length - visible.length;
    if (hiddenCount > 0) {
      visible.push(`${hiddenCount} more`);
    }
    return visible.join("; ");
  }

  function formatSignals(item) {
    const signals = [...(item.signals || []), ...(item.flags || [])];
    return signals.length ? signals.join(", ") : "no notable signals";
  }

  function isMaintainerBlocked(item) {
    const flags = item && Array.isArray(item.flags) ? item.flags : [];
    return (
      flags.includes("maintainer blocker language") ||
      flags.includes("maintainer blocking label")
    );
  }

  function markdownCell(value) {
    return String(value || "")
      .replaceAll("\n", " ")
      .replaceAll("|", "\\|")
      .trim();
  }

  function markdownPrLabel(item) {
    const title = markdownCell(`#${item.number} ${item.title}`);
    return item.url ? `[${title}](${item.url})` : title;
  }

  function intValue(value) {
    const number = Number(value || 0);
    return Number.isFinite(number) ? Math.trunc(number) : 0;
  }

  function estimateReviewMinutes(item) {
    const action = String((item && item.action) || "needs triage");
    const changedFiles = intValue(item && item.changedFiles);
    const totalDiff = intValue(item && item.additions) + intValue(item && item.deletions);
    const signals = item && Array.isArray(item.signals) ? item.signals : [];

    if (action === "wait for CI" || action === "wait for author") {
      return 0;
    }
    if (
      action === "ask for CI fix" ||
      action === "needs author follow-up" ||
      action === "request smaller PR"
    ) {
      return 5;
    }
    if (action === "needs triage") {
      return 8;
    }

    let base;
    if (signals.includes("docs-only shape")) {
      base = 6;
    } else if (totalDiff > 500 || changedFiles > 10) {
      base = 25;
    } else if (totalDiff > 150 || changedFiles > 5) {
      base = 18;
    } else {
      base = 12;
    }

    return action === "review with caution" ? base + 8 : base;
  }

  function planReason(item) {
    const flags = item && Array.isArray(item.flags) ? item.flags.filter(Boolean) : [];
    const signals = item && Array.isArray(item.signals) ? item.signals.filter(Boolean) : [];
    const visible = flags.length ? flags.slice(0, 2) : signals.slice(0, 2);
    return visible.length ? visible.join(", ") : "no notable signals";
  }

  function draftFollowUpComment(item) {
    const action = String((item && item.action) || "");
    if (!FOLLOW_UP_ACTIONS.has(action)) {
      return "";
    }
    const flags = item && Array.isArray(item.flags) ? item.flags : [];
    const requests = [];

    if (flags.some((flag) => String(flag).includes("CI failing"))) {
      requests.push("Get CI passing or explain why the failing check is unrelated.");
    }
    if (flags.some((flag) => String(flag).includes("CI pending"))) {
      requests.push("Wait for CI to finish before requesting another review.");
    }
    if (flags.some((flag) => String(flag).includes("no test plan"))) {
      requests.push("Add a short validation or test plan to the PR body.");
    }
    if (flags.some((flag) => String(flag).includes("code changed without tests"))) {
      requests.push("Add regression coverage, or explain why tests are not practical for this change.");
    }
    if (flags.some((flag) => String(flag).includes("maintainer blocker language"))) {
      requests.push("Respond to the unresolved maintainer feedback before the next review pass.");
    }
    if (flags.some((flag) => String(flag).includes("merge conflicts"))) {
      requests.push("Resolve merge conflicts before requesting another review pass.");
    }
    if (flags.some((flag) => String(flag).includes("branch behind base"))) {
      requests.push("Update the branch with the base branch, then rerun checks.");
    }
    if (flags.some((flag) => String(flag).includes("large diff"))) {
      requests.push("Consider splitting the PR or explaining why the current scope needs to stay together.");
    }
    if (flags.some((flag) => String(flag).startsWith("stale ") || String(flag).startsWith("quiet "))) {
      requests.push("Rebase or leave a short status update so reviewers know the PR is still active.");
    }
    if (!requests.length) {
      requests.push("Keep CI green and leave any extra context that would make review easier.");
    }

    const lines = [
      "Thanks for the PR.",
      "",
      `Current triage suggests: **${action || "needs triage"}**.`,
    ];
    if (item && item.reviewability !== undefined && item.reviewability !== null) {
      lines.push(`Reviewability score: **${item.reviewability}/100**.`);
    }
    lines.push("", "Before the next maintainer pass, please:");
    for (const request of requests) {
      lines.push(`- ${request}`);
    }
    lines.push("", "_Generated as a draft with Maintainer Radar. Please edit before posting._");
    return lines.join("\n");
  }

  function buildReviewPlan(items, budgetMinutes) {
    const budget = intValue(budgetMinutes);
    if (budget < 1) {
      throw new Error("Plan minutes must be 1 or greater.");
    }
    const candidates = [...(items || [])].sort((a, b) => {
      const aAction = String((a && a.action) || "");
      const bAction = String((b && b.action) || "");
      const priorityDelta =
        (PLAN_ACTION_PRIORITY[aAction] ?? 99) - (PLAN_ACTION_PRIORITY[bAction] ?? 99);
      if (priorityDelta) {
        return priorityDelta;
      }
      const minuteDelta = estimateReviewMinutes(a) - estimateReviewMinutes(b);
      if (minuteDelta) {
        return minuteDelta;
      }
      const scoreDelta = intValue(b && b.reviewability) - intValue(a && a.reviewability);
      if (scoreDelta) {
        return scoreDelta;
      }
      return intValue(a && a.number) - intValue(b && b.number);
    });

    const planned = [];
    const deferred = [];
    const waiting = [];
    let used = 0;

    for (const item of candidates) {
      const estimatedMinutes = estimateReviewMinutes(item);
      const entry = { item, estimatedMinutes, reason: planReason(item) };
      if (estimatedMinutes === 0) {
        waiting.push(entry);
      } else if (used + estimatedMinutes <= budget || planned.length === 0) {
        planned.push(entry);
        used += estimatedMinutes;
      } else {
        deferred.push(entry);
      }
    }

    return {
      budgetMinutes: budget,
      plannedMinutes: used,
      remainingMinutes: Math.max(0, budget - used),
      overBudgetMinutes: Math.max(0, used - budget),
      planned,
      deferred,
      waiting,
    };
  }

  function reviewPlanFollowUpEntries(plan, limit = 5) {
    const entries = [];
    for (const section of ["planned", "deferred", "waiting"]) {
      for (const entry of plan[section] || []) {
        if (draftFollowUpComment(entry.item)) {
          entries.push(entry);
        }
        if (entries.length >= limit) {
          return entries;
        }
      }
    }
    return entries;
  }

  function summarizeItems(items) {
    const total = items.length;
    const reviewNow = items.filter((item) => item.action === "review now").length;
    const followUp = items.filter((item) => item.action !== "review now").length;
    const authorFollowUp = items.filter((item) => item.action === "needs author follow-up").length;
    const ciBlocked = items.filter((item) => hasFlag(item, "CI failing")).length;
    const ciPending = items.filter((item) => hasFlag(item, "CI pending")).length;
    const mergeConflicts = items.filter((item) => hasFlag(item, "merge conflicts")).length;
    const branchBehind = items.filter((item) => hasFlag(item, "branch behind base")).length;
    const mergeGated = items.filter(
      (item) => hasFlag(item, "merge blocked by repo rules") || hasFlag(item, "merge checks unstable")
    ).length;
    const reviewRequested = items.filter((item) => intValue(item.reviewRequests) > 0).length;
    const maintainerBlocked = items.filter(isMaintainerBlocked).length;
    const largeOrTriage = items.filter(
      (item) => item.action === "request smaller PR" || item.action === "needs triage"
    ).length;
    const stale = items.filter((item) => intValue(item.staleDays) >= 7).length;
    const average = total
      ? Math.round(items.reduce((sum, item) => sum + item.reviewability, 0) / total)
      : 0;
    const nextSession = nextSessionSummary(items, DEFAULT_SESSION_MINUTES);
    const summary = {
      total,
      reviewNow,
      followUp,
      authorFollowUp,
      ciBlocked,
      ciPending,
      mergeConflicts,
      branchBehind,
      mergeGated,
      reviewRequested,
      maintainerBlocked,
      largeOrTriage,
      stale,
      average,
      ...nextSession,
    };
    summary.queueHeadline = queueHeadline(summary);
    const attention = attentionSignal(summary);
    summary.attentionLevel = attention.level;
    summary.attentionReason = attention.reason;
    const workflow = workflowRecommendation(summary);
    summary.workflowMode = workflow.mode;
    summary.workflowRecommendation = workflow.recommendation;
    return summary;
  }

  function nextSessionSummary(items, budgetMinutes) {
    const plan = buildReviewPlan(items || [], budgetMinutes);
    const quickUnblocks = (items || []).filter((item) => estimateReviewMinutes(item) === 5).length;
    const watchOnly = (items || []).filter((item) => estimateReviewMinutes(item) === 0).length;
    const summary = {
      nextSessionPrs: plan.planned.length,
      nextSessionMinutes: plan.plannedMinutes,
      nextSessionDeferred: plan.deferred.length,
      quickUnblocks,
      watchOnly,
    };
    summary.nextSessionBrief = nextSessionBrief(summary, budgetMinutes);
    return summary;
  }

  function nextSessionBrief(summary, budgetMinutes) {
    const planned = intValue(summary.nextSessionPrs);
    const minutes = intValue(summary.nextSessionMinutes);
    const deferred = intValue(summary.nextSessionDeferred);
    const quickUnblocks = intValue(summary.quickUnblocks);
    const watchOnly = intValue(summary.watchOnly);

    if (!planned && !deferred && !quickUnblocks && !watchOnly) {
      return `Next ${budgetMinutes} minutes: no matching PRs need maintainer time.`;
    }
    if (!planned) {
      return `Next ${budgetMinutes} minutes: no active review work fits yet; keep ${prCount(
        watchOnly
      )} on watch.`;
    }

    const parts = [`handle ${prCount(planned)} in about ${minutes} minutes`];
    if (quickUnblocks) {
      parts.push(`${quickUnblocks} ${quickUnblocks === 1 ? "quick unblock" : "quick unblocks"}`);
    }
    if (deferred) {
      parts.push(`${prCount(deferred)} deferred by the session budget`);
    }
    if (watchOnly) {
      parts.push(`${prCount(watchOnly)} watch-only`);
    }
    return `Next ${budgetMinutes} minutes: ${parts.join("; ")}.`;
  }

  function hasFlag(item, flag) {
    return (item.flags || []).includes(flag);
  }

  function queueHeadline(summary) {
    if (!summary.total) {
      return "No pull requests matched this scan.";
    }
    const parts = [];
    const ciTotal = summary.ciBlocked + summary.ciPending;
    if (summary.reviewNow) {
      parts.push(`${summary.reviewNow} ready for review`);
    }
    if (summary.authorFollowUp) {
      parts.push(needsPhrase(summary.authorFollowUp, "author follow-up"));
    }
    if (ciTotal) {
      parts.push(`${ciTotal} blocked or waiting on CI`);
    }
    if (summary.mergeConflicts) {
      parts.push(
        `${summary.mergeConflicts} with merge ${
          summary.mergeConflicts === 1 ? "conflict" : "conflicts"
        }`
      );
    }
    if (summary.branchBehind) {
      parts.push(`${summary.branchBehind} behind base`);
    }
    if (summary.mergeGated) {
      parts.push(`${summary.mergeGated} blocked by merge gates`);
    }
    if (summary.maintainerBlocked) {
      const verb = summary.maintainerBlocked === 1 ? "has" : "have";
      const blocker = summary.maintainerBlocked === 1 ? "blocker" : "blockers";
      parts.push(`${prCount(summary.maintainerBlocked)} ${verb} unresolved maintainer ${blocker}`);
    }
    if (!parts.length) {
      parts.push("no urgent blocker signals");
    }
    return `${prCount(summary.total)} scanned: ${parts.join("; ")}.`;
  }

  function attentionSignal(summary) {
    if (!summary.total) {
      return { level: "quiet", reason: "No pull requests matched this scan." };
    }
    if (summary.maintainerBlocked) {
      return {
        level: "blocked",
        reason: attentionReason(
          summary.maintainerBlocked,
          "has unresolved maintainer blocker",
          "have unresolved maintainer blockers"
        ),
      };
    }
    if (summary.mergeConflicts) {
      return {
        level: "blocked",
        reason: attentionReason(summary.mergeConflicts, "has merge conflicts", "have merge conflicts"),
      };
    }
    if (summary.ciBlocked) {
      return {
        level: "blocked",
        reason: attentionReason(summary.ciBlocked, "has failing CI", "have failing CI"),
      };
    }
    if (summary.mergeGated) {
      return {
        level: "blocked",
        reason: attentionReason(
          summary.mergeGated,
          "is blocked by repository merge gates",
          "are blocked by repository merge gates"
        ),
      };
    }
    if (summary.authorFollowUp) {
      return {
        level: "follow-up",
        reason: attentionReason(
          summary.authorFollowUp,
          "needs author follow-up",
          "need author follow-up"
        ),
      };
    }
    if (summary.branchBehind) {
      return {
        level: "follow-up",
        reason: attentionReason(summary.branchBehind, "is behind base", "are behind base"),
      };
    }
    if (summary.ciPending) {
      return {
        level: "follow-up",
        reason: attentionReason(summary.ciPending, "is waiting on CI", "are waiting on CI"),
      };
    }
    if (summary.reviewNow) {
      return {
        level: "review",
        reason: attentionReason(summary.reviewNow, "is ready for review", "are ready for review"),
      };
    }
    if (summary.largeOrTriage) {
      return {
        level: "triage",
        reason: attentionReason(
          summary.largeOrTriage,
          "needs triage or scope reduction",
          "need triage or scope reduction"
        ),
      };
    }
    if (summary.stale) {
      return {
        level: "follow-up",
        reason: attentionReason(summary.stale, "is stale", "are stale"),
      };
    }
    if (summary.reviewRequested) {
      return {
        level: "review",
        reason: attentionReason(
          summary.reviewRequested,
          "has requested reviewers",
          "have requested reviewers"
        ),
      };
    }
    return { level: "quiet", reason: "No urgent maintainer attention signal was found." };
  }

  function prCount(count) {
    return `${count} ${count === 1 ? "PR" : "PRs"}`;
  }

  function needsPhrase(count, noun) {
    return `${count} ${count === 1 ? "needs" : "need"} ${noun}`;
  }

  function attentionReason(count, singular, plural) {
    return `${prCount(count)} ${count === 1 ? singular : plural}.`;
  }

  function workflowRecommendation(summary) {
    if (!summary.total) {
      return {
        mode: "quiet",
        recommendation: "No matching PRs. Keep the scheduled scan quiet.",
      };
    }
    if (
      summary.maintainerBlocked ||
      summary.mergeConflicts ||
      summary.ciBlocked ||
      summary.mergeGated
    ) {
      return {
        mode: "blocker-sweep",
        recommendation:
          "Clear maintainer blockers, merge conflicts, failing CI, or merge gates before assigning review time.",
      };
    }
    if (summary.reviewNow) {
      return {
        mode: "review-sprint",
        recommendation: "Start a focused review block with the ready PRs.",
      };
    }
    if (summary.authorFollowUp || summary.branchBehind) {
      return {
        mode: "author-follow-up",
        recommendation: "Send author follow-ups for waiting authors or branches behind base.",
      };
    }
    if (summary.largeOrTriage) {
      return {
        mode: "triage-pass",
        recommendation: "Classify or split large and unclear PRs before review.",
      };
    }
    if (summary.ciPending) {
      return {
        mode: "ci-watch",
        recommendation: "Wait for pending checks before spending review time.",
      };
    }
    if (summary.stale) {
      return {
        mode: "stale-sweep",
        recommendation: "Run a stale follow-up pass before assigning review time.",
      };
    }
    if (summary.reviewRequested) {
      return {
        mode: "review-sprint",
        recommendation: "Handle requested reviews that have no stronger blocker signal.",
      };
    }
    return {
      mode: "quiet",
      recommendation: "No urgent maintainer workflow was found.",
    };
  }

  function groupItemsByAction(items) {
    const groups = [];
    const byAction = new Map();
    for (const item of items || []) {
      const action = item.action || "needs triage";
      if (!byAction.has(action)) {
        const group = { action, items: [] };
        byAction.set(action, group);
        groups.push(group);
      }
      byAction.get(action).items.push(item);
    }
    return groups;
  }

  function renderMarkdownTable(lines, items) {
    lines.push(
      "| PR | Action | Next Step | Score | Risk Impact | Signals |",
      "| --- | --- | --- | ---: | --- | --- |"
    );
    if (!items || !items.length) {
      lines.push("| No open PRs found | n/a | n/a | 0 | n/a | n/a |");
      return;
    }
    for (const item of items) {
      const title = `#${item.number} ${item.title}`;
      const label = item.url ? `[${markdownCell(title)}](${item.url})` : markdownCell(title);
      lines.push(
        `| ${label} | ${markdownCell(item.action)} | ${markdownCell(
          item.nextStep
        )} | ${item.reviewability} | ${markdownCell(formatImpact(item.scoreBreakdown))} | ${markdownCell(
          formatSignals(item)
        )} |`
      );
    }
  }

  function renderMarkdownReport(items, repository, shareUrl, options = {}) {
    const summary = summarizeItems(items || []);
    const lines = [
      `## Maintainer Radar Preview: ${repository}`,
      "",
      summary.queueHeadline,
      "",
      `- Attention level: ${summary.attentionLevel}`,
      `- Attention reason: ${summary.attentionReason}`,
      `- Workflow mode: ${summary.workflowMode}`,
      `- Workflow recommendation: ${summary.workflowRecommendation}`,
      `- Next session: ${summary.nextSessionBrief}`,
      `- PRs scanned: ${summary.total}`,
      `- Review now: ${summary.reviewNow}`,
      `- Follow-up: ${summary.followUp}`,
      `- Quick unblocks: ${summary.quickUnblocks}`,
      `- Watch only: ${summary.watchOnly}`,
      `- Next-session PRs: ${summary.nextSessionPrs}`,
      `- Next-session active time: ${summary.nextSessionMinutes} minutes`,
      `- Next-session deferred: ${summary.nextSessionDeferred}`,
      `- Maintainer blocked: ${summary.maintainerBlocked}`,
      `- Average reviewability: ${summary.average}/100`,
    ];
    if (shareUrl) {
      lines.push(`- Demo link: ${shareUrl}`);
    }
    lines.push("");

    if (options.groupByAction && items && items.length) {
      for (const group of groupItemsByAction(items)) {
        const count = group.items.length;
        const label = count === 1 ? "PR" : "PRs";
        lines.push(`### ${group.action} (${count} ${label})`, "");
        renderMarkdownTable(lines, group.items);
        lines.push("");
      }
    } else {
      renderMarkdownTable(lines, items || []);
    }

    lines.push(
      "",
      "Generated by Maintainer Radar's browser preview. Use the CLI for deeper hydrated scans."
    );
    return `${lines.join("\n")}\n`;
  }

  function renderReviewPlanMarkdown(items, repository, budgetMinutes, shareUrl = "") {
    const plan = buildReviewPlan(items || [], budgetMinutes);
    const summary = summarizeItems(items || []);
    const lines = [
      `## Maintainer Radar Review Plan: ${repository}`,
      "",
      `- Time budget: ${plan.budgetMinutes} minutes`,
      `- Planned PRs: ${plan.planned.length}`,
      `- Estimated active time: ${plan.plannedMinutes} minutes`,
      `- Left for interrupts: ${plan.remainingMinutes} minutes`,
      `- Attention level: ${summary.attentionLevel}`,
      `- Attention reason: ${summary.attentionReason}`,
      `- Workflow mode: ${summary.workflowMode}`,
      `- Workflow recommendation: ${summary.workflowRecommendation}`,
      `- Queue scanned: ${summary.total} PRs`,
      `- Review now: ${summary.reviewNow}`,
      `- Maintainer blocked: ${summary.maintainerBlocked}`,
    ];
    if (shareUrl) {
      lines.push(`- Demo link: ${shareUrl}`);
    }
    lines.push("");
    if (plan.overBudgetMinutes) {
      lines.push(`First planned item exceeds the budget by ${plan.overBudgetMinutes} minutes.`, "");
    }

    if (plan.planned.length) {
      lines.push(
        "| Order | PR | Action | Est. | Next Step | Why |",
        "| ---: | --- | --- | ---: | --- | --- |"
      );
      for (const [index, entry] of plan.planned.entries()) {
        const item = entry.item;
        lines.push(
          `| ${index + 1} | ${markdownPrLabel(item)} | ${markdownCell(item.action)} | ${
            entry.estimatedMinutes
          }m | ${markdownCell(item.nextStep)} | ${markdownCell(entry.reason)} |`
        );
      }
    } else {
      lines.push("No active maintainer work was found for this budget.");
    }

    if (plan.deferred.length) {
      lines.push("", "### Deferred by Budget", "");
      for (const entry of plan.deferred.slice(0, 5)) {
        lines.push(
          `- ${markdownPrLabel(entry.item)}: ${entry.estimatedMinutes}m, ${markdownCell(
            entry.item.action
          )}`
        );
      }
    }

    if (plan.waiting.length) {
      lines.push("", "### Watch Only", "");
      for (const entry of plan.waiting.slice(0, 5)) {
        lines.push(`- ${markdownPrLabel(entry.item)}: ${markdownCell(entry.item.nextStep)}`);
      }
    }

    const followUps = reviewPlanFollowUpEntries(plan);
    if (followUps.length) {
      lines.push("", "### Draft Follow-ups", "");
      for (const entry of followUps) {
        lines.push(
          `#### ${markdownPrLabel(entry.item)}`,
          "",
          "```markdown",
          draftFollowUpComment(entry.item),
          "```",
          ""
        );
      }
    }

    lines.push(
      "",
      "Generated by Maintainer Radar's browser preview. Use the plan to spend attention, not to skip review."
    );
    return `${lines.join("\n")}\n`;
  }

  function reviewPlanJsonEntry(entry) {
    const item = entry.item || {};
    return {
      number: item.number,
      title: item.title || "Untitled",
      url: item.url || "",
      action: item.action || "needs triage",
      next_step: item.nextStep || "Triage manually before assigning reviewer time.",
      estimated_minutes: intValue(entry.estimatedMinutes),
      reason: entry.reason || "no notable signals",
      reviewability: intValue(item.reviewability),
      risk: intValue(item.risk),
      signals: Array.isArray(item.signals) ? item.signals.filter(Boolean) : [],
      flags: Array.isArray(item.flags) ? item.flags.filter(Boolean) : [],
      draft_follow_up_comment: draftFollowUpComment(item),
    };
  }

  function renderReviewPlanJson(items, repository, budgetMinutes, shareUrl = "") {
    const plan = buildReviewPlan(items || [], budgetMinutes);
    const summary = summarizeItems(items || []);
    return `${JSON.stringify(
      {
        repository,
        demo_link: shareUrl || "",
        budget_minutes: plan.budgetMinutes,
        planned_minutes: plan.plannedMinutes,
        remaining_minutes: plan.remainingMinutes,
        over_budget_minutes: plan.overBudgetMinutes,
        queue_summary: {
          total: summary.total,
          review_now: summary.reviewNow,
          follow_up: summary.followUp,
          maintainer_blocked: summary.maintainerBlocked,
          average_score: summary.average,
          queue_headline: summary.queueHeadline,
          attention_level: summary.attentionLevel,
          attention_reason: summary.attentionReason,
          workflow_mode: summary.workflowMode,
          workflow_recommendation: summary.workflowRecommendation,
          next_session_brief: summary.nextSessionBrief,
          next_session_prs: summary.nextSessionPrs,
          next_session_minutes: summary.nextSessionMinutes,
          next_session_deferred: summary.nextSessionDeferred,
          quick_unblocks: summary.quickUnblocks,
          watch_only: summary.watchOnly,
        },
        planned: plan.planned.map(reviewPlanJsonEntry),
        deferred: plan.deferred.map(reviewPlanJsonEntry),
        watch_only: plan.waiting.map(reviewPlanJsonEntry),
      },
      null,
      2
    )}\n`;
  }

  function renderActionWorkflow(options = {}) {
    const budgetMinutes = intValue(options.budgetMinutes || 30);
    if (budgetMinutes < 1) {
      throw new Error("Plan minutes must be 1 or greater.");
    }
    return [
      "name: Maintainer Radar Review Plan",
      "",
      "on:",
      "  workflow_dispatch:",
      "  schedule:",
      '    - cron: "0 8 * * 1-5"',
      "",
      "permissions:",
      "  contents: read",
      "  pull-requests: read",
      "",
      "jobs:",
      "  review-plan:",
      "    runs-on: ubuntu-latest",
      "    steps:",
      "      - uses: actions/setup-python@v6",
      "        with:",
      '          python-version: "3.12"',
      `      - name: Build ${budgetMinutes} minute review plan`,
      "        id: radar",
      `        uses: JackSpiece/maintainer-radar@${ACTION_VERSION}`,
      "        env:",
      "          GH_TOKEN: ${{ github.token }}",
      "        with:",
      "          repository: ${{ github.repository }}",
      "          format: markdown",
      "          output: review-plan.md",
      '          limit: "50"',
      "          sort: action",
      `          review-plan-minutes: "${budgetMinutes}"`,
      '          hydrate: "true"',
      "      - uses: actions/upload-artifact@v7",
      "        with:",
      "          name: review-plan",
      "          path: ${{ steps.radar.outputs.report-path }}",
      "",
    ].join("\n");
  }

  function actionClass(action) {
    if (action === "review now") {
      return "review";
    }
    if (action === "request smaller PR" || action === "review with caution") {
      return "caution";
    }
    return "ci";
  }

  async function requestJson(path) {
    const response = await fetch(`https://api.github.com${path}`, {
      headers: { Accept: "application/vnd.github+json" },
    });
    if (!response.ok) {
      const remaining = response.headers.get("x-ratelimit-remaining");
      if (response.status === 403 && remaining === "0") {
        throw new Error("GitHub API rate limit reached. Try again later.");
      }
      throw new Error(`GitHub returned HTTP ${response.status}.`);
    }
    return response.json();
  }

  async function requestOptionalJson(path) {
    try {
      return await requestJson(path);
    } catch (_error) {
      return null;
    }
  }

  async function fetchPreview(repository) {
    const pulls = await requestJson(
      `/repos/${repository}/pulls?state=open&sort=updated&direction=desc&per_page=${MAX_PULLS}`
    );
    return Promise.all(
      pulls.map(async (pull) => {
        const [detail, files] = await Promise.all([
          requestJson(`/repos/${repository}/pulls/${pull.number}`),
          requestJson(`/repos/${repository}/pulls/${pull.number}/files?per_page=100`),
        ]);
        const sha = detail && detail.head && detail.head.sha;
        const checks = sha
          ? await requestOptionalJson(`/repos/${repository}/commits/${sha}/check-runs?per_page=100`)
          : null;
        const checkRuns = checks && Array.isArray(checks.check_runs) ? checks.check_runs : null;
        return analyzePullRequest(detail, files, { checkRuns });
      })
    );
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function renderPreview(items, repository, options = {}) {
    const summary = summarizeItems(items);

    document.querySelector("#metric-total").textContent = String(summary.total);
    document.querySelector("#metric-session").textContent = String(summary.nextSessionPrs);
    document.querySelector("#metric-review").textContent = String(summary.reviewNow);
    document.querySelector("#metric-followup").textContent = String(summary.followUp);
    document.querySelector("#metric-quick").textContent = String(summary.quickUnblocks);
    document.querySelector("#metric-blocked").textContent = String(summary.maintainerBlocked);
    document.querySelector("#metric-score").textContent = String(summary.average);
    const attentionCard = document.querySelector("#attention-card");
    const attentionLevel = document.querySelector("#attention-level");
    const attentionHeadline = document.querySelector("#attention-headline");
    const attentionReason = document.querySelector("#attention-reason");
    const workflowMode = document.querySelector("#workflow-mode");
    const workflowRecommendation = document.querySelector("#workflow-recommendation");
    const nextSessionBrief = document.querySelector("#next-session-brief");
    if (
      attentionCard &&
      attentionLevel &&
      attentionHeadline &&
      attentionReason &&
      workflowMode &&
      workflowRecommendation &&
      nextSessionBrief
    ) {
      attentionCard.dataset.level = summary.attentionLevel;
      attentionLevel.textContent = summary.attentionLevel;
      attentionHeadline.textContent = summary.queueHeadline;
      attentionReason.textContent = summary.attentionReason;
      workflowMode.textContent = `Workflow: ${summary.workflowMode}`;
      workflowRecommendation.textContent = summary.workflowRecommendation;
      nextSessionBrief.textContent = summary.nextSessionBrief;
    }

    const body = document.querySelector("#queue-body");
    if (!body) {
      return;
    }
    if (!items.length) {
      body.innerHTML = `<tr><td colspan="6">No open pull requests found for ${escapeHtml(repository)}.</td></tr>`;
      return;
    }
    const rows = [];
    const groups = options.groupByAction
      ? groupItemsByAction(items).flatMap((group) => [
          { group: group.action, count: group.items.length },
          ...group.items,
        ])
      : items;
    for (const item of groups) {
      if (item.group) {
        const label = item.count === 1 ? "PR" : "PRs";
        rows.push(
          `<tr class="group-row"><td colspan="6">${escapeHtml(item.group)} - ${item.count} ${label}</td></tr>`
        );
        continue;
      }
      const label = `#${item.number} ${item.title}`;
      const pr = item.url
        ? `<a href="${escapeHtml(item.url)}">${escapeHtml(label)}</a>`
        : escapeHtml(label);
      rows.push(`<tr>
          <td>${pr}</td>
          <td><span class="pill ${actionClass(item.action)}">${escapeHtml(item.action)}</span></td>
          <td>${escapeHtml(item.nextStep)}</td>
          <td class="score">${item.reviewability}</td>
          <td class="impact">${escapeHtml(formatImpact(item.scoreBreakdown))}</td>
          <td class="signals">${escapeHtml(formatSignals(item))}</td>
        </tr>`);
    }
    body.innerHTML = rows.join("");
  }

  function renderPlanPreview(items, budgetMinutes) {
    const title = document.querySelector("#plan-title");
    const meta = document.querySelector("#plan-meta");
    const body = document.querySelector("#plan-body");
    if (!title || !meta || !body) {
      return;
    }
    try {
      const plan = buildReviewPlan(items || [], budgetMinutes);
      title.textContent = `${plan.budgetMinutes} minute review plan`;
      meta.textContent = `${plan.plannedMinutes}m active - ${plan.remainingMinutes}m open`;
      if (!plan.planned.length) {
        body.innerHTML =
          '<div class="plan-row"><span>0</span><strong>No active maintainer work</strong><span>watch only</span></div>';
        return;
      }
      body.innerHTML = plan.planned
        .slice(0, 3)
        .map((entry, index) => {
          const item = entry.item;
          const label = `#${item.number} ${item.title}`;
          return `<div class="plan-row">
            <span>${index + 1}</span>
            <strong>${escapeHtml(label)}</strong>
            <span>${escapeHtml(item.action)} - ${entry.estimatedMinutes}m</span>
          </div>`;
        })
        .join("");
    } catch (error) {
      title.textContent = "Review plan";
      meta.textContent = error instanceof Error ? error.message : "Plan unavailable";
      body.innerHTML =
        '<div class="plan-row"><span>!</span><strong>Plan unavailable</strong><span>check minutes</span></div>';
    }
  }

  function renderDraftFollowUpPreview(items, budgetMinutes) {
    const meta = document.querySelector("#draft-meta");
    const body = document.querySelector("#draft-followup-body");
    if (!meta || !body) {
      return;
    }
    try {
      const plan = buildReviewPlan(items || [], budgetMinutes);
      const followUps = reviewPlanFollowUpEntries(plan, 3);
      if (!followUps.length) {
        meta.textContent = "0 editable asks";
        body.innerHTML =
          '<p class="draft-empty">No draft follow-ups for the current review plan.</p>';
        return;
      }
      const askLabel = followUps.length === 1 ? "editable ask" : "editable asks";
      meta.textContent = `${followUps.length} ${askLabel}`;
      body.innerHTML = followUps
        .map((entry, index) => {
          const item = entry.item || {};
          const label = `#${item.number} ${item.title || "Untitled"}`;
          const copyId = `demo-draft-follow-up-${index + 1}`;
          return `<article class="draft-item">
              <div class="draft-title">
                <strong>${escapeHtml(label)}</strong>
                <button type="button" data-copy-target="${copyId}" data-copy-label="#${escapeHtml(
                  item.number || index + 1
                )}">Copy Draft</button>
              </div>
              <pre id="${copyId}">${escapeHtml(draftFollowUpComment(item))}</pre>
            </article>`;
        })
        .join("");
    } catch (error) {
      meta.textContent = "unavailable";
      body.innerHTML =
        '<p class="draft-empty">Draft follow-ups are unavailable. Check plan minutes.</p>';
    }
  }

  function setStatus(message) {
    const status = document.querySelector("#demo-status");
    if (status) {
      status.textContent = message;
    }
  }

  function init() {
    const form = document.querySelector("#repo-form");
    const input = document.querySelector("#repo-input");
    const button = document.querySelector("#repo-submit");
    const copyButton = document.querySelector("#copy-link");
    const badgeButton = document.querySelector("#copy-badge");
    const cliButton = document.querySelector("#copy-cli");
    const markdownButton = document.querySelector("#copy-markdown");
    const planButton = document.querySelector("#copy-plan");
    const planJsonButton = document.querySelector("#copy-plan-json");
    const planMinutesInput = document.querySelector("#plan-minutes");
    const workflowButton = document.querySelector("#copy-workflow");
    const groupToggle = document.querySelector("#group-action");
    const draftBody = document.querySelector("#draft-followup-body");
    if (
      !form ||
      !input ||
      !button ||
      !copyButton ||
      !badgeButton ||
      !cliButton ||
      !markdownButton ||
      !planButton ||
      !planJsonButton ||
      !planMinutesInput ||
      !workflowButton ||
      !groupToggle ||
      !draftBody
    ) {
      return;
    }

    let currentRepository = "";
    let currentItems = [];
    let currentShareUrl = "";
    let currentScanReady = false;

    function setShareRepository(repository) {
      currentRepository = normalizeRepository(repository);
      copyButton.disabled = !currentRepository;
      badgeButton.disabled = !currentRepository;
      cliButton.disabled = !currentRepository;
      markdownButton.disabled = !currentRepository || !currentScanReady;
      planButton.disabled = !currentRepository || !currentScanReady;
      planJsonButton.disabled = !currentRepository || !currentScanReady;
    }

    function updateLocation(repository) {
      const shareUrl = shareUrlForRepository(window.location.href, repository, {
        groupByAction: groupToggle.checked,
        planMinutes: planMinutesInput.value,
      });
      if (shareUrl && window.history && window.history.replaceState) {
        window.history.replaceState(null, "", shareUrl);
      }
      return shareUrl;
    }

    function submitForm() {
      if (form.requestSubmit) {
        form.requestSubmit();
      } else {
        form.dispatchEvent(new Event("submit", { cancelable: true }));
      }
    }

    async function copyText(value, successMessage, fallbackMessage) {
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) {
          throw new Error("Clipboard API is unavailable.");
        }
        await navigator.clipboard.writeText(value);
        setStatus(successMessage);
      } catch (_error) {
        setStatus(fallbackMessage);
      }
    }

    draftBody.addEventListener("click", async (event) => {
      const target = event.target;
      if (!(target instanceof Element)) {
        return;
      }
      const draftButton = target.closest("[data-copy-target]");
      if (!(draftButton instanceof HTMLButtonElement)) {
        return;
      }
      const source = document.getElementById(draftButton.dataset.copyTarget || "");
      if (!source) {
        setStatus("Draft follow-up is unavailable.");
        return;
      }
      const label = draftButton.dataset.copyLabel || "PR";
      await copyText(
        source.textContent || "",
        `Copied draft follow-up for ${label}.`,
        "Draft follow-up is ready, but clipboard access is unavailable."
      );
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const repository = normalizeRepository(input.value);
      if (!repository) {
        setStatus("Enter a repository as owner/repo.");
        return;
      }

      button.disabled = true;
      currentItems = [];
      currentShareUrl = "";
      currentScanReady = false;
      setShareRepository("");
      setStatus(`Scanning ${repository} with public GitHub API data.`);
      try {
        const items = await fetchPreview(repository);
        renderPreview(items, repository, { groupByAction: groupToggle.checked });
        renderPlanPreview(items, planMinutesInput.value);
        renderDraftFollowUpPreview(items, planMinutesInput.value);
        const shareUrl = updateLocation(repository);
        currentItems = items;
        currentShareUrl = shareUrl;
        currentScanReady = true;
        setShareRepository(repository);
        setStatus(
          `Scanned ${items.length} recent open PRs from ${repository}. Share link ready: ${shareUrl}`
        );
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Scan failed.");
      } finally {
        button.disabled = false;
      }
    });

    copyButton.addEventListener("click", async () => {
      const repository = currentRepository || normalizeRepository(input.value);
      const shareUrl = shareUrlForRepository(window.location.href, repository, {
        groupByAction: groupToggle.checked,
        planMinutes: planMinutesInput.value,
      });
      if (!shareUrl) {
        setStatus("Scan a repository before copying a share link.");
        return;
      }
      await copyText(shareUrl, `Copied share link for ${repository}.`, `Share link: ${shareUrl}`);
    });

    badgeButton.addEventListener("click", async () => {
      const repository = currentRepository || normalizeRepository(input.value);
      const shareUrl = shareUrlForRepository(window.location.href, repository, {
        groupByAction: groupToggle.checked,
        planMinutes: planMinutesInput.value,
      });
      const badge = renderBadgeMarkdown(repository, shareUrl);
      if (!badge) {
        setStatus("Scan a repository before copying a badge.");
        return;
      }
      await copyText(
        badge,
        `Copied README badge for ${repository}.`,
        `Badge Markdown: ${badge}`
      );
    });

    cliButton.addEventListener("click", async () => {
      const repository = currentRepository || normalizeRepository(input.value);
      const command = renderCliCommand(repository, { groupByAction: groupToggle.checked });
      if (!command) {
        setStatus("Enter a repository before copying a CLI command.");
        return;
      }
      await copyText(
        command,
        `Copied CLI command for ${repository}.`,
        `CLI command: ${command}`
      );
    });

    markdownButton.addEventListener("click", async () => {
      if (!currentRepository || !currentScanReady) {
        setStatus("Scan a repository before copying Markdown.");
        return;
      }
      const markdown = renderMarkdownReport(currentItems, currentRepository, currentShareUrl, {
        groupByAction: groupToggle.checked,
      });
      await copyText(
        markdown,
        `Copied Markdown brief for ${currentRepository}.`,
        "Markdown brief is ready, but clipboard access is unavailable."
      );
    });

    planButton.addEventListener("click", async () => {
      if (!currentRepository || !currentScanReady) {
        setStatus("Scan a repository before copying a review plan.");
        return;
      }
      try {
        const plan = renderReviewPlanMarkdown(
          currentItems,
          currentRepository,
          planMinutesInput.value,
          currentShareUrl
        );
        await copyText(
          plan,
          `Copied review plan for ${currentRepository}.`,
          "Review plan is ready, but clipboard access is unavailable."
        );
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Review plan failed.");
      }
    });

    planJsonButton.addEventListener("click", async () => {
      if (!currentRepository || !currentScanReady) {
        setStatus("Scan a repository before copying review-plan JSON.");
        return;
      }
      try {
        const planJson = renderReviewPlanJson(
          currentItems,
          currentRepository,
          planMinutesInput.value,
          currentShareUrl
        );
        await copyText(
          planJson,
          `Copied review-plan JSON for ${currentRepository}.`,
          "Review-plan JSON is ready, but clipboard access is unavailable."
        );
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Review-plan JSON failed.");
      }
    });

    workflowButton.addEventListener("click", async () => {
      try {
        const workflow = renderActionWorkflow({ budgetMinutes: planMinutesInput.value });
        await copyText(
          workflow,
          `Copied review-plan workflow using Maintainer Radar ${ACTION_VERSION}.`,
          "Workflow YAML is ready, but clipboard access is unavailable."
        );
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Workflow generation failed.");
      }
    });

    groupToggle.addEventListener("change", () => {
      if (currentScanReady) {
        renderPreview(currentItems, currentRepository, { groupByAction: groupToggle.checked });
        renderPlanPreview(currentItems, planMinutesInput.value);
        renderDraftFollowUpPreview(currentItems, planMinutesInput.value);
        currentShareUrl = updateLocation(currentRepository);
      }
    });

    planMinutesInput.addEventListener("input", () => {
      if (currentScanReady) {
        renderPlanPreview(currentItems, planMinutesInput.value);
        renderDraftFollowUpPreview(currentItems, planMinutesInput.value);
        currentShareUrl = updateLocation(currentRepository);
      }
    });

    groupToggle.checked = groupByActionFromSearch(window.location.search);
    const initialPlanMinutes = planMinutesFromSearch(window.location.search);
    if (initialPlanMinutes) {
      planMinutesInput.value = String(initialPlanMinutes);
    }
    const initialRepository = repositoryFromSearch(window.location.search);
    if (initialRepository) {
      input.value = initialRepository;
      setShareRepository(initialRepository);
      submitForm();
    }
  }

  const api = {
    analyzePullRequest,
    chooseAction,
    formatImpact,
    groupByActionFromSearch,
    groupItemsByAction,
    hasBlockingLabel,
    isMaintainerBlocked,
    labelNames,
    mergeableState,
    mergeStateStatus,
    buildReviewPlan,
    draftFollowUpComment,
    estimateReviewMinutes,
    normalizeRepository,
    normalizePlanMinutes,
    planMinutesFromSearch,
    recommendNextStep,
    renderBadgeMarkdown,
    renderCliCommand,
    renderReviewPlanJson,
    renderReviewPlanMarkdown,
    repositoryFromSearch,
    renderMarkdownReport,
    renderDraftFollowUpPreview,
    renderActionWorkflow,
    reviewPlanFollowUpEntries,
    reviewRequestCount,
    shareUrlForRepository,
    summarizeCheckRuns,
    summarizeItems,
    summarizeFiles,
    workflowRecommendation,
  };

  if (typeof window !== "undefined") {
    window.MaintainerRadarDemo = api;
    init();
  }
  if (typeof module !== "undefined") {
    module.exports = api;
  }
})();
