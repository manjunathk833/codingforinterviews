    /* ========================================================================
       LOCAL IDE WORKBENCH (WAVE 2 MULTI-FILE CAPSTONE + 17 BLANK-CANVAS BUILDS)
       ======================================================================== */
    function switchWorkbenchMode(mode) {
      state.workbenchSubmode = mode;
      document.getElementById('wb-pane-frameworks').classList.toggle('hidden', mode !== 'frameworks');
      document.getElementById('wb-pane-interviews').classList.toggle('hidden', mode !== 'interviews');
      document.getElementById('wb-mode-frameworks').classList.toggle('active', mode === 'frameworks');
      document.getElementById('wb-mode-interviews').classList.toggle('active', mode === 'interviews');
      if (state.activeView === 'workbench') {
        document.getElementById('tab-btn-workbench').classList.toggle('active', mode === 'frameworks');
        document.getElementById('tab-btn-interviews').classList.toggle('active', mode === 'interviews');
      }
    }

    function filterWorkbenchChallenges(group) {
      state.activeWorkbenchGroup = group || 'all';
      ['all', 'capstone', 'ui-api', 'design', 'infra-sdet'].forEach(g => {
        const btn = document.getElementById('wb-filter-' + g);
        if (btn) btn.classList.toggle('active', g === state.activeWorkbenchGroup);
      });
      const all = state.workbenchChallenges || [];
      const filtered = state.activeWorkbenchGroup === 'all'
        ? all
        : all.filter(ch => ch.group === state.activeWorkbenchGroup);
      const sel = document.getElementById('wb-challenge-select');
      if (!sel) return;
      sel.innerHTML = filtered.map(ch =>
        `<option value="${escapeHtml(ch.id)}">${escapeHtml(ch.title)} · [${escapeHtml(ch.workspacePath.split('/').slice(-2).join('/'))}]</option>`
      ).join('');
      if (filtered.length) {
        const keep = filtered.find(c => c.id === state.activeWorkbenchChallengeId);
        selectWorkbenchChallenge(keep ? keep.id : filtered[0].id);
      }
    }

    function getActiveWorkbenchChallenge() {
      return (state.workbenchChallenges || []).find(c => c.id === state.activeWorkbenchChallengeId) || null;
    }

    function renderWorkbenchCheckpointCards(checkpoints) {
      const grid = document.getElementById('wb-checkpoints-grid');
      if (!grid) return;
      grid.innerHTML = (checkpoints || []).map((cp, idx) => {
        const pending = cp.passed === undefined || cp.passed === null;
        const ok = cp.passed === true;
        const badgeBg = pending
          ? 'var(--bg-card)'
          : (ok ? 'var(--accent-sage-soft)' : 'var(--accent-terra-soft)');
        const badgeColor = pending
          ? 'var(--ink-muted)'
          : (ok ? 'var(--accent-sage)' : 'var(--accent-terra)');
        const statusTxt = pending ? '○ Pending' : (ok ? `✓ Passed (${cp.durationMs || 0}ms)` : '✗ Failed');
        return `
          <div class="rounded-lg p-2.5 space-y-1" style="background: var(--bg-subtle); border: 1px solid var(--border-warm);">
            <div class="flex items-center justify-between gap-2">
              <strong class="text-xs" style="color: var(--ink-primary);">${idx + 1}. ${escapeHtml(cp.title)}</strong>
              <span class="mono text-[10.5px] font-semibold px-2 py-0.5 rounded" style="background: ${badgeBg}; color: ${badgeColor};">${statusTxt}</span>
            </div>
            <p class="text-[11px]" style="color: var(--ink-secondary); margin: 0;">${escapeHtml(cp.description || '')}</p>
            ${cp.detail ? `<div class="mono text-[10.5px] pt-0.5 break-all" style="color: ${ok ? 'var(--accent-sage)' : 'var(--accent-terra)'};">${escapeHtml(cp.detail)}</div>` : ''}
          </div>
        `;
      }).join('');
    }

    function resetWorkbenchReviewCard() {
      const scoreEl = document.getElementById('wb-arch-score-title');
      const verdEl = document.getElementById('wb-arch-verdict');
      const cpEl = document.getElementById('wb-arch-cp-pts');
      const ctEl = document.getElementById('wb-arch-contract-pts');
      const clEl = document.getElementById('wb-arch-clean-pts');
      const tipsEl = document.getElementById('wb-arch-tips');
      const refWrap = document.getElementById('wb-ref-wrap');
      const refPre = document.getElementById('wb-ref-pre');
      if (scoreEl) scoreEl.textContent = '🏛️ AST Architecture Reviewer: Ready';
      if (verdEl) {
        verdEl.textContent = '0-Pass Strictly Gated at 0/100';
        verdEl.style.color = 'var(--ink-secondary)';
      }
      if (cpEl) cpEl.textContent = 'Checkpoints: --/60';
      if (ctEl) ctEl.textContent = 'Contract & Types: --/20';
      if (clEl) clEl.textContent = 'Cleanliness: --/20';
      if (tipsEl) tipsEl.innerHTML = '<li>Implement the blank contract above (or click <strong>↗ Open in VS Code</strong>) and run the 4 black-box checkpoints.</li>';
      if (refWrap) refWrap.classList.add('hidden');
      if (refPre) refPre.classList.add('hidden');
    }

    function selectWorkbenchChallenge(challengeId) {
      const ch = (state.workbenchChallenges || []).find(c => c.id === challengeId);
      if (!ch) return;
      state.activeWorkbenchChallengeId = ch.id;
      state.wbIsDirty = false;
      const sel = document.getElementById('wb-challenge-select');
      if (sel && sel.value !== ch.id) sel.value = ch.id;

      const vsLink = document.getElementById('wb-open-vscode-link');
      if (vsLink) vsLink.href = ch.vscodeUri || '#';

      const catPill = document.getElementById('wb-ch-category-pill');
      if (catPill) catPill.textContent = ch.category;
      const pathLbl = document.getElementById('wb-ch-path-label');
      if (pathLbl) pathLbl.textContent = ch.workspacePath;
      const titleEl = document.getElementById('wb-ch-title');
      if (titleEl) titleEl.textContent = ch.title;
      const promptEl = document.getElementById('wb-ch-prompt');
      if (promptEl) promptEl.textContent = ch.prompt;
      const symEl = document.getElementById('wb-ch-symbols');
      if (symEl) symEl.textContent = (ch.contractSymbols || []).join(', ');

      const ed = document.getElementById('wb-code-editor');
      if (ed) ed.value = ch.code || '';
      const syncEl = document.getElementById('wb-disk-sync-status');
      if (syncEl) {
        syncEl.textContent = `✓ Synced · ${ch.workspacePath} (${(ch.sha256 || '').slice(0, 7)})`;
        syncEl.style.color = 'var(--accent-sage)';
      }

      renderWorkbenchCheckpointCards((ch.checkpointLabels || []).map(cp => ({ ...cp, passed: null })));
      resetWorkbenchReviewCard();
    }

    function handleWorkbenchEditorInput() {
      const ch = getActiveWorkbenchChallenge();
      const ed = document.getElementById('wb-code-editor');
      const syncEl = document.getElementById('wb-disk-sync-status');
      if (!ch || !ed) return;
      ch.code = ed.value;
      state.wbIsDirty = true;
      if (syncEl) {
        syncEl.textContent = `● Unsaved buffer · ${ch.workspacePath} (saved on ▶ Run)`;
        syncEl.style.color = 'var(--accent-terra)';
      }
    }

    function injectWorkbenchOutline() {
      const ch = getActiveWorkbenchChallenge();
      const ed = document.getElementById('wb-code-editor');
      if (!ch || !ed) return;
      const steps = ch.outlineSteps || [];
      if (!steps.length) return;
      const rawComments = steps.map((s, i) => `# Architecture Step ${i + 1}: ${s}`).join('\n');
      if (ed.value.includes('# Architecture Step 1:')) return;
      const lines = ed.value.split('\n');
      const idx = lines.findIndex(ln => ln.includes('NotImplementedError'));
      if (idx !== -1) {
        const indent = (lines[idx].match(/^(\s*)/) || ['', '    '])[1];
        const block = steps.map((s, i) => `${indent}# Architecture Step ${i + 1}: ${s}`).join('\n');
        lines.splice(idx, 0, block);
        ed.value = lines.join('\n');
      } else {
        ed.value = rawComments + '\n\n' + ed.value;
      }
      handleWorkbenchEditorInput();
    }

    async function resetActiveWorkbenchChallenge() {
      const ch = getActiveWorkbenchChallenge();
      if (!ch) return;
      const btn = document.getElementById('wb-reset-btn');
      if (btn) btn.textContent = '⏳ Resetting...';
      try {
        const res = await fetch('/api/workbench/challenge/reset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ challengeId: ch.id })
        });
        if (res.ok) {
          const data = await res.json();
          ch.code = data.code;
          ch.sha256 = data.sha256;
          selectWorkbenchChallenge(ch.id);
        }
      } catch (_) {}
      if (btn) btn.textContent = '↺ Reset Blank';
    }

    async function runActiveWorkbenchChallenge() {
      const ch = getActiveWorkbenchChallenge();
      const ed = document.getElementById('wb-code-editor');
      if (!ch || !ed) return;
      const btn = document.getElementById('wb-run-challenge-btn');
      if (btn) btn.textContent = '⏳ Running 4 Checkpoints...';
      try {
        const res = await fetch('/api/workbench/challenge/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            challengeId: ch.id,
            code: ed.value,
            persist: true
          })
        });
        if (res.ok) {
          const data = await res.json();
          state.wbIsDirty = false;
          if (data.sha256) ch.sha256 = data.sha256;
          const syncEl = document.getElementById('wb-disk-sync-status');
          if (syncEl) {
            syncEl.textContent = `✓ Saved & Verified · ${ch.workspacePath} (${(ch.sha256 || '').slice(0, 7)})`;
            syncEl.style.color = 'var(--accent-sage)';
          }
          renderWorkbenchCheckpointCards(data.checkpoints || []);
          const rev = data.architectureReview || {};
          const scoreEl = document.getElementById('wb-arch-score-title');
          const verdEl = document.getElementById('wb-arch-verdict');
          const cpEl = document.getElementById('wb-arch-cp-pts');
          const ctEl = document.getElementById('wb-arch-contract-pts');
          const clEl = document.getElementById('wb-arch-clean-pts');
          const tipsEl = document.getElementById('wb-arch-tips');
          const refWrap = document.getElementById('wb-ref-wrap');
          const refPre = document.getElementById('wb-ref-pre');

          if (scoreEl) scoreEl.textContent = `🏛️ Architecture Score: ${rev.score ?? 0} / 100`;
          if (verdEl) {
            verdEl.textContent = rev.verdict || data.status;
            verdEl.style.color = (rev.score || 0) >= 90 ? 'var(--accent-sage)' : 'var(--accent-terra)';
          }
          if (cpEl) cpEl.textContent = `✓ Checkpoints: ${rev.checkpointPts ?? 0}/60`;
          if (ctEl) ctEl.textContent = `📐 Contract & Types: ${rev.contractPts ?? 0}/20`;
          if (clEl) clEl.textContent = `✨ Cleanliness: ${rev.cleanlinessPts ?? 0}/20`;
          if (tipsEl) {
            tipsEl.innerHTML = (rev.tips || []).map(t => `<li>${escapeHtml(t)}</li>`).join('');
          }
          if (data.referenceSolution && refWrap && refPre) {
            refPre.textContent = data.referenceSolution;
            refWrap.classList.remove('hidden');
          } else if (refWrap) {
            refWrap.classList.add('hidden');
          }
        }
      } catch (_) {}
      if (btn) btn.textContent = '▶ Run 4 Checkpoints & AST Review';
    }

    function toggleWorkbenchReference() {
      const refPre = document.getElementById('wb-ref-pre');
      if (refPre) refPre.classList.toggle('hidden');
    }

    function openActiveWorkbenchTextbook() {
      const ch = getActiveWorkbenchChallenge();
      if (ch && ch.relatedChapter) openTextbookChapter(ch.relatedChapter);
    }

    async function loadWorkbenchAndInterviews() {
      try {
        const chRes = await fetch('/api/workbench/challenges');
        if (chRes.ok) {
          const chData = await chRes.json();
          state.workbenchChallenges = chData.challenges || [];
          filterWorkbenchChallenges(state.activeWorkbenchGroup || 'all');
        }
      } catch (_) {}

      try {
        const wbRes = await fetch('/api/workbench/catalog');
        if (wbRes.ok) {
          const data = await wbRes.json();
          const grid = document.getElementById('workbench-items-grid');
          grid.innerHTML = (data.items || []).map(item => {
            const last = item.lastRun;
            const isDone = Boolean(item.completed || (last && last.status === 'PASS'));
            return `
              <div class="track-card flex flex-col justify-between space-y-4">
                <div class="space-y-2">
                  <div class="flex items-center justify-between gap-2">
                    <span class="archetype-pill" style="background: var(--bg-subtle); color: var(--accent-blue);">${escapeHtml(item.category)}</span>
                    <div class="flex items-center gap-2">
                      <span class="mono text-[11px]" style="color: var(--ink-muted);">${escapeHtml(item.stack)}</span>
                      <button
                        onclick="toggleRoadmapItemDone('${item.id}')"
                        class="mark-done-btn ${isDone ? 'completed' : ''}"
                        style="padding: 3px 9px; font-size: 0.69rem;"
                        title="Mark this Workbench Lab as Done in your Staff SDET Roadmap"
                      >
                        ${isDone ? '✓ Completed' : '○ Mark Done'}
                      </button>
                    </div>
                  </div>
                  <h4 style="font-size: 1.1rem; font-weight: 700;">${escapeHtml(item.title)}</h4>
                  <p class="text-xs leading-relaxed" style="color: var(--ink-secondary);">${escapeHtml(item.invariant)}</p>
                  <div class="news-card mono text-[11px] break-all" style="padding: 10px 12px;">
                    <div style="color: var(--accent-sage); font-weight: 600;">${escapeHtml(item.folderPath)}</div>
                    <div class="mt-0.5" style="color: var(--ink-secondary);">$ ${escapeHtml(item.cliDisplay)}</div>
                  </div>
                </div>
                <div class="flex flex-wrap items-center justify-between gap-2 pt-2" style="border-top: 1px solid var(--border-warm);">
                  ${item.relatedChapter ? `
                    <button onclick="openTextbookChapter('${item.relatedChapter}')" class="mono text-[11px] font-semibold hover:underline" style="color: var(--accent-sage);">
                      📖 Textbook Theory →
                    </button>
                  ` : '<span></span>'}
                  <div class="flex flex-wrap items-center gap-2">
                    ${last ? `<span class="mono px-2 py-0.5 rounded text-[10px] font-semibold" style="background: var(--bg-subtle); color: ${last.status === 'PASS' ? 'var(--accent-sage)' : 'var(--accent-crimson)'};">${last.status} (${last.durationMs}ms)</span>` : ''}
                    <button
                      onclick="toggleRoadmapItemDone('${item.id}')"
                      class="mark-done-btn ${isDone ? 'completed' : ''}"
                      title="Mark or unmark this Workbench Lab as Done in your Staff SDET Roadmap"
                    >
                      ${isDone ? '✓ Lab Completed' : '○ Mark Lab Done'}
                    </button>
                    <button onclick="verifyWorkbenchItem('${item.id}')" id="wb-btn-${item.id}" class="btn-primary" style="background: var(--accent-blue);">
                      ▶ Verify Locally (Zero AI)
                    </button>
                  </div>
                </div>
              </div>
            `;
          }).join('');
        }
      } catch (_) {}

      try {
        const miRes = await fetch('/api/interviews/session?id=interview-1');
        if (miRes.ok) {
          state.interviewSession = await miRes.json();
          document.getElementById('mi-session-title').textContent = state.interviewSession.title;
          document.getElementById('mi-status-pill').textContent = `${state.interviewSession.status} · ${state.interviewSession.overallScore}`;
          const miDoneBtn = document.getElementById('mi-mark-done-btn');
          if (miDoneBtn) {
            miDoneBtn.classList.toggle('completed', Boolean(state.interviewSession.completed));
            miDoneBtn.textContent = state.interviewSession.completed ? '✓ Completed' : '○ Mark Done';
          }
          switchInterviewDocTab('questions');
          loadSelectedInterviewQuestionResponse();

          document.getElementById('mi-related-chapters').innerHTML = (state.interviewSession.relatedChapters || []).map(slug => `
            <button onclick="openTextbookChapter('${slug}')" class="w-full text-left news-card mono text-xs font-semibold" style="padding: 9px 12px; color: var(--accent-sage);">
              📖 ${escapeHtml(slug)} →
            </button>
          `).join('');
        }
      } catch (_) {}
      renderRoadmapEverywhere();
    }

    async function verifyWorkbenchItem(itemId) {
      const btn = document.getElementById('wb-btn-' + itemId);
      if (btn) btn.textContent = '⏳ Running...';
      try {
        const res = await fetch('/api/workbench/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ itemId })
        });
        if (res.ok) {
          const data = await res.json();
          const box = document.getElementById('workbench-console-box');
          box.classList.remove('hidden');
          document.getElementById('workbench-console-title').textContent = `${data.status === 'PASS' ? '✓' : '✗'} ${data.title}`;
          document.getElementById('workbench-console-meta').textContent = `${data.status} · ${data.durationMs}ms (Exit ${data.exitCode})`;
          document.getElementById('workbench-console-output').textContent = data.output || '';
          await loadWorkbenchAndInterviews();
          await loadTracksAndHome();
          await loadRoadmapStatus();
        }
      } catch (_) {}
      if (btn) btn.textContent = '▶ Verify Locally (Zero AI)';
    }

    function switchInterviewDocTab(tab) {
      state.interviewActiveDoc = tab;
      document.getElementById('mi-tab-questions').classList.toggle('active', tab === 'questions');
      document.getElementById('mi-tab-evaluation').classList.toggle('active', tab === 'evaluation');
      if (!state.interviewSession) return;
      const md = tab === 'questions'
        ? state.interviewSession.questionsMarkdown
        : state.interviewSession.evaluationMarkdown;
      document.getElementById('mi-doc-viewer').innerHTML = renderEditorialMarkdown(md);
    }

    function loadSelectedInterviewQuestionResponse() {
      if (!state.interviewSession) return;
      const qid = document.getElementById('mi-question-select').value;
      const saved = (state.interviewSession.candidateResponses || {})[qid] || '';
      document.getElementById('mi-response-textarea').value = saved;
    }

    async function saveInterviewDraft() {
      const qid = document.getElementById('mi-question-select').value;
      const text = document.getElementById('mi-response-textarea').value;
      const statusEl = document.getElementById('mi-save-status');
      statusEl.textContent = '⏳ Saving...';
      try {
        const res = await fetch('/api/interviews/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sessionId: 'interview-1', questionId: qid, response: text })
        });
        if (res.ok) {
          const data = await res.json();
          if (state.interviewSession) state.interviewSession.candidateResponses = data.candidateResponses;
          statusEl.textContent = `✓ Saved ${qid.toUpperCase()} to SQLite`;
        }
      } catch (_) {}
    }
