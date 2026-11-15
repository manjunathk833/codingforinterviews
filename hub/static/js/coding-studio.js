    /* ========================================================================
       BANKED DSA MILESTONES 1–4 (15-CH ROADMAP, 50/50 STUDIO & 3D VISUALIZER)
       ======================================================================== */
    function renderRoadmapSpineAndChapter(chapterIdx) {
      state.activeChapterIdx = chapterIdx;
      const chapters = state.chapters || FALLBACK_CHAPTERS;
      const activeCh = chapters[chapterIdx] || chapters[0];

      const spineEl = document.getElementById('roadmap-chapter-spine');
      spineEl.innerHTML = chapters.map((ch, idx) => {
        const isActive = idx === chapterIdx;
        if (isActive) {
          return `
            <div onclick="renderRoadmapSpineAndChapter(${idx})" class="p-3 rounded-lg bg-[#F3EDE2] border-l-4 border-[#C85A32] space-y-1 cursor-pointer transition">
              <div class="font-bold text-xs">${ch.title}</div>
              <span class="mono inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[#C85A32] text-white">
                ${ch.done}/${ch.total} Mastered
              </span>
            </div>
          `;
        }
        return `
          <div onclick="renderRoadmapSpineAndChapter(${idx})" class="p-2.5 rounded-lg flex justify-between items-center text-xs hover:bg-[#F3EDE2] cursor-pointer transition" style="color: var(--ink-secondary);">
            <span class="truncate pr-2"><strong>Ch ${ch.number}:</strong> ${ch.pattern}</span>
            <span class="mono bg-[#F3EDE2] px-2 py-0.5 rounded-full text-[10px] shrink-0">${ch.done}/${ch.total}</span>
          </div>
        `;
      }).join('');

      document.getElementById('roadmap-banner-tag').textContent = `CHAPTER ${activeCh.number} · ${activeCh.pattern.toUpperCase()}`;
      document.getElementById('roadmap-banner-title').textContent = activeCh.mentalModelTitle;
      document.getElementById('roadmap-banner-summary').textContent = activeCh.mentalModelSummary || '';

      document.getElementById('roadmap-banner-tiles').innerHTML = (activeCh.tiles || []).map(t => `
        <div class="bg-white rounded-xl p-3 border border-[#E6DEC8] text-center shadow-sm min-w-[72px]">
          <div class="wood-tile px-2.5 h-9 mx-auto rounded-lg bg-[#D7B38C] font-bold flex items-center justify-center mb-1.5 text-zinc-900">
            ${t.label}
          </div>
          <div class="text-[11px] font-bold" style="color: var(--accent-sage);">${t.sub}</div>
        </div>
      `).join('');

      document.getElementById('roadmap-grid-heading').textContent = `${activeCh.title} (${activeCh.problems.length} Stepping Stones)`;

      document.getElementById('roadmap-problems-grid').innerHTML = (activeCh.problems || []).map(p => {
        const numStr = String(p.id).padStart(3, '0');
        const targetSlug = p.folderSlug || `${numStr}-${p.slug}`;
        const dsaItemId = `dsa-${numStr}`;
        const rmCompleted = Boolean(state.roadmap && state.roadmap.completedMap && state.roadmap.completedMap[dsaItemId]);
        const isMastered = Boolean(p.bothDone || rmCompleted);
        const isScaffolded = p.hasLocalFiles;

        const badgeHtml = isMastered
          ? `<span class="archetype-pill" style="background:#E6F4F0; color:#1E6F5C;">Mastered ✓</span>`
          : isScaffolded
            ? `<span class="archetype-pill" style="background:#FEF3C7; color:#92400E;">In Studio · Ready</span>`
            : `<span class="archetype-pill">⚡ 1-Click Scaffold</span>`;

        const borderStyle = (!isMastered && isScaffolded) ? 'border: 1.5px solid var(--accent-terra);' : '';

        return `
          <div onclick="openOrScaffoldProblem(${p.id}, '${targetSlug}', ${isScaffolded})" class="track-card flex flex-col justify-between space-y-3.5 cursor-pointer" style="padding: 16px; ${borderStyle}">
            <div class="space-y-2">
              <div class="flex items-start justify-between gap-2">
                <div class="font-bold text-sm leading-snug">${numStr}. ${p.title}</div>
                <span class="tag shrink-0">${p.difficulty}</span>
              </div>
              <div class="flex items-center justify-between gap-2">
                ${badgeHtml}
                <button
                  onclick="event.stopPropagation(); toggleRoadmapItemDone('${dsaItemId}')"
                  class="mark-done-btn ${isMastered ? 'completed' : ''}"
                  style="padding: 2px 8px; font-size: 0.68rem;"
                  title="Mark Problem #${numStr} as Done in your Staff SDET Roadmap"
                >
                  ${isMastered ? '✓ Done' : '○ Mark Done'}
                </button>
              </div>
              <div class="flex gap-1.5 text-[11px] mono pt-0.5">
                <span class="px-2 py-0.5 rounded ${p.pyDone ? 'bg-[#E6F4F0] text-[#1E6F5C] font-semibold' : 'bg-[#F3EDE2] text-[#5C554E]'}">Python ${p.pyDone ? '✓' : '○'}</span>
                <span class="px-2 py-0.5 rounded ${p.javaDone ? 'bg-[#E6F4F0] text-[#1E6F5C] font-semibold' : 'bg-[#F3EDE2] text-[#5C554E]'}">Java ${p.javaDone ? '✓' : '○'}</span>
              </div>
            </div>
            <div class="news-card text-center text-[11px] mono" style="padding: 10px;">
              <div class="font-semibold mb-0.5 truncate" style="color: var(--ink-primary);">${p.diagramFormula || 'O(1) Invariant'}</div>
              <div class="text-[10px]" style="color: var(--ink-muted);">${p.diagramCaption || activeCh.pattern}</div>
            </div>
          </div>
        `;
      }).join('');
    }

    async function openOrScaffoldProblem(problemId, slug, isScaffolded) {
      state.activeProblemId = problemId;
      if (!isScaffolded) {
        try {
          const res = await fetch('/api/dsa/scaffold', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ problemId, slug })
          });
          if (res.ok) {
            const data = await res.json();
            await refreshDashboardState();
            if (data.problem && data.problem.slug) return openProblemWorkspace(data.problem.slug);
          }
        } catch (_) {}
      }
      return openProblemWorkspace(slug);
    }

    function updateEditorLineNumbers() {
      const editor = document.getElementById('ws-code-editor');
      const gutter = document.getElementById('editor-line-gutter');
      if (!editor || !gutter) return;
      const linesCount = (editor.value || '').split('\n').length || 1;
      const nums = [];
      for (let i = 1; i <= linesCount; i++) nums.push(i);
      gutter.textContent = nums.join('\n');
    }

    function syncEditorGutterScroll() {
      const editor = document.getElementById('ws-code-editor');
      const gutter = document.getElementById('editor-line-gutter');
      if (editor && gutter) gutter.scrollTop = editor.scrollTop;
    }

    function handleEditorInput() {
      state.isDirty = true;
      updateEditorLineNumbers();
      const fileObj = state.files[state.activeLang];
      if (fileObj) {
        fileObj.content = document.getElementById('ws-code-editor').value;
        const statusEl = document.getElementById('editor-disk-status');
        statusEl.textContent = `● Unsaved edits · ${fileObj.path}`;
        statusEl.className = 'text-[11px] mono px-2.5 py-1 rounded-md';
        statusEl.style.background = 'var(--accent-terra-soft)';
        statusEl.style.color = 'var(--accent-terra)';
        statusEl.style.borderColor = 'var(--accent-terra)';
      }
    }

    function attachSmartEditorKeybindings() {
      const editor = document.getElementById('ws-code-editor');
      if (!editor) return;
      editor.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
          e.preventDefault();
          const start = editor.selectionStart;
          const end = editor.selectionEnd;
          editor.value = editor.value.substring(0, start) + '    ' + editor.value.substring(end);
          editor.selectionStart = editor.selectionEnd = start + 4;
          handleEditorInput();
        }
      });
    }

    async function pollActiveDiskFile() {
      if (state.activeView === 'workbench' && typeof getActiveWorkbenchChallenge === 'function') {
        const ch = getActiveWorkbenchChallenge();
        if (!ch || !ch.workspacePath || state.wbIsDirty) return;
        try {
          const stRes = await fetch(`/api/fs/stat?path=${encodeURIComponent(ch.workspacePath)}`);
          if (!stRes.ok) return;
          const st = await stRes.json();
          if (st.sha256 && st.sha256 !== ch.sha256 && !state.wbIsDirty) {
            const fRes = await fetch(`/api/fs/file?path=${encodeURIComponent(ch.workspacePath)}`);
            if (fRes.ok) {
              const fData = await fRes.json();
              ch.code = fData.content;
              ch.sha256 = fData.sha256;
              const ed = document.getElementById('wb-code-editor');
              if (ed) ed.value = fData.content;
              const syncEl = document.getElementById('wb-disk-sync-status');
              if (syncEl) syncEl.textContent = `↻ Synced from VS Code · ${ch.workspacePath} (${fData.sha256.slice(0, 7)})`;
            }
          }
        } catch (_) {}
        return;
      }
      if (state.activeView !== 'workspace') return;
      const fileObj = state.files[state.activeLang];
      if (!fileObj || !fileObj.path || fileObj.sha256 === 'local') return;
      try {
        const res = await fetch(`/api/fs/stat?path=${encodeURIComponent(fileObj.path)}`);
        if (!res.ok) return;
        const stat = await res.json();
        if (stat.sha256 && stat.sha256 !== fileObj.sha256 && !state.isDirty) {
          const fullRes = await fetch(`/api/fs/file?path=${encodeURIComponent(fileObj.path)}`);
          if (fullRes.ok) {
            const fullData = await fullRes.json();
            fileObj.content = fullData.content;
            fileObj.sha256 = fullData.sha256;
            document.getElementById('ws-code-editor').value = fullData.content;
            updateEditorLineNumbers();
            document.getElementById('editor-disk-status').textContent = `↻ Synced from IDE · ${fileObj.path} (${fullData.sha256.slice(0, 7)})`;
          }
        }
      } catch (_) {}
    }

    function switchLeftTab(tabName) {
      ['problem', 'hints', 'walkthrough'].forEach(t => {
        document.getElementById('left-pane-' + t).classList.toggle('hidden', t !== tabName);
        const btn = document.getElementById('left-tab-' + t);
        if (btn) btn.classList.toggle('active', t === tabName);
      });
    }

    async function openProblemWorkspace(slug, switchScreen = true) {
      state.activeSlug = slug;
      state.activeWarmupId = null;
      state.helpStartClicks = 0;
      state.lastReferencePython = null;
      const warmupSel = document.getElementById('ws-warmup-select');
      if (warmupSel) warmupSel.value = '';
      resetHelpMeStartBanner();
      resetInvariantVisibility();
      resetCodeCoachCard();
      state.unlockedHintTier = 1;
      state.isDirty = false;
      if (switchScreen) showView('workspace');

      ['001-two-sum', '002-valid-anagram', '003-group-anagrams', '004-longest-consecutive-sequence', '005-top-k-frequent-elements'].forEach(s => {
        const pill = document.getElementById('prob-pill-' + s);
        if (pill) pill.classList.toggle('active', s === slug);
      });

      const fb = FALLBACK_PROBLEMS[slug] || FALLBACK_PROBLEMS['003-group-anagrams'];
      let probMeta = fb;
      state.files.python = { path: `dsa/01-arrays-and-hashing/${slug}/solution.py`, content: fb.pythonCode, sha256: 'local' };
      state.files.java = { path: `dsa/01-arrays-and-hashing/${slug}/Solution.java`, content: fb.javaCode, sha256: 'local' };
      state.cases = fb.cases;

      try {
        const res = await fetch(`/api/dsa/problem?slug=${encodeURIComponent(slug)}`);
        if (res.ok) {
          const data = await res.json();
          probMeta = data.problem || fb;
          if (data.files && data.files.python) state.files.python = data.files.python;
          if (data.files && data.files.java) state.files.java = data.files.java;
          if (probMeta.cases && probMeta.cases.length) {
            state.cases = probMeta.cases.map(c => ({ ...c, passed: null, actual: '(click ▶ Run & Coach to execute)', durationMs: 0.0 }));
          }
        }
      } catch (_) {}

      state.activeProblemMeta = probMeta;
      if (probMeta && probMeta.id) {
        state.activeProblemId = Number(probMeta.id);
      } else {
        for (let cIdx = 0; cIdx < (state.chapters || []).length; cIdx++) {
          const matchP = (state.chapters[cIdx].problems || []).find(pr => pr.folderSlug === slug || pr.slug === slug);
          if (matchP && matchP.id) {
            state.activeProblemId = Number(matchP.id);
            break;
          }
        }
      }
      state.activeVisualizerId = probMeta.visualizerId || 'dsa-group-anagrams';
      document.getElementById('ws-breadcrumb-chapter').textContent = `← ${probMeta.chapter || 'Ch 01: Arrays & Hashing'}`;
      document.getElementById('ws-breadcrumb-title').textContent = probMeta.title || slug;
      document.getElementById('ws-problem-title').textContent = probMeta.title || slug;
      document.getElementById('ws-problem-prompt').textContent = probMeta.prompt || '';
      document.getElementById('ws-problem-invariant').textContent = probMeta.invariant || '';
      document.getElementById('ws-difficulty-badge').textContent = probMeta.difficulty || 'Medium';
      document.getElementById('ws-complexity-summary').textContent =
        `Time: ${probMeta.timeComplexity || 'O(N)'} · Space: ${probMeta.spaceComplexity || 'O(N)'}`;

      state.currentHints = probMeta.hints || fb.hints;
      renderHints(state.currentHints);
      switchEditorLang(state.activeLang, false);
      renderCasePills();
      selectTestCaseIndex(0);

      const firstInput = state.cases[0] ? state.cases[0].input : null;
      if (firstInput) document.getElementById('viz-custom-input').value = JSON.stringify(firstInput);
      renderRoadmapEverywhere();
      await loadVisualizerTrace(state.activeVisualizerId, firstInput);
    }

    async function loadWarmupDrills() {
      try {
        const res = await fetch('/api/dsa/warmups');
        if (!res.ok) return;
        const data = await res.json();
        state.warmupDrills = data.warmups || [];
        const sel = document.getElementById('ws-warmup-select');
        if (sel) {
          sel.innerHTML = `<option value="">🥋 5-Min Warmup Drills (12 Templates)</option>` +
            state.warmupDrills.map(d => `<option value="${d.id}">${d.title} (~${d.minutes}m)</option>`).join('');
        }
      } catch (_) {}
    }

    function selectWarmupDrill(drillId) {
      if (!drillId) {
        state.activeWarmupId = null;
        return openProblemWorkspace(state.activeSlug || '003-group-anagrams', false);
      }
      const drill = (state.warmupDrills || []).find(d => d.id === drillId);
      if (!drill) return;
      state.activeWarmupId = drill.id;
      state.helpStartClicks = 0;
      state.lastReferencePython = null;
      resetHelpMeStartBanner();
      resetCodeCoachCard();

      document.getElementById('ws-breadcrumb-title').textContent = `🥋 Warmup · ${drill.title}`;
      document.getElementById('ws-problem-title').textContent = drill.title;
      document.getElementById('ws-problem-prompt').textContent = drill.goal;
      document.getElementById('ws-problem-invariant').textContent = drill.firstLine;
      document.getElementById('ws-difficulty-badge').textContent = `${drill.minutes}m Drill`;

      state.activeLang = 'python';
      document.getElementById('lang-tab-python').classList.add('active');
      document.getElementById('lang-tab-java').classList.remove('active');
      const ed = document.getElementById('ws-code-editor');
      ed.value = drill.starterPy;
      updateEditorLineNumbers();
      document.getElementById('editor-disk-status').textContent = `🥋 Drill Mode · In-Memory Sandbox`;

      state.cases = (drill.cases || []).map((c, idx) => ({
        id: `drill-c${idx + 1}`, label: `Drill ${idx + 1}`, input: c.input, expected: c.expected, actual: '(click ▶ Run & Coach to execute)', passed: null, durationMs: 0.0
      }));
      renderCasePills();
      selectTestCaseIndex(0);
    }

    function resetInvariantVisibility() {
      const invEl = document.getElementById('ws-problem-invariant');
      const btn = document.getElementById('ws-invariant-toggle-btn');
      if (invEl) invEl.classList.add('hidden');
      if (btn) btn.textContent = '🔒 Reveal Invariant';
    }

    function toggleProblemInvariant(forceShow) {
      const invEl = document.getElementById('ws-problem-invariant');
      const btn = document.getElementById('ws-invariant-toggle-btn');
      if (!invEl) return;
      const shouldShow = typeof forceShow === 'boolean' ? forceShow : invEl.classList.contains('hidden');
      invEl.classList.toggle('hidden', !shouldShow);
      if (btn) btn.textContent = shouldShow ? '🙈 Hide Invariant' : '🔒 Reveal Invariant';
    }

    function resetHelpMeStartBanner() {
      const b = document.getElementById('ws-first-line-banner');
      const btn = document.getElementById('ws-help-start-btn');
      if (b) b.classList.add('hidden');
      if (btn) btn.textContent = '⚡ Help Me Start';
    }

    function injectOutlineNonDestructively(currentCode, rawComments, lang) {
      const firstLine = (rawComments || '').split('\n')[0] || '';
      if (!rawComments || (firstLine && currentCode.includes(firstLine))) {
        return currentCode;
      }
      const lines = (currentCode || '').split('\n');
      const marker = lang === 'java' ? 'UnsupportedOperationException' : 'NotImplementedError';
      const idx = lines.findIndex(ln => ln.includes(marker));
      if (idx !== -1) {
        const indentMatch = lines[idx].match(/^(\s*)/);
        const indent = indentMatch ? indentMatch[1] : '        ';
        const indentedBlock = rawComments.split('\n').map(c => indent + c).join('\n');
        lines.splice(idx, 0, indentedBlock);
        return lines.join('\n');
      }
      if (lang === 'python') {
        const defIdx = lines.findIndex(ln => /^\s*def\s+(?!__init__)/.test(ln));
        if (defIdx !== -1) {
          const baseIndent = (lines[defIdx].match(/^(\s*)/) || ['', '    '])[1] + '    ';
          const indentedBlock = rawComments.split('\n').map(c => baseIndent + c).join('\n');
          lines.splice(defIdx + 1, 0, indentedBlock);
          return lines.join('\n');
        }
      } else {
        const sigIdx = lines.findIndex(ln => /public\s+(?!class\b|static\s+void\s+main)/.test(ln) && ln.includes('{'));
        if (sigIdx !== -1) {
          const baseIndent = (lines[sigIdx].match(/^(\s*)/) || ['', '    '])[1] + '    ';
          const indentedBlock = rawComments.split('\n').map(c => baseIndent + c).join('\n');
          lines.splice(sigIdx + 1, 0, indentedBlock);
          return lines.join('\n');
        }
      }
      return rawComments + '\n' + currentCode;
    }

    function triggerHelpMeStart() {
      const banner = document.getElementById('ws-first-line-banner');
      const txtEl = document.getElementById('ws-first-line-text');
      const badgeEl = document.getElementById('ws-first-line-badge');
      const btn = document.getElementById('ws-help-start-btn');
      const editor = document.getElementById('ws-code-editor');

      const meta = state.activeWarmupId
        ? (state.warmupDrills || []).find(d => d.id === state.activeWarmupId)
        : state.activeProblemMeta;
      const firstLine = (meta && meta.firstLine) || 'Initialize a hash map or pointer state on line 1.';
      const rawOutline = state.activeLang === 'java'
        ? (meta && (meta.outlineJava || meta.javaOutlineComments))
        : (meta && (meta.outlinePy || meta.pythonOutlineComments));

      state.helpStartClicks = (state.helpStartClicks || 0) + 1;
      if (state.helpStartClicks === 1 || !rawOutline) {
        if (txtEl) txtEl.textContent = firstLine;
        if (badgeEl) badgeEl.textContent = state.activeWarmupId ? '3-step hints already in editor' : 'Click again to inject 3-step comments (keeps your code)';
        if (banner) banner.classList.remove('hidden');
        if (btn && !state.activeWarmupId) btn.textContent = '⚡ Inject 3-Step Outline';
        return;
      }

      if (editor && rawOutline) {
        editor.value = injectOutlineNonDestructively(editor.value, rawOutline, state.activeLang);
        handleEditorInput();
        if (badgeEl) badgeEl.textContent = '✓ 3-Step Outline Injected (Non-Destructive)';
        if (btn) btn.textContent = '⚡ Outline Injected';
      }
    }

    async function resetActiveProblemToBlank() {
      state.helpStartClicks = 0;
      state.lastReferencePython = null;
      resetHelpMeStartBanner();
      resetCodeCoachCard();
      if (state.activeWarmupId) {
        selectWarmupDrill(state.activeWarmupId);
        return;
      }
      const btn = document.getElementById('ws-reset-blank-btn');
      if (btn) btn.textContent = '⏳ Resetting...';
      try {
        const res = await fetch('/api/dsa/problem/reset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ slug: state.activeSlug, lang: state.activeLang })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.files && data.files.python) state.files.python = data.files.python;
          if (data.files && data.files.java) state.files.java = data.files.java;
          state.isDirty = false;
          switchEditorLang(state.activeLang, false);
        }
      } catch (_) {}
      if (btn) btn.textContent = '↺ Reset Blank';
    }

    function resetCodeCoachCard() {
      const titleEl = document.getElementById('ws-coach-score-title');
      const verdEl = document.getElementById('ws-coach-verdict');
      const scaleEl = document.getElementById('ws-coach-scaling');
      const corrEl = document.getElementById('ws-coach-correct');
      const spdEl = document.getElementById('ws-coach-speed');
      const clnEl = document.getElementById('ws-coach-clean');
      const tipsEl = document.getElementById('ws-coach-tips');
      const refWrap = document.getElementById('ws-coach-ref-wrap');
      const refPre = document.getElementById('ws-coach-ref-pre');
      if (titleEl) titleEl.textContent = '🏆 Instant Code Coach: Ready';
      if (verdEl) verdEl.textContent = '100% Local Grader';
      if (scaleEl) scaleEl.textContent = 'Click ▶ Run & Coach to score Correctness, Speed & Clean Code';
      if (corrEl) corrEl.textContent = 'Correctness: --/50';
      if (spdEl) spdEl.textContent = 'Speed: --/25';
      if (clnEl) clnEl.textContent = 'Clean Code: --/25';
      if (tipsEl) tipsEl.innerHTML = '<li>Write your first lines from scratch, or click <strong>⚡ Help Me Start</strong> for a 3-step plain-English outline.</li>';
      if (refWrap) refWrap.classList.add('hidden');
      if (refPre) refPre.classList.add('hidden');
    }

    function renderCodeCoachAssessment(coach, refSol) {
      if (!coach) return;
      const titleEl = document.getElementById('ws-coach-score-title');
      const verdEl = document.getElementById('ws-coach-verdict');
      const scaleEl = document.getElementById('ws-coach-scaling');
      const corrEl = document.getElementById('ws-coach-correct');
      const spdEl = document.getElementById('ws-coach-speed');
      const clnEl = document.getElementById('ws-coach-clean');
      const tipsEl = document.getElementById('ws-coach-tips');
      const refWrap = document.getElementById('ws-coach-ref-wrap');
      const refPre = document.getElementById('ws-coach-ref-pre');

      if (titleEl) titleEl.textContent = `🏆 Code Coach Score: ${coach.score} / 100`;
      if (verdEl) {
        verdEl.textContent = coach.verdict || 'Evaluated';
        verdEl.style.color = coach.score >= 90 ? 'var(--accent-sage)' : 'var(--accent-terra)';
      }
      if (scaleEl) scaleEl.textContent = coach.empiricalScaling || '';
      if (corrEl) corrEl.textContent = `✓ Correctness: ${coach.correctnessPts}/50`;
      if (spdEl) spdEl.textContent = `⚡ Speed: ${coach.speedPts}/25`;
      if (clnEl) clnEl.textContent = `✨ Clean Code: ${coach.cleanCodePts}/25`;

      if (tipsEl) {
        tipsEl.innerHTML = (coach.tips || []).map(t => `<li>${String(t).replace(/</g, '&lt;')}</li>`).join('');
      }
      const refCode = refSol && (state.activeLang === 'java' && refSol.java ? refSol.java : refSol.python);
      if (refCode && refWrap && refPre) {
        state.lastReferencePython = refCode;
        refPre.textContent = refCode;
        refWrap.classList.remove('hidden');
      } else if (refWrap) {
        refWrap.classList.add('hidden');
      }
    }

    function toggleCoachReference() {
      const refPre = document.getElementById('ws-coach-ref-pre');
      if (refPre) refPre.classList.toggle('hidden');
    }

    function renderHints(hints) {
      document.getElementById('ws-hints-list').innerHTML = (hints || []).map(h => {
        const unlocked = h.tier <= state.unlockedHintTier;
        return `
          <div class="news-card ${unlocked ? '' : 'opacity-60'}">
            <div class="font-bold">Tier ${h.tier}: ${h.title}</div>
            <p class="mt-1" style="color: var(--ink-secondary);">${unlocked ? h.content : '🔒 Click "Unlock Next Tier" above to reveal this hint.'}</p>
          </div>
        `;
      }).join('');
    }

    function unlockNextHintTier() {
      if (state.unlockedHintTier < 4) state.unlockedHintTier += 1;
      renderHints(state.currentHints || []);
    }

    function switchEditorLang(lang, preserveCurrentEditor = true) {
      const editor = document.getElementById('ws-code-editor');
      if (preserveCurrentEditor && editor && state.files[state.activeLang] && editor.value) {
        state.files[state.activeLang].content = editor.value;
      }
      state.activeLang = lang;
      document.getElementById('lang-tab-python').classList.toggle('active', lang === 'python');
      document.getElementById('lang-tab-java').classList.toggle('active', lang === 'java');

      const fileObj = state.files[lang];
      editor.value = fileObj ? fileObj.content : '';
      updateEditorLineNumbers();
      const shortSha = fileObj && fileObj.sha256 ? fileObj.sha256.slice(0, 7) : 'local';
      document.getElementById('editor-disk-status').textContent = `✓ Saved · ${fileObj ? fileObj.path : ''} (${shortSha})`;
    }

    async function saveActiveFileToDisk() {
      const fileObj = state.files[state.activeLang];
      const editor = document.getElementById('ws-code-editor');
      if (!fileObj || !editor) return;
      fileObj.content = editor.value;
      const statusEl = document.getElementById('editor-disk-status');
      statusEl.textContent = '⏳ Saving to disk...';

      try {
        const res = await fetch('/api/fs/file', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...(fileObj.sha256 && fileObj.sha256 !== 'local' ? { 'If-Match': fileObj.sha256 } : {})
          },
          body: JSON.stringify({
            path: fileObj.path,
            content: fileObj.content,
            expectedSha256: fileObj.sha256 !== 'local' ? fileObj.sha256 : undefined
          })
        });
        const data = await res.json();
        if (res.status === 412) {
          statusEl.textContent = '⚠️ Disk Conflict (Modified in IDE!)';
          statusEl.className = 'text-[11px] mono px-2.5 py-1 rounded-md';
          statusEl.style.background = 'var(--accent-terra-soft)';
          statusEl.style.color = 'var(--accent-terra)';
          statusEl.style.borderColor = 'var(--accent-terra)';
          return;
        }
        if (res.ok && data.sha256) {
          fileObj.sha256 = data.sha256;
          state.isDirty = false;
          statusEl.textContent = `✓ Saved · ${fileObj.path} (${data.sha256.slice(0, 7)})`;
          statusEl.className = 'text-[11px] mono px-2.5 py-1 rounded-md';
          statusEl.style.background = 'var(--accent-sage-soft)';
          statusEl.style.color = 'var(--accent-sage)';
          statusEl.style.borderColor = 'var(--border-warm)';
        }
      } catch (_) {
        statusEl.textContent = `✓ Saved in buffer · ${fileObj.path}`;
      }
    }

    async function runAndVerifyWorkspaceCode() {
      const btn = document.getElementById('ws-run-btn');
      if (state.activeWarmupId) {
        btn.textContent = '⏳ Coaching Drill...';
        try {
          const code = (document.getElementById('ws-code-editor') || {}).value || '';
          const res = await fetch('/api/dsa/warmup/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drillId: state.activeWarmupId, code })
          });
          if (res.ok) {
            const data = await res.json();
            if (data.cases && data.cases.length) state.cases = data.cases;
            renderCasePills(data.durationMs);
            selectTestCaseIndex(Math.min(state.selectedCaseIdx || 0, Math.max(0, state.cases.length - 1)));
            renderCodeCoachAssessment(data.codeCoach, data.referenceSolution);
          }
        } catch (_) {}
        btn.textContent = '▶ Run & Coach (⌘↵)';
        return;
      }

      await saveActiveFileToDisk();
      btn.textContent = '⏳ Running & Coaching...';
      try {
        const res = await fetch('/api/run-cases', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ slug: state.activeSlug, lang: state.activeLang })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.cases && data.cases.length) state.cases = data.cases;
          renderCasePills(data.durationMs);
          selectTestCaseIndex(Math.min(state.selectedCaseIdx || 0, Math.max(0, state.cases.length - 1)));
          document.getElementById('ws-mastery-btn').classList.toggle('hidden', data.status !== 'PASSED');
          if (data.status === 'PASSED') toggleProblemInvariant(true);
          renderCodeCoachAssessment(data.codeCoach, data.referenceSolution);
        } else {
          await fetch('/api/run-test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: state.activeSlug, lang: state.activeLang })
          });
        }
      } catch (_) {}
      btn.textContent = '▶ Run & Coach (⌘↵)';
    }

    async function markProblemMastered() {
      const btn = document.getElementById('ws-mastery-btn');
      btn.textContent = '⏳ Updating MASTER_SHEET.md...';
      try {
        await fetch('/api/dsa/mastery', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            problemId: state.activeProblemId,
            javaDone: true,
            pyDone: true,
            score: '95/100',
            status: 'Passed'
          })
        });
        await refreshDashboardState();
        await loadTracksAndHome();
        await loadRoadmapStatus();
        btn.textContent = '✓ Mastered in MASTER_SHEET.md!';
      } catch (_) {
        btn.textContent = '✓ Mastered!';
      }
    }

    function renderCasePills(latencyMs) {
      const container = document.getElementById('ws-case-pills');
      const pillsHtml = (state.cases || []).map((c, idx) => {
        const pending = c.passed === null || c.passed === undefined;
        const ok = c.passed === true;
        const selected = idx === state.selectedCaseIdx ? 'ring-2 ring-zinc-500' : '';
        const colorCls = pending
          ? 'bg-zinc-700 text-zinc-100'
          : (ok ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white');
        const icon = pending ? '○' : (ok ? '✓' : '✗');
        return `
          <button onclick="selectTestCaseIndex(${idx})" class="px-2.5 py-1 rounded-md font-semibold ${selected} ${colorCls}">
            ${icon} ${c.label || ('Case ' + (idx + 1))}
          </button>
        `;
      }).join('');
      const latTxt = latencyMs !== undefined ? `${latencyMs}ms` : 'Ready';
      container.innerHTML = pillsHtml + `<span id="ws-run-latency" class="ml-1" style="color: var(--ink-muted);">${latTxt}</span>`;
    }

    function selectTestCaseIndex(idx) {
      state.selectedCaseIdx = idx;
      const c = (state.cases || [])[idx];
      if (!c) return;
      renderCasePills();
      document.getElementById('ws-case-input-label').textContent = `Input: ${JSON.stringify(c.input)}`;
      document.getElementById('ws-case-expected').textContent = JSON.stringify(c.expected);
      document.getElementById('ws-case-actual').textContent = JSON.stringify(c.actual !== undefined ? c.actual : c.expected);
    }

    async function visualizeSelectedCase() {
      switchLeftTab('problem');
      const c = (state.cases || [])[state.selectedCaseIdx];
      if (c && c.input) document.getElementById('viz-custom-input').value = JSON.stringify(c.input);
      await loadVisualizerTrace(state.activeVisualizerId, c ? c.input : null);
    }

    async function runCustomVisualizerInput() {
      try {
        const parsed = JSON.parse(document.getElementById('viz-custom-input').value);
        await loadVisualizerTrace(state.activeVisualizerId, parsed);
      } catch (_) {
        alert('Please enter valid JSON for Custom Input');
      }
    }

    async function loadVisualizerTrace(vizId, customInput) {
      try {
        const res = await fetch('/api/visualize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ visualizerId: vizId, customInput })
        });
        if (res.ok) {
          const data = await res.json();
          state.vizTrace = data.steps || [];
          state.vizStepIdx = 0;
          renderVisualizerStep();
        }
      } catch (_) {}
    }

    function stepVisualizer(delta) {
      if (!state.vizTrace.length) return;
      state.vizStepIdx = Math.max(0, Math.min(state.vizTrace.length - 1, state.vizStepIdx + delta));
      renderVisualizerStep();
    }

    function renderVisualizerStep() {
      if (!state.vizTrace.length) return;
      const step = state.vizTrace[state.vizStepIdx];
      document.getElementById('viz-step-header').textContent = `Interactive 3D Trace · Step ${state.vizStepIdx + 1} of ${state.vizTrace.length}`;
      document.getElementById('viz-step-narration').textContent = step.narration || '';
      document.getElementById('viz-codeline-pill').textContent = step.codeLine || '';

      const tilesRow = document.getElementById('viz-tiles-row');
      const grid = document.getElementById('viz-buckets-grid');
      const colors = ['bg-[#E6C79C]', 'bg-[#72D5A5]', 'bg-[#E07A5F] text-white', 'bg-[#5A78E6] text-white'];

      if (step.nums && Array.isArray(step.nums)) {
        document.getElementById('viz-active-badge').textContent =
          step.complement !== null && step.complement !== undefined ? `target=${step.target} · need=${step.complement}` : `target=${step.target}`;
        tilesRow.innerHTML = step.nums.map((num, idx) => {
          const isMatched = (step.matchedIndices || []).includes(idx);
          const isCurrent = idx === step.currentIndex;
          const bg = isMatched
            ? 'bg-emerald-600 text-white ring-2 ring-emerald-900'
            : isCurrent
              ? 'bg-[#C85A32] text-white ring-2 ring-zinc-900 -translate-y-1'
              : 'bg-[#E6C79C] text-zinc-900';
          return `<div class="text-center"><span class="wood-tile px-3 h-10 rounded-lg ${bg} mono font-bold flex items-center justify-center transition">${num}</span><span class="text-[10px] mono" style="color:var(--ink-muted);">i=${idx}</span></div>`;
        }).join('');
        const seenEntries = Object.entries(step.seenMap || {});
        grid.innerHTML = seenEntries.length
          ? seenEntries.map(([val, idx]) => `<div class="bg-white rounded-lg border border-[#E6DEC8] p-2.5 text-center shadow-sm"><div class="text-[11px] font-bold" style="color:var(--accent-sage);">seen[${val}]</div><div class="font-bold">index → ${idx}</div></div>`).join('')
          : `<div class="col-span-3 bg-white rounded-lg border border-[#E6DEC8] p-3 text-center" style="color:var(--ink-muted);">seen = {} (Empty HashMap)</div>`;
        return;
      }

      if (step.s !== undefined && step.t !== undefined) {
        document.getElementById('viz-active-badge').textContent = step.title || 'Balance Check';
        tilesRow.innerHTML = String(step.s).split('').map((ch, idx) => `
          <span class="wood-tile w-9 h-9 rounded-lg ${idx === step.pointer ? 'bg-[#C85A32] text-white -translate-y-1' : 'bg-[#E6C79C] text-zinc-900'} mono font-bold flex items-center justify-center">${ch.toUpperCase()}</span>
        `).join('');
        const countsEntries = Object.entries(step.counts || {}).filter(([, v]) => v !== 0);
        grid.innerHTML = countsEntries.length
          ? countsEntries.slice(0, 6).map(([ch, cnt]) => `<div class="bg-white rounded-lg border border-amber-400 p-2.5 text-center"><div class="text-[11px] font-bold" style="color:var(--ink-secondary);">Slot '${ch}'</div><div class="font-bold ${cnt > 0 ? 'text-emerald-700' : 'text-rose-700'}">${cnt > 0 ? '+' + cnt : cnt}</div></div>`).join('')
          : `<div class="col-span-3 bg-white rounded-lg border-2 border-emerald-500 p-3 text-center font-bold text-emerald-800">All 26 frequency slots balanced at 0 ✓</div>`;
        return;
      }

      document.getElementById('viz-active-badge').textContent = step.currentWord ? `word = "${step.currentWord}"` : (step.title || 'Active');
      const word = step.currentWord || 'EAT';
      tilesRow.innerHTML = String(word).toUpperCase().split('').map((ch, i) => `
        <span class="wood-tile w-10 h-10 rounded-lg ${colors[i % colors.length]} mono font-bold flex items-center justify-center">${ch}</span>
      `).join('');
      if (step.buckets && Object.keys(step.buckets).length) {
        grid.innerHTML = Object.entries(step.buckets).slice(0, 3).map(([k, words]) => `
          <div class="bg-white rounded-lg border-2 border-[#1E6F5C] p-3 text-center shadow-sm">
            <div class="text-[11px] font-bold truncate" style="color: var(--accent-sage);">${k}</div>
            <div class="font-bold mt-1">${JSON.stringify(words)}</div>
          </div>
        `).join('');
      }
    }

    async function refreshDashboardState() {
      try {
        const dashRes = await fetch('/api/dashboard');
        if (dashRes.ok) {
          const dash = await dashRes.json();
          if (dash.dsa) {
            if (dash.dsa.chapters && dash.dsa.chapters.length) state.chapters = dash.dsa.chapters;
            state.recommendedProblem = dash.dsa.recommendedProblem || null;
            const kbCount = state.kbChapters.length || 8;
            const courseCount = state.kbCourses.length || 8;
            document.getElementById('home-dsa-progress').textContent = `${dash.dsa.bothDone} / ${dash.dsa.total} DSA · ${courseCount} Textbook Courses (${kbCount} Ch)`;
            document.getElementById('header-mastery-pill').textContent = `${dash.dsa.bothDone}/${dash.dsa.total} DSA · ${kbCount} Chapters`;
            renderRoadmapSpineAndChapter(state.activeChapterIdx);
          }
        }
      } catch (_) {
        renderRoadmapSpineAndChapter(0);
      }
    }

