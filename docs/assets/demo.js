(() => {
  const MAX_PULLS = 5;
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

  function analyzePullRequest(pr, files, now = new Date()) {
    const fileSummary = summarizeFiles(files);
    const additions = Number(pr.additions || 0);
    const deletions = Number(pr.deletions || 0);
    const changedFiles = Number(pr.changed_files || fileSummary.totalFiles || 0);
    const totalDiff = additions + deletions;
    const staleDays = daysSince(pr.updated_at, now);
    const hasBody = Object.prototype.hasOwnProperty.call(pr, "body");
    const hasTestPlan = TEST_PLAN_RE.test(String(pr.body || ""));
    const isDraft = Boolean(pr.draft);

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

    return {
      number: pr.number,
      title: pr.title || "Untitled",
      url: pr.html_url || "",
      action: chooseAction({
        reviewability,
        isDraft,
        totalDiff,
        changedFiles,
      }),
      reviewability,
      risk,
      rawRisk,
      signals,
      flags,
      scoreBreakdown,
    };
  }

  function chooseAction({ reviewability, isDraft, totalDiff, changedFiles }) {
    if (isDraft) {
      return "wait for author";
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
        return analyzePullRequest(detail, files);
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
    const total = items.length;
    const reviewNow = items.filter((item) => item.action === "review now").length;
    const followUp = items.filter((item) => item.action !== "review now").length;
    const average = total
      ? Math.round(items.reduce((sum, item) => sum + item.reviewability, 0) / total)
      : 0;

    document.querySelector("#metric-total").textContent = String(total);
    document.querySelector("#metric-review").textContent = String(reviewNow);
    document.querySelector("#metric-followup").textContent = String(followUp);
    document.querySelector("#metric-score").textContent = String(average);

    const body = document.querySelector("#queue-body");
    if (!body) {
      return;
    }
    if (!items.length) {
      body.innerHTML = `<tr><td colspan="5">No open pull requests found for ${escapeHtml(repository)}.</td></tr>`;
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
    if (!form || !input || !button) {
      return;
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const repository = normalizeRepository(input.value);
      if (!repository) {
        setStatus("Enter a repository as owner/repo.");
        return;
      }

      button.disabled = true;
      setStatus(`Scanning ${repository} with public GitHub API data.`);
      try {
        const items = await fetchPreview(repository);
        renderPreview(items, repository);
        setStatus(
          `Scanned ${items.length} recent open PRs from ${repository}. CLI scans can include richer CI and review context.`
        );
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Scan failed.");
      } finally {
        button.disabled = false;
      }
    });
  }

  const api = {
    analyzePullRequest,
    chooseAction,
    formatImpact,
    normalizeRepository,
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
