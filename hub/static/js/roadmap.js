    /* ========================================================================
       STAFF SDET CAREER ROADMAP, GAMIFIED HABIT ENGINE & CROSS-PAGE TRACKER
       ======================================================================== */
    const DSA_QUICK_SLUG_TO_ID = {
      '001-two-sum': 'dsa-001',
      '002-contains-duplicate': 'dsa-002',
      '002-valid-anagram': 'dsa-003',
      '003-group-anagrams': 'dsa-004',
      '005-top-k-frequent-elements': 'dsa-005',
      '004-longest-consecutive-sequence': 'dsa-008'
    };

    function resolveDsaRoadmapItemId(slugOrId) {
      const raw = String(slugOrId || state.activeSlug || '').trim();
      if (raw.startsWith('dsa-')) return raw;
      for (let cIdx = 0; cIdx < (state.chapters || []).length; cIdx++) {
        const ch = state.chapters[cIdx];
        const found = (ch.problems || []).find(p => {
          const numStr = String(p.id).padStart(3, '0');
          return p.folderSlug === raw || p.slug === raw || `${numStr}-${p.slug}` === raw;
        });
        if (found && found.id) {
          return `dsa-${String(found.id).padStart(3, '0')}`;
        }
      }
      if (DSA_QUICK_SLUG_TO_ID[raw]) return DSA_QUICK_SLUG_TO_ID[raw];
      if (state.activeProblemId) {
        return `dsa-${String(state.activeProblemId).padStart(3, '0')}`;
      }
      const m = raw.match(/^(\d{3})/);
      return m ? `dsa-${m[1]}` : 'dsa-001';
    }

    async function loadRoadmapStatus() {
      try {
        const res = await fetch('/api/roadmap/status');
        if (res.ok) {
          state.roadmap = await res.json();
          if (!state.activeRoadmapPhase && state.roadmap.upNext && state.roadmap.upNext.phaseNumber) {
            state.activeRoadmapPhase = state.roadmap.upNext.phaseNumber;
          }
          renderRoadmapEverywhere();
          renderRoadmapSpineAndChapter(state.activeChapterIdx || 0);
        }
      } catch (_) {}
    }

    async function toggleStaffRoadmap() {
      const nextEnabled = !(state.roadmap && state.roadmap.roadmapEnabled);
      if (state.roadmap) {
        state.roadmap.roadmapEnabled = nextEnabled;
        renderRoadmapEverywhere();
      }
      try {
        const res = await fetch('/api/roadmap/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled: nextEnabled })
        });
        if (res.ok) {
          state.roadmap = await res.json();
          renderRoadmapEverywhere();
        }
      } catch (_) {}
    }

    async function setRoadmapPace(pace) {
      const normPace = pace === '120d' ? '120d' : '60d';
      try {
        const res = await fetch('/api/roadmap/pace', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pace: normPace })
        });
        if (res.ok) {
          state.roadmap = await res.json();
          renderRoadmapEverywhere();
        }
      } catch (_) {}
    }

    async function toggleRoadmapItemDone(itemId, explicitVal = null) {
      if (!itemId) return;
      try {
        const payload = { itemId };
        if (explicitVal !== null && explicitVal !== undefined) payload.completed = Boolean(explicitVal);
        const res = await fetch('/api/roadmap/mark-done', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const data = await res.json();
          state.roadmap = data;
          state.kbCompendiumCache = {};
          await Promise.all([
            loadKbCatalogAndDefaultChapter(),
            loadTracksAndHome(),
            refreshDashboardState(),
            loadWorkbenchAndInterviews()
          ]);
          if (state.activeKbChapter && state.activeKbChapter.slug === data.itemId) {
            state.activeKbChapter.mastered = Boolean(data.completed);
            ['kb-mark-done-btn', 'kb-footer-mark-done-btn'].forEach(bId => {
              const btn = document.getElementById(bId);
              if (btn) {
                btn.classList.toggle('completed', Boolean(data.completed));
                btn.textContent = data.completed
                  ? (bId.includes('footer') ? '✓ Chapter Completed' : '✓ Completed')
                  : (bId.includes('footer') ? '○ Mark Chapter Done' : '○ Mark Done');
              }
            });
            const mBadge = document.getElementById('kb-chapter-mastery-badge');
            if (mBadge) {
              if (data.completed) {
                mBadge.textContent = state.activeKbChapter.quizTotal
                  ? `✓ Mastered (${state.activeKbChapter.quizScore || state.activeKbChapter.quizTotal}/${state.activeKbChapter.quizTotal})`
                  : `✓ Completed in Roadmap`;
                mBadge.className = 'mono text-[11px] font-semibold px-2.5 py-1 rounded-full';
                mBadge.style.background = 'var(--accent-sage-soft)';
                mBadge.style.color = 'var(--accent-sage)';
              } else {
                mBadge.textContent = `${state.activeKbChapter.quizCount || (state.activeKbChapter.quizzes || []).length} Quiz Questions`;
                mBadge.className = 'mono text-[11px] font-semibold px-2.5 py-1 rounded-full';
                mBadge.style.background = 'var(--bg-subtle)';
                mBadge.style.color = 'var(--ink-muted)';
              }
            }
          }
          if (state.kbReadingMode === 'revise' && state.expandedCourseId) {
            await openCourseCompendium(state.expandedCourseId, false);
          }
          renderRoadmapEverywhere();
          renderRoadmapSpineAndChapter(state.activeChapterIdx || 0);
        }
      } catch (_) {}
    }

    async function toggleActiveChapterDone() {
      if (!state.activeKbChapter || !state.activeKbChapter.slug) return;
      await toggleRoadmapItemDone(state.activeKbChapter.slug);
    }

    async function toggleActiveDsaProblemDone() {
      const dsaId = resolveDsaRoadmapItemId(state.activeSlug);
      await toggleRoadmapItemDone(dsaId);
    }

    function selectRoadmapPhaseTab(phaseNumber) {
      state.activeRoadmapPhase = Number(phaseNumber) || 1;
      state.roadmapChecklistOpen = true;
      const detailsEl = document.getElementById('rm-phase-checklist-details');
      if (detailsEl) detailsEl.open = true;
      renderRoadmapEverywhere();
    }

    function openRoadmapItem(itemId) {
      if (!itemId) return;
      if (itemId.startsWith('dsa-')) {
        const num = parseInt(itemId.replace('dsa-', ''), 10);
        for (let cIdx = 0; cIdx < (state.chapters || []).length; cIdx++) {
          const ch = state.chapters[cIdx];
          const p = (ch.problems || []).find(pr => Number(pr.id) === num);
          if (p) {
            const numStr = String(p.id).padStart(3, '0');
            const targetSlug = p.folderSlug || `${numStr}-${p.slug}`;
            openOrScaffoldProblem(p.id, targetSlug, p.hasLocalFiles);
            return;
          }
        }
        showView('roadmap');
        return;
      }
      if (itemId.startsWith('wb-')) {
        openWorkbenchSubmode('frameworks');
        return;
      }
      if (itemId.startsWith('interview-')) {
        openWorkbenchSubmode('interviews');
        return;
      }
      openTextbookChapter(itemId, true);
    }

    function renderPageTrackerBannerHtml(pageKey, label, icon, meta, nextItem, currentActionHtml = '') {
      if (!meta) return '';
      const pct = meta.pct || 0;
      const nextBtn = nextItem ? `
        <button onclick="openRoadmapItem('${escapeHtml(nextItem.itemId)}')" class="btn-primary" style="padding: 4px 10px; font-size: 0.72rem;">
          ▶ Up Next (#${nextItem.globalOrder}): ${escapeHtml(nextItem.title.slice(0, 36))} →
        </button>
      ` : `<span class="mono text-[11px] font-bold" style="color: var(--accent-sage);">🏆 Track 100% Complete!</span>`;

      return `
        <div class="flex flex-wrap items-center gap-2.5">
          <span class="mono text-[11px] font-bold uppercase px-2.5 py-0.5 rounded-full" style="background: var(--accent-terra-soft); color: var(--accent-terra);">
            ${icon} ${escapeHtml(label)} TRACKER
          </span>
          <span class="mono font-bold text-xs" style="color: var(--ink-primary);">
            ${meta.done} / ${meta.total} Done (${pct}%)
          </span>
          <span class="mono text-[11px]" style="color: var(--ink-muted);">
            · ${meta.remaining} Remaining
          </span>
          <div class="w-28 h-2 rounded-full overflow-hidden hidden sm:block" style="background: var(--bg-subtle);">
            <div style="width: ${pct}%; background: var(--accent-sage);" class="h-full rounded-full transition-all"></div>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          ${currentActionHtml}
          ${nextBtn}
        </div>
      `;
    }

    function renderRoadmapEverywhere() {
      const rm = state.roadmap;
      if (!rm) return;
      const enabled = Boolean(rm.roadmapEnabled);
      const pctStr = rm.macro ? `${rm.macro.pct}%` : '0%';

      // 1. Sync Topbar & Both Home Switch Pills (.active + .on + dot + label)
      const syncSwitchBtn = (btnId, dotId, lblId, onText, offText) => {
        const btn = document.getElementById(btnId);
        const dot = document.getElementById(dotId);
        const lbl = document.getElementById(lblId);
        if (btn) {
          btn.classList.toggle('active', enabled);
          btn.classList.toggle('on', enabled);
        }
        if (dot) dot.textContent = enabled ? '●' : '○';
        if (lbl) lbl.textContent = enabled ? onText : offText;
      };

      syncSwitchBtn(
        'topbar-roadmap-toggle-btn',
        'topbar-roadmap-toggle-dot',
        'topbar-roadmap-toggle-label',
        `Roadmap: ON (${pctStr})`,
        'Roadmap: OFF'
      );
      syncSwitchBtn(
        'home-roadmap-switch-btn',
        'home-roadmap-switch-dot',
        'home-roadmap-switch-text',
        'Track Staff SDET Roadmap: ON',
        'Track Staff SDET Roadmap: OFF'
      );
      syncSwitchBtn(
        'home-roadmap-on-switch-btn',
        'home-roadmap-on-switch-dot',
        'home-roadmap-on-switch-text',
        'Track Staff SDET Roadmap: ON',
        'Track Staff SDET Roadmap: OFF'
      );

      // 2. Calm Mode-Aware Home View: Show EITHER Roadmap Card OR Freeform Hero Card (never both stacked)
      const homeDash = document.getElementById('home-roadmap-dashboard');
      const freeformHero = document.getElementById('home-freeform-hero');
      if (homeDash) homeDash.classList.toggle('hidden', !enabled);
      if (freeformHero) freeformHero.classList.toggle('hidden', enabled);

      // 3. Populate Home Roadmap Header & Macro Progress Rail
      const rankBadge = document.getElementById('rm-rank-badge');
      const streakPill = document.getElementById('rm-streak-pill');
      const xpPill = document.getElementById('rm-xp-pill');
      const overallPill = document.getElementById('rm-overall-pill');
      const macroPct = document.getElementById('rm-macro-pct');
      const macroBar = document.getElementById('rm-macro-bar');
      const sbCountPill = document.getElementById('rm-soundbite-count-pill');

      if (rankBadge && rm.gamification) {
        rankBadge.textContent = `${rm.gamification.rankIcon} ${rm.gamification.rankTitle}`;
      }
      if (streakPill && rm.gamification) {
        streakPill.textContent = `🔥 ${rm.gamification.streakDays}d Streak`;
      }
      if (xpPill && rm.gamification) {
        xpPill.textContent = `⚡ ${(rm.gamification.xp || 0).toLocaleString()} XP`;
      }
      if (overallPill && rm.macro) {
        overallPill.textContent = `${rm.macro.completedItems} / ${rm.macro.totalItems} Done · ${rm.macro.pct}%`;
      }
      if (macroPct && rm.macro) {
        macroPct.textContent = `${rm.macro.pct}% Complete · ${rm.macro.remainingItems} Remaining`;
      }
      if (macroBar && rm.macro) {
        macroBar.style.width = `${Math.max(1.5, rm.macro.pct || 0)}%`;
      }
      if (sbCountPill && rm.gamification) {
        sbCountPill.textContent = `🎙️ ${rm.gamification.unlockedSoundbitesCount || rm.gamification.unlockedSoundbites || 1} / 5 Staff Soundbites Unlocked`;
      }

      // 3b. Sync Daily Pace Toggle Buttons ('60d' vs '120d')
      const activePace = rm.pace === '120d' ? '120d' : '60d';
      const pace60Btn = document.getElementById('rm-pace-60d-btn');
      const pace120Btn = document.getElementById('rm-pace-120d-btn');
      if (pace60Btn) pace60Btn.classList.toggle('active', activePace === '60d');
      if (pace120Btn) pace120Btn.classList.toggle('active', activePace === '120d');

      // 4. Populate Focal "Today's Rigid Session" Action Card (#rm-up-next-card)
      const upNextCard = document.getElementById('rm-up-next-card');
      const upNext = rm.upNext;
      const todaySession = rm.todaySession || null;
      if (upNextCard) {
        if (upNext) {
          upNextCard.classList.remove('hidden');
          const phaseBadge = document.getElementById('rm-up-next-phase-badge');
          const orderBadge = document.getElementById('rm-up-next-order-badge');
          const titleEl = document.getElementById('rm-up-next-title');
          const whyEl = document.getElementById('rm-up-next-why');
          const openBtn = document.getElementById('rm-up-next-open-btn');
          const doneBtn = document.getElementById('rm-up-next-mark-btn');
          const chipsEl = document.getElementById('rm-today-session-chips');

          if (phaseBadge) {
            if (todaySession) {
              phaseBadge.textContent = `TODAY'S RIGID SESSION · SESSION ${todaySession.sessionNumber} OF ${todaySession.totalSessions} (PHASE ${todaySession.phaseNumber})`;
            } else {
              phaseBadge.textContent = `UP NEXT · PHASE ${upNext.phaseNumber} · ${(upNext.trackType || '').toUpperCase()}`;
            }
          }
          if (orderBadge) {
            orderBadge.textContent = todaySession && todaySession.quotaSummary
              ? todaySession.quotaSummary
              : `Step #${upNext.globalOrder} of ${rm.macro.totalItems} · ~${upNext.estMinutes || 12}m`;
          }
          if (titleEl) titleEl.textContent = upNext.title;
          if (whyEl) whyEl.textContent = upNext.whyNow || 'Next interleaved prerequisite in your sequential Staff SDET roadmap.';
          if (openBtn) openBtn.onclick = () => openRoadmapItem(upNext.itemId);
          if (doneBtn) {
            doneBtn.classList.remove('completed');
            doneBtn.textContent = '○ Mark Done';
            doneBtn.onclick = () => toggleRoadmapItemDone(upNext.itemId, true);
          }
          if (chipsEl) {
            const sItems = (todaySession && todaySession.items) ? todaySession.items : [];
            if (sItems.length) {
              chipsEl.classList.remove('hidden');
              chipsEl.innerHTML = sItems.map(sit => {
                const cls = sit.completed ? 'done' : (sit.isUpNext ? 'current' : '');
                const icon = sit.completed ? '✓' : (sit.isUpNext ? '▶' : '○');
                const suffix = sit.completed ? 'Done' : `${sit.estMinutes}m`;
                return `
                  <button
                    onclick="openRoadmapItem('${escapeHtml(sit.itemId)}')"
                    class="session-step-chip ${cls}"
                    title="${escapeHtml(sit.title)}"
                  >
                    <span>${icon}</span>
                    <span>#${sit.globalOrder} ${escapeHtml(sit.shortChipLabel || sit.title)} (${suffix})</span>
                  </button>
                `;
              }).join('');
            } else {
              chipsEl.classList.add('hidden');
              chipsEl.innerHTML = '';
            }
          }
        } else {
          upNextCard.classList.add('hidden');
        }
      }

      // 5. Populate Connected 5-Phase Flow Pipeline with Explicit Directional Arrows (→)
      const phases = rm.phases || [];
      const phaseTabsEl = document.getElementById('rm-phases-tabs');
      const phaseDetailEl = document.getElementById('rm-active-phase-detail');
      const checklistSummaryEl = document.getElementById('rm-phase-checklist-summary');
      const checklistDetailsEl = document.getElementById('rm-phase-checklist-details');

      if (phaseTabsEl && phases.length) {
        const activePhaseObj = phases.find(p => p.phaseNumber === state.activeRoadmapPhase) || phases[0];
        const shortPhaseNames = {
          1: 'Foundations & Core',
          2: 'Microservices & Sync',
          3: 'SQL, Cloud & CI/CD',
          4: 'Chaos, Perf & Security',
          5: 'Staff Bar-Raiser'
        };
        phaseTabsEl.innerHTML = phases.map((p, idx) => {
          const isAct = p.phaseNumber === activePhaseObj.phaseNumber;
          const isComp = p.completedItems >= p.totalItems && p.totalItems > 0;
          const sRange = p.sessionRange ? ` · ${p.sessionRange}` : '';
          const boxHtml = `
            <button onclick="selectRoadmapPhaseTab(${p.phaseNumber})" class="connected-flow-box ${isAct ? 'active' : (isComp ? 'completed' : '')}">
              <div>
                <div class="flex items-center justify-between gap-1 mono text-[10.5px] font-bold" style="color: ${isAct ? 'var(--accent-terra)' : (isComp ? 'var(--accent-sage)' : 'var(--ink-muted)')};">
                  <span>Phase ${p.phaseNumber}${escapeHtml(sRange)}</span>
                  <span>${p.completedItems}/${p.totalItems}</span>
                </div>
                <div class="font-bold text-xs mt-0.5 truncate" style="color: var(--ink-primary);">
                  ${escapeHtml(shortPhaseNames[p.phaseNumber] || p.title.replace(/^Phase \d+:\s*/, ''))}
                </div>
              </div>
              <div class="w-full h-1 rounded-full overflow-hidden mt-2" style="background: var(--bg-card);">
                <div style="width: ${p.pct}%; background: ${isAct ? 'var(--accent-terra)' : 'var(--accent-sage)'};" class="h-full rounded-full"></div>
              </div>
            </button>
          `;
          const arrowHtml = idx < phases.length - 1
            ? `<div class="connected-flow-arrow" aria-hidden="true">→</div>`
            : '';
          return boxHtml + arrowHtml;
        }).join('');

        if (checklistSummaryEl && activePhaseObj) {
          const rangeInfo = activePhaseObj.sessionRange ? `${activePhaseObj.sessionRange} · ` : '';
          checklistSummaryEl.textContent =
            `▸ View Phase ${activePhaseObj.phaseNumber} Interleaved Checklist: ${activePhaseObj.title.replace(/^Phase \d+:\s*/, '')} (${rangeInfo}${activePhaseObj.completedItems}/${activePhaseObj.totalItems} Done · ${activePhaseObj.weeks})`;
        }
        if (checklistDetailsEl && state.roadmapChecklistOpen !== undefined) {
          checklistDetailsEl.open = Boolean(state.roadmapChecklistOpen);
        }

        if (phaseDetailEl && activePhaseObj) {
          const items = activePhaseObj.items || [];
          let lastSessionSeen = null;
          const rowsHtml = items.map(it => {
            const typeBadgeMap = {
              course: { icon: '📖 Course', col: 'var(--accent-terra)' },
              dsa: { icon: '💻 DSA', col: 'var(--accent-amber)' },
              workbench: { icon: '🛠️ Lab', col: 'var(--accent-blue)' },
              interview: { icon: '🎙️ Mock', col: 'var(--accent-crimson)' }
            };
            const tb = typeBadgeMap[it.trackType] || typeBadgeMap.course;
            let sessionHeaderHtml = '';
            if (it.sessionNumber && it.sessionNumber !== lastSessionSeen) {
              lastSessionSeen = it.sessionNumber;
              sessionHeaderHtml = `
                <div class="mono text-[10px] font-bold uppercase pt-2 pb-0.5 px-1" style="color: var(--accent-terra);">
                  Session ${it.sessionNumber} of ${rm.totalSessions || 60}
                </div>
              `;
            }
            return `
              ${sessionHeaderHtml}
              <div class="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-lg text-xs" style="background: ${it.completed ? 'var(--accent-sage-soft)' : 'var(--bg-subtle)'};">
                <div onclick="openRoadmapItem('${escapeHtml(it.itemId)}')" class="flex items-center gap-2 flex-1 min-w-[220px] cursor-pointer">
                  <span class="mono text-[10px] font-bold px-1.5 py-0.5 rounded" style="background: var(--bg-card); color: var(--ink-muted);">
                    #${it.globalOrder}
                  </span>
                  <span class="mono text-[10px] font-bold px-1.5 py-0.5 rounded" style="background: var(--bg-card); color: ${tb.col};">
                    ${tb.icon}
                  </span>
                  <span class="font-semibold truncate ${it.completed ? 'line-through opacity-75' : ''}" style="color: var(--ink-primary);">
                    ${escapeHtml(it.title)}
                  </span>
                  <span class="mono text-[10px] hidden md:inline" style="color: var(--ink-muted);">
                    (${escapeHtml(it.parentGroup)})
                  </span>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  <button
                    onclick="toggleRoadmapItemDone('${escapeHtml(it.itemId)}')"
                    class="mark-done-btn ${it.completed ? 'completed' : ''}"
                    style="padding: 3px 9px; font-size: 0.68rem;"
                  >
                    ${it.completed ? '✓ Completed' : '○ Mark Done'}
                  </button>
                  <button onclick="openRoadmapItem('${escapeHtml(it.itemId)}')" class="btn-subtle" style="padding: 3px 9px; font-size: 0.68rem;">
                    Open →
                  </button>
                </div>
              </div>
            `;
          }).join('');

          phaseDetailEl.innerHTML = `
            <div class="flex flex-wrap items-center justify-between gap-2 pb-2.5" style="border-bottom: 1px solid var(--border-warm);">
              <p class="text-xs" style="color: var(--ink-secondary); margin: 0;">
                ${escapeHtml(activePhaseObj.subtitle)}
              </p>
              <span class="mono text-[10.5px] px-2.5 py-1 rounded-full font-semibold" style="background: var(--bg-subtle); color: var(--accent-sage);">
                🎙️ Soundbite: "${escapeHtml((activePhaseObj.soundbite || '').slice(0, 72))}..."
              </span>
            </div>
            <div class="max-h-72 overflow-y-auto pr-1 space-y-1.5 pt-1">
              ${rowsHtml}
            </div>
          `;
        }
      }

      // 6. Populate 4 Practice Arena Gauges (#rm-tracks-grid — Parallel Daily Arenas, Zero Misleading Sequential Arrows)
      const tracksGrid = document.getElementById('rm-tracks-grid');
      if (tracksGrid && rm.pages) {
        const pageCards = [
          { key: 'courses', title: 'Textbook Courses', icon: '📚', accent: 'var(--accent-terra)', action: "showView('textbook')", unit: 'Chapters' },
          { key: 'dsa', title: 'Coding & DSA', icon: '💻', accent: 'var(--accent-amber)', action: "showView('roadmap')", unit: 'Problems' },
          { key: 'workbench', title: 'Local Workbench', icon: '🛠️', accent: 'var(--accent-blue)', action: "openWorkbenchSubmode('frameworks')", unit: 'Labs' },
          { key: 'interviews', title: 'Staff Mock Sim', icon: '🎙️', accent: 'var(--accent-crimson)', action: "openWorkbenchSubmode('interviews')", unit: 'Scenarios' }
        ];
        tracksGrid.innerHTML = pageCards.map(pc => {
          const stat = rm.pages[pc.key] || { done: 0, total: 0, remaining: 0, pct: 0 };
          return `
            <div onclick="${pc.action}" class="connected-flow-box">
              <div>
                <div class="flex items-center justify-between gap-1.5 mono text-[10.5px] font-bold" style="color: ${pc.accent};">
                  <span>${pc.icon} ${escapeHtml(pc.title)}</span>
                  <span>${stat.pct}%</span>
                </div>
                <div class="flex items-center justify-between mono text-[11px] mt-1" style="color: var(--ink-primary);">
                  <span><strong>${stat.done}/${stat.total}</strong> ${pc.unit}</span>
                  <span style="color: var(--ink-muted); font-size: 10px;">${stat.remaining} left</span>
                </div>
              </div>
              <div class="w-full h-1 rounded-full overflow-hidden mt-2" style="background: var(--bg-card);">
                <div style="width: ${stat.pct}%; background: ${pc.accent};" class="h-full rounded-full transition-all"></div>
              </div>
            </div>
          `;
        }).join('');
      }

      // 7. Populate Cross-Page Completion Tracker Banners on ALL 6 Pages
      const allItems = phases.flatMap(p => p.items || []);
      const nextByTrack = (tType) => allItems.find(i => i.trackType === tType && !i.completed) || null;

      const isChDone = Boolean(state.activeKbChapter && rm.completedMap && (rm.completedMap[state.activeKbChapter.slug] || state.activeKbChapter.mastered));
      const activeDsaId = resolveDsaRoadmapItemId(state.activeSlug);
      const isDsaDone = Boolean(rm.completedMap && rm.completedMap[activeDsaId]);
      const isMiDone = Boolean(rm.completedMap && rm.completedMap['interview-1']);
      const savedDraftCount = state.interviewSession && state.interviewSession.candidateResponses
        ? Object.values(state.interviewSession.candidateResponses).filter(v => String(v || '').trim().length > 0).length
        : 0;

      const kbBannerAction = state.activeKbChapter
        ? `<button onclick="toggleActiveChapterDone()" class="mark-done-btn ${isChDone ? 'completed' : ''}" style="padding: 4px 10px; font-size: 0.7rem;">${isChDone ? '✓ Current Chapter Done' : '○ Mark Current Chapter Done'}</button>`
        : '';
      const wsBannerAction = `<button onclick="toggleActiveDsaProblemDone()" class="mark-done-btn ${isDsaDone ? 'completed' : ''}" style="padding: 4px 10px; font-size: 0.7rem;">${isDsaDone ? '✓ Active Problem Done' : '○ Mark Active Problem Done'}</button>`;
      const miBannerAction = `
        <span class="mono text-[11px]" style="color: var(--ink-secondary);">Drafts Saved: <strong>${savedDraftCount} / 5</strong> Questions</span>
        <button onclick="toggleRoadmapItemDone('interview-1')" class="mark-done-btn ${isMiDone ? 'completed' : ''}" style="padding: 4px 10px; font-size: 0.7rem;">${isMiDone ? '✓ Mock Sim Completed' : '○ Mark Mock Sim Done'}</button>
      `;

      const bannerConfigs = [
        { id: 'kb-page-tracker-bar', key: 'courses', label: 'COURSES (01–12)', icon: '📚', next: nextByTrack('course'), extra: kbBannerAction },
        { id: 'dsa-page-tracker-bar', key: 'dsa', label: 'CODING & DSA (128)', icon: '💻', next: nextByTrack('dsa'), extra: '' },
        { id: 'ws-page-tracker-bar', key: 'dsa', label: '50/50 SPLIT STUDIO', icon: '💻', next: nextByTrack('dsa'), extra: wsBannerAction },
        { id: 'wb-page-tracker-bar', key: 'workbench', label: 'LOCAL IDE WORKBENCH', icon: '🛠️', next: nextByTrack('workbench'), extra: '' },
        { id: 'mi-page-tracker-bar', key: 'interviews', label: 'STAFF MOCK SIMULATOR', icon: '🎙️', next: nextByTrack('interview'), extra: miBannerAction }
      ];

      bannerConfigs.forEach(cfg => {
        const el = document.getElementById(cfg.id);
        if (!el) return;
        el.classList.toggle('active-tracker', enabled);
        if (enabled && rm.pages && rm.pages[cfg.key]) {
          el.innerHTML = renderPageTrackerBannerHtml(cfg.key, cfg.label, cfg.icon, rm.pages[cfg.key], cfg.next, cfg.extra);
        } else {
          el.innerHTML = '';
        }
      });

      const pulseBar = document.getElementById('pulse-page-tracker-bar');
      if (pulseBar) {
        pulseBar.classList.toggle('active-tracker', enabled);
        if (enabled) {
          pulseBar.innerHTML = `
            <div class="flex flex-wrap items-center gap-2.5">
              <span class="mono text-[11px] font-bold uppercase px-2.5 py-0.5 rounded-full" style="background: var(--accent-sage-soft); color: var(--accent-sage);">
                📡 CONTINUOUS INDUSTRY RADAR
              </span>
              <span class="text-xs" style="color: var(--ink-secondary);">
                Optional daily reading cross-linked to your 12 Courses — not required for 256-item Staff Roadmap completion.
              </span>
            </div>
            ${upNext ? `<button onclick="openRoadmapItem('${escapeHtml(upNext.itemId)}')" class="btn-subtle" style="padding: 4px 10px; font-size: 0.72rem;">← Return to Up Next (#${upNext.globalOrder})</button>` : ''}
          `;
        } else {
          pulseBar.innerHTML = '';
        }
      }

      // 8. Sync All Individual Mark-Done Buttons Across Active Pages
      ['kb-mark-done-btn', 'kb-footer-mark-done-btn'].forEach(bId => {
        const kbBtn = document.getElementById(bId);
        if (kbBtn) {
          kbBtn.classList.toggle('completed', isChDone);
          kbBtn.textContent = isChDone
            ? (bId.includes('footer') ? '✓ Chapter Completed' : '✓ Completed')
            : (bId.includes('footer') ? '○ Mark Chapter Done' : '○ Mark Done');
        }
      });

      ['ws-roadmap-done-btn', 'ws-title-mark-done-btn', 'ws-footer-mark-done-btn'].forEach(bId => {
        const wsBtn = document.getElementById(bId);
        if (wsBtn) {
          wsBtn.classList.toggle('completed', isDsaDone);
          wsBtn.textContent = isDsaDone
            ? (bId.includes('title') ? '✓ Problem Completed' : '✓ Completed')
            : (bId.includes('title') ? '○ Mark Problem Done' : '○ Mark Done');
        }
      });

      ['mi-mark-done-btn', 'mi-studio-mark-done-btn'].forEach(bId => {
        const miBtn = document.getElementById(bId);
        if (miBtn) {
          miBtn.classList.toggle('completed', isMiDone);
          miBtn.textContent = isMiDone
            ? (bId.includes('studio') ? '✓ Interview Completed' : '✓ Completed')
            : (bId.includes('studio') ? '○ Mark Interview Done' : '○ Mark Done');
        }
      });
    }

    async function initHub() {
      initZenPreferences();
      attachSmartEditorKeybindings();
      await loadKbCatalogAndDefaultChapter();
      await Promise.all([
        loadRoadmapStatus(),
        refreshDashboardState(),
        loadTracksAndHome(),
        loadNewsfeedView('all', false),
        loadWorkbenchAndInterviews(),
        loadWarmupDrills()
      ]);
      let nextUnsolvedSlug = '004-longest-consecutive-sequence';
      for (const ch of (state.chapters || [])) {
        const unsolved = (ch.problems || []).find(p => !p.bothDone && p.hasLocalFiles && p.folderSlug);
        if (unsolved) {
          nextUnsolvedSlug = unsolved.folderSlug;
          break;
        }
      }
      await openProblemWorkspace(nextUnsolvedSlug, false);

      try {
        const feedRes = await fetch('/api/feed');
        if (feedRes.ok) {
          const feed = await feedRes.json();
          document.getElementById('feed-cards-container').innerHTML = (feed.cards || []).map(c => `
            <div class="news-card space-y-1.5">
              <div class="mono text-[11px] font-semibold uppercase" style="color: var(--accent-terra);">${escapeHtml(c.category)} · ${escapeHtml(c.readTime)}</div>
              <h4 style="font-size: 1.05rem; font-weight: 700;">${escapeHtml(c.title)}</h4>
              <p class="text-xs leading-relaxed" style="color: var(--ink-secondary);">${escapeHtml(c.mentalModel)}</p>
            </div>
          `).join('');
        }
      } catch (_) {}

      const hashView = (window.location.hash || '').replace('#', '').trim();
      const validViews = ['home', 'textbook', 'newsfeed', 'roadmap', 'workspace', 'workbench'];
      showView(validViews.includes(hashView) ? hashView : 'home');
      setInterval(pollActiveDiskFile, 3000);
    }

    document.addEventListener('keydown', (e) => {
      const inInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes((e.target && e.target.tagName) || '');
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (document.body.classList.contains('zen-fullscreen')) toggleZenFullscreen(false);
        const searchInput = document.getElementById('global-kb-search');
        if (searchInput) { searchInput.focus(); searchInput.select(); }
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') {
        if (state.activeView === 'workspace') {
          e.preventDefault();
          saveActiveFileToDisk();
        }
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        if (state.activeView === 'workspace') {
          e.preventDefault();
          runAndVerifyWorkspaceCode();
        }
        return;
      }
      if (e.key === 'Escape') {
        const drawer = document.getElementById('kb-peek-drawer');
        if (drawer && drawer.classList.contains('open')) {
          closePeekDrawer();
          return;
        }
        if (state.maximizedSplitPane) {
          restoreAllSplitPanes();
          return;
        }
        if (document.body.classList.contains('zen-fullscreen')) {
          toggleZenFullscreen(false);
          return;
        }
      }
      if (!inInput && !e.metaKey && !e.ctrlKey && !e.altKey) {
        if (e.key === 'f' || e.key === 'F' || e.key === 'z' || e.key === 'Z') {
          e.preventDefault();
          toggleCenterContentExpand(e.shiftKey);
        } else if (e.key === '[') {
          if (state.activeView === 'textbook') {
            e.preventDefault();
            toggleKbSidebar('left');
          } else if (state.activeView === 'roadmap') {
            e.preventDefault();
            toggleSplitPaneMaximize('roadmap-main');
          }
        } else if (e.key === ']' && state.activeView === 'textbook') {
          e.preventDefault();
          toggleKbSidebar('right');
        }
      }
    });

    window.addEventListener('DOMContentLoaded', initHub);
