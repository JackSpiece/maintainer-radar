(() => {
  const MAX_PULLS = 5;
  const ACTION_VERSION = "v0.16.8";
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

  function shareUrlForRepository(baseUrl, value) {
    const repository = normalizeRepository(value);
    if (!repository) {
      return "";
    }
    const url = new URL(
      String(baseUrl || "https://jackspiece.github.io/maintainer-radar/"),
      "https://jackspiece.github.io/maintainer-radar/"
    );
    url.searchParams.set("repo", repository);
    return url.toString();
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
    };
  }

  function chooseAction({ reviewability, isDraft, checks, hasCheckData, totalDiff, changedFiles }) {
    if (isDraft) {
      return "wait for author";
    }
    if (hasCheckData && checks && checks.failed) {
      return "ask for CI fix";
    }
    if (hasCheckData && checks && checks.pending) {
      return "wait for CI";
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
      if (flags.includes("maintainer blocker language")) {
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

  function markdownCell(value) {
    return String(value || "")
      .replaceAll("\n", " ")
      .replaceAll("|", "\\|")
      .trim();
  }

  function summarizeItems(items) {
    const total = items.length;
    const reviewNow = items.filter((item) => item.action === "review now").length;
    const followUp = items.filter((item) => item.action !== "review now").length;
    const average = total
      ? Math.round(items.reduce((sum, item) => sum + item.reviewability, 0) / total)
      : 0;
    return { total, reviewNow, followUp, average };
  }

  function renderMarkdownReport(items, repository, shareUrl) {
    const summary = summarizeItems(items || []);
    const lines = [
      `## Maintainer Radar Preview: ${repository}`,
      "",
      `- PRs scanned: ${summary.total}`,
      `- Review now: ${summary.reviewNow}`,
      `- Follow-up: ${summary.followUp}`,
      `- Average reviewability: ${summary.average}/100`,
    ];
    if (shareUrl) {
      lines.push(`- Demo link: ${shareUrl}`);
    }
    lines.push(
      "",
      "| PR | Action | Next Step | Score | Risk Impact | Signals |",
      "| --- | --- | --- | ---: | --- | --- |"
    );

    if (!items || !items.length) {
      lines.push("| No open PRs found | n/a | n/a | 0 | n/a | n/a |");
    } else {
      for (const item of items) {
        const title = `#${item.number} ${item.title}`;
        const label = item.url ? `[${markdownCell(title)}](${item.url})` : markdownCell(title);
        lines.push(
          `| ${label} | ${markdownCell(item.action)} | ${markdownCell(
            item.nextStep
          )} | ${item.reviewability} | ${markdownCell(
            formatImpact(item.scoreBreakdown)
          )} | ${markdownCell(formatSignals(item))} |`
        );
      }
    }

    lines.push(
      "",
      "Generated by Maintainer Radar's browser preview. Use the CLI for deeper hydrated scans."
    );
    return `${lines.join("\n")}\n`;
  }

  function renderActionWorkflow() {
    return [
      "name: Maintainer Radar",
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
      "  report:",
      "    runs-on: ubuntu-latest",
      "    steps:",
      "      - uses: actions/setup-python@v6",
      "        with:",
      '          python-version: "3.12"',
      "      - name: Build PR report",
      "        id: radar",
      `        uses: JackSpiece/maintainer-radar@${ACTION_VERSION}`,
      "        env:",
      "          GH_TOKEN: ${{ github.token }}",
      "        with:",
      "          repository: ${{ github.repository }}",
      "          format: markdown",
      "          output: maintainer-radar.md",
      '          limit: "50"',
      "          sort: action",
      '          hydrate: "true"',
      "      - uses: actions/upload-artifact@v4",
      "        with:",
      "          name: maintainer-radar",
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

  function renderPreview(items, repository) {
    const summary = summarizeItems(items);

    document.querySelector("#metric-total").textContent = String(summary.total);
    document.querySelector("#metric-review").textContent = String(summary.reviewNow);
    document.querySelector("#metric-followup").textContent = String(summary.followUp);
    document.querySelector("#metric-score").textContent = String(summary.average);

    const body = document.querySelector("#queue-body");
    if (!body) {
      return;
    }
    if (!items.length) {
      body.innerHTML = `<tr><td colspan="6">No open pull requests found for ${escapeHtml(repository)}.</td></tr>`;
      return;
    }
    body.innerHTML = items
      .map((item) => {
        const label = `#${item.number} ${item.title}`;
        const pr = item.url
          ? `<a href="${escapeHtml(item.url)}">${escapeHtml(label)}</a>`
          : escapeHtml(label);
        return `<tr>
          <td>${pr}</td>
          <td><span class="pill ${actionClass(item.action)}">${escapeHtml(item.action)}</span></td>
          <td>${escapeHtml(item.nextStep)}</td>
          <td class="score">${item.reviewability}</td>
          <td class="impact">${escapeHtml(formatImpact(item.scoreBreakdown))}</td>
          <td class="signals">${escapeHtml(formatSignals(item))}</td>
        </tr>`;
      })
      .join("");
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
    const markdownButton = document.querySelector("#copy-markdown");
    const workflowButton = document.querySelector("#copy-workflow");
    if (!form || !input || !button || !copyButton || !markdownButton || !workflowButton) {
      return;
    }

    let currentRepository = "";
    let currentItems = [];
    let currentShareUrl = "";
    let currentScanReady = false;

    function setShareRepository(repository) {
      currentRepository = normalizeRepository(repository);
      copyButton.disabled = !currentRepository;
      markdownButton.disabled = !currentRepository || !currentScanReady;
    }

    function updateLocation(repository) {
      const shareUrl = shareUrlForRepository(window.location.href, repository);
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
        renderPreview(items, repository);
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
      const shareUrl = shareUrlForRepository(window.location.href, repository);
      if (!shareUrl) {
        setStatus("Scan a repository before copying a share link.");
        return;
      }
      await copyText(shareUrl, `Copied share link for ${repository}.`, `Share link: ${shareUrl}`);
    });

    markdownButton.addEventListener("click", async () => {
      if (!currentRepository || !currentScanReady) {
        setStatus("Scan a repository before copying Markdown.");
        return;
      }
      const markdown = renderMarkdownReport(currentItems, currentRepository, currentShareUrl);
      await copyText(
        markdown,
        `Copied Markdown brief for ${currentRepository}.`,
        "Markdown brief is ready, but clipboard access is unavailable."
      );
    });

    workflowButton.addEventListener("click", async () => {
      const workflow = renderActionWorkflow();
      await copyText(
        workflow,
        `Copied GitHub Action workflow using Maintainer Radar ${ACTION_VERSION}.`,
        "Workflow YAML is ready, but clipboard access is unavailable."
      );
    });

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
    normalizeRepository,
    recommendNextStep,
    repositoryFromSearch,
    renderMarkdownReport,
    renderActionWorkflow,
    shareUrlForRepository,
    summarizeCheckRuns,
    summarizeItems,
    summarizeFiles,
  };

  if (typeof window !== "undefined") {
    window.MaintainerRadarDemo = api;
    init();
  }
  if (typeof module !== "undefined") {
    module.exports = api;
  }
})();
