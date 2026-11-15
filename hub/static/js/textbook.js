    /* ========================================================================
       TEXTBOOK COURSES & SCIENTIFIC PEDAGOGY CONTROLLER
       ======================================================================== */
    const FALLBACK_COURSE_SPINE = [
      { courseId: '01-zero-to-staff-sdet', priorityRank: 1, shortTitle: 'Zero to Staff SDET', title: '01. Zero to Staff SDET', accentColor: '#C85A32', pillBg: '#FCEEE8', plannedModules: 4, publishedChapters: 12, masteredChapters: 0, tagline: 'Determinism math, BVA/Pairwise, test topologies, 32-worker tenant isolation, CI sharding, OTel & Staff RFCs.', modules: [] },
      { courseId: '02-building-testing-frameworks', priorityRank: 2, shortTitle: 'Building Testing Frameworks', title: '02. Zero to Mastery: Building Testing Frameworks', accentColor: '#2B6CB0', pillBg: '#EBF8FF', plannedModules: 4, publishedChapters: 10, masteredChapters: 0, tagline: 'Runner lifecycles, DI fixtures, POM vs Screenplay, immutable builders, JSON diffing, smart retries & SDKs.', modules: [] },
      { courseId: '03-ui-automation-playwright', priorityRank: 3, shortTitle: 'UI Automation (Playwright)', title: '03. Zero to Mastery: UI Automation (Playwright-Focused)', accentColor: '#1E6F5C', pillBg: '#E6F4F0', plannedModules: 4, publishedChapters: 10, masteredChapters: 0, tagline: 'CDP & BiDi pipes, BrowserContext memory, Accessibility locators, 5 actionability gates, HAR & sharded CI.', modules: [] },
      { courseId: '04-api-and-api-automation', priorityRank: 4, shortTitle: 'API & API Automation', title: '04. Zero to Mastery: API & API Automation', accentColor: '#0F766E', pillBg: '#E6FFFA', plannedModules: 4, publishedChapters: 10, masteredChapters: 0, tagline: 'TCP/TLS 1.3, HTTP/2 pooling, JWT/OAuth2/mTLS, Pydantic + REST Assured, 429 Token Buckets, gRPC & Pact.', modules: [] },
      { courseId: '05-ai-engineering', priorityRank: 5, shortTitle: 'AI Engineering (ML → LLMs)', title: '05. Zero to Mastery: AI Engineering', accentColor: '#5B3FD9', pillBg: '#F0EBFF', plannedModules: 5, publishedChapters: 12, masteredChapters: 0, tagline: 'Loss functions, embeddings, Self-Attention, RoPE/GQA/MoE, KV-Cache, Hybrid RRF RAG, LoRA/DPO & MCP Agents.', modules: [] },
      { courseId: '06-ai-engineering-qa-focused', priorityRank: 6, shortTitle: 'AI Engineering — QA Focused', title: '06. Zero to Mastery: AI Engineering — QA Focused', accentColor: '#7C3AED', pillBg: '#F5F3FF', plannedModules: 4, publishedChapters: 10, masteredChapters: 0, tagline: 'Golden datasets, RAG Triad entailment, negation traps, Rogan-Gladen Judge calibration, red-teaming & AST healing.', modules: [] },
      { courseId: '07-distributed-system-design', priorityRank: 7, shortTitle: 'Distributed System Design', title: '07. Distributed System Design', accentColor: '#B45309', pillBg: '#FEF3C7', plannedModules: 2, publishedChapters: 5, masteredChapters: 0, tagline: 'Backpressure, Full Jitter, consistent hashing, Kafka outbox CDC, Singleflight caching & Raft quorums.', modules: [] },
      { courseId: '08-core-cs-internals', priorityRank: 8, shortTitle: 'Core CS: OS, Net & Storage', title: '08. Core CS: OS, Networking & Storage', accentColor: '#374151', pillBg: '#F3F4F6', plannedModules: 2, publishedChapters: 5, masteredChapters: 0, tagline: 'Linux virtual memory, post-GC RSS slopes, TLS 1.3/HTTP2, B+Trees vs LSM-Trees, WAL, CAS & epoll/cgroups.', modules: [] },
      { courseId: '09-sql-and-data-engineering', priorityRank: 9, shortTitle: 'SQL & Data Engineering', title: '09. Zero to Mastery: SQL, Databases & Data Engineering', accentColor: '#0369A1', pillBg: '#E0F2FE', plannedModules: 4, publishedChapters: 10, masteredChapters: 0, tagline: 'Relational algebra, B+Tree composite indexes, EXPLAIN BUFFERS, MVCC isolation anomalies, CDC & Great Expectations.', modules: [] },
      { courseId: '10-docker-cicd-and-cloud-infra', priorityRank: 10, shortTitle: 'Docker, CI/CD & Cloud Infra', title: '10. Zero to Mastery: Docker, CI/CD & Cloud Test Infrastructure', accentColor: '#0284C7', pillBg: '#F0F9FF', plannedModules: 4, publishedChapters: 10, masteredChapters: 0, tagline: 'Linux namespaces & cgroups v2, OverlayFS multi-stage builds, Testcontainers, LPT CI sharding, K8s & Terraform.', modules: [] },
      { courseId: '11-performance-load-and-sre', priorityRank: 11, shortTitle: 'Performance, Load & SRE', title: '11. Zero to Mastery: Performance, Load Testing & SRE Observability', accentColor: '#D97706', pillBg: '#FEF3C7', plannedModules: 4, publishedChapters: 10, masteredChapters: 0, tagline: 'Little’s Law, Coordinated Omission, HdrHistogram, k6/Locust executors, USL contention, FlameGraphs & Chaos.', modules: [] },
      { courseId: '12-application-and-api-security', priorityRank: 12, shortTitle: 'App, API & AI Security', title: '12. Zero to Mastery: Application, API & AI Security Testing', accentColor: '#BE123C', pillBg: '#FFE4E6', plannedModules: 4, publishedChapters: 10, masteredChapters: 0, tagline: 'OWASP API Top 10, BOLA/BOPLA matrix, JWT/JWKS Confusion, OAuth2 PKCE, SSRF, SAST/DAST & LLM Prompt Shields.', modules: [] }
    ];

    async function loadKbCatalogAndDefaultChapter() {
      try {
        const [coursesRes, chaptersRes] = await Promise.all([
          fetch('/api/kb/courses'),
          fetch('/api/kb/chapters')
        ]);
        if (coursesRes.ok) {
          const cData = await coursesRes.json();
          state.kbCourses = (cData.courses && cData.courses.length) ? cData.courses : FALLBACK_COURSE_SPINE;
        } else {
          state.kbCourses = FALLBACK_COURSE_SPINE;
        }
        if (chaptersRes.ok) {
          const chData = await chaptersRes.json();
          state.kbChapters = chData.chapters || [];
        }
        const countPill = document.getElementById('kb-total-count-pill');
        if (countPill) {
          countPill.textContent = `${state.kbChapters.length || 74} Chapters`;
        }
        renderHomeCoursesGrid();
        renderKbChaptersSpine();

        if (state.kbChapters.length && !state.activeKbChapter) {
          const c01 = state.kbCourses.find(c => c.courseId === '01-zero-to-staff-sdet' && c.firstChapterSlug);
          const initialSlug = c01 ? c01.firstChapterSlug : (state.kbChapters[0] ? state.kbChapters[0].slug : 'cs-03-lsm-trees-b-trees-and-wal-isolation');
          await openTextbookChapter(initialSlug, false);
        }
      } catch (_) {
        state.kbCourses = FALLBACK_COURSE_SPINE;
        renderHomeCoursesGrid();
        renderKbChaptersSpine();
      }
    }

    function toggleSpineCourse(courseId) {
      state.expandedCourseId = courseId;
      if (state.kbReadingMode === 'revise') {
        openCourseCompendium(courseId, false);
        return;
      }
      const course = (state.kbCourses || []).find(c => c.courseId === courseId);
      if (course && course.firstChapterSlug && (!state.activeKbChapter || state.activeKbChapter.courseId !== courseId)) {
        openTextbookChapter(course.firstChapterSlug, false);
      } else {
        renderKbChaptersSpine();
      }
    }

    function handleSpineChapterClick(slug) {
      if (typeof closePeekDrawer === 'function') closePeekDrawer();
      if (state.kbReadingMode === 'revise') {
        const anchor = document.getElementById(`comp-ch-${slug}`);
        if (anchor) {
          anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
          return;
        }
      }
      openTextbookChapter(slug);
    }

    function scrollToKbSection(secId) {
      const el = document.getElementById(secId);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function renderKbChaptersSpine() {
      const container = document.getElementById('kb-chapters-spine');
      if (!container) return;

      const coursesList = (state.kbCourses && state.kbCourses.length) ? state.kbCourses : FALLBACK_COURSE_SPINE;
      const selectedCourseId = state.expandedCourseId || (state.activeKbChapter && state.activeKbChapter.courseId) || coursesList[0].courseId;
      const activeCourse = coursesList.find(c => c.courseId === selectedCourseId) || coursesList[0];

      const pillsHtml = coursesList.map(course => {
        const isSelected = course.courseId === activeCourse.courseId;
        const numPrefix = String(course.priorityRank).padStart(2, '0');
        const rightBadge = `${course.masteredChapters || 0}/${course.publishedChapters || 0} Ch`;
        return `
          <button
            onclick="toggleSpineCourse('${course.courseId}')"
            class="course-pill ${isSelected ? 'active' : ''}"
          >
            <span class="truncate">${numPrefix}. ${escapeHtml(course.shortTitle || course.title)}</span>
            <span class="mono shrink-0" style="font-size: 0.68rem; color: ${(course.masteredChapters && course.masteredChapters === course.publishedChapters) ? 'var(--accent-sage)' : (isSelected ? 'var(--accent-terra)' : 'var(--ink-muted)')};">
              ${escapeHtml(rightBadge)}
            </span>
          </button>
        `;
      }).join('');

      let modules = activeCourse.modules || [];
      if (!modules.length && state.kbChapters.length) {
        const matching = state.kbChapters.filter(c => c.courseId === activeCourse.courseId);
        if (matching.length) {
          modules = [{ moduleNumber: 1, moduleTitle: 'Module 1: Core Architecture', chapters: matching }];
        }
      }

      const courseNumStr = String(activeCourse.priorityRank || 1).padStart(2, '0');
      const isReviseMode = state.kbReadingMode === 'revise';
      const syllabusHtml = modules.length ? modules.map(mod => `
        <div class="space-y-1 mb-2.5">
          <div class="mono uppercase px-1" style="font-size: 0.65rem; font-weight: 700; color: ${activeCourse.accentColor || 'var(--accent-terra)'};">
            ${escapeHtml(mod.moduleTitle || ('Module ' + mod.moduleNumber))}
          </div>
          ${(mod.chapters || []).map(ch => {
            const isActive = !isReviseMode && state.activeKbChapter && state.activeKbChapter.slug === ch.slug;
            const chNum = String(ch.chapterNumber).padStart(2, '0');
            return `
              <div class="flex items-center gap-1">
                <button
                  onclick="handleSpineChapterClick('${ch.slug}')"
                  class="syllabus-ch-row flex-1 ${isActive ? 'active' : ''}"
                >
                  <span class="truncate">Mod ${mod.moduleNumber} · Ch ${chNum}: ${escapeHtml(ch.title)}</span>
                </button>
                <button
                  onclick="event.stopPropagation(); toggleRoadmapItemDone('${ch.slug}')"
                  class="mono text-[10px] px-1.5 py-0.5 rounded border shrink-0 cursor-pointer transition"
                  style="${ch.mastered ? 'background:#E6F4F0; color:#1E6F5C; border-color:#B7E4D8; font-weight:700;' : 'background:var(--bg-subtle); color:var(--ink-muted); border-color:var(--border-warm);'}"
                  title="${ch.mastered ? 'Completed in Roadmap (Click to unmark)' : 'Mark Chapter as Done'}"
                >
                  ${ch.mastered ? '✓' : '○'}
                </button>
              </div>
            `;
          }).join('')}
        </div>
      `).join('') : `
        <div class="text-xs px-1 py-2" style="color: var(--ink-muted);">
          Chapters indexing into SQLite FTS5...
        </div>
      `;

      const spineMarkup = `
        <div>${pillsHtml}</div>
        <div style="border-top: 1px solid var(--border-warm); margin-top: 12px; padding-top: 12px;">
          <button
            onclick="if(typeof closePeekDrawer==='function') closePeekDrawer(); setKbReadingMode(state.kbReadingMode === 'revise' ? 'guided' : 'revise')"
            class="w-full text-left px-3 py-2 rounded-lg transition flex items-center justify-between gap-2 mb-2.5 cursor-pointer"
            style="background: ${isReviseMode ? 'var(--accent-terra)' : 'var(--bg-subtle)'}; color: ${isReviseMode ? '#FAF7F2' : 'var(--accent-terra)'}; border: none; font-size: 0.73rem; font-weight: 700;"
          >
            <span>${isReviseMode ? '📖 Exit Single-Page Revise' : '⚡ Revise Course in 1 Page'}</span>
            <span class="mono text-[10px]">${activeCourse.publishedChapters || 0} Ch</span>
          </button>
          <div class="mono uppercase" style="font-size: 0.68rem; color: var(--ink-muted); font-weight: 600; margin-bottom: 8px;">
            COURSE ${courseNumStr} ${isReviseMode ? 'JUMP ANCHORS' : 'SYLLABUS MODULES'} (${activeCourse.publishedChapters || 0} CH)
          </div>
          ${syllabusHtml}
        </div>
      `;
      container.innerHTML = spineMarkup;
      const peekBody = document.getElementById('kb-peek-drawer-body');
      if (peekBody) peekBody.innerHTML = spineMarkup;
    }

    async function handleSpineKbSearch(query) {
      const out = document.getElementById('kb-spine-search-results');
      const q = (query || '').trim();
      if (!q) {
        out.classList.add('hidden');
        return;
      }
      try {
        const res = await fetch(`/api/kb/search?q=${encodeURIComponent(q)}`);
        if (!res.ok) return;
        const data = await res.json();
        out.classList.remove('hidden');
        out.innerHTML = (data.results || []).slice(0, 6).map(r => `
          <div onclick="openTextbookChapter('${r.slug}')" class="news-card cursor-pointer hover:border-zinc-900 text-xs" style="padding: 10px;">
            <div class="mono text-[9px] font-semibold uppercase" style="color: var(--accent-terra);">${escapeHtml(r.courseId || r.track)}</div>
            <div class="font-bold mt-0.5">${escapeHtml(r.title)}</div>
            <div class="text-[11px] mt-0.5" style="color: var(--ink-secondary);">${r.snippet || ''}</div>
          </div>
        `).join('') || `<div class="text-xs p-2" style="color: var(--ink-muted);">No matches.</div>`;
      } catch (_) {}
    }

    function formatWalkthroughCaptionHtml(txt) {
      return escapeHtml(txt || '')
        .replace(/`([^`]+)`/g, '<span class="wt-code-pill">$1</span>')
        .replace(/-&gt;/g, '→')
        .replace(/=&gt;/g, '⇒');
    }

    function sanitizeCaptionForSpeech(txt) {
      return (txt || '')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/->/g, ' to ')
        .replace(/=>/g, ' leads to ')
        .replace(/!=/g, ' does not equal ')
        .replace(/==/g, ' equals ')
        .replace(/p\^N/g, 'p to the power of N')
        .replace(/0\.99\s*\^\s*100/g, '0.99 to the power of 100');
    }

    function formatSecondsMmSs(sec) {
      const s = Math.max(0, Math.round(Number(sec) || 0));
      return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
    }

    function renderWalkthroughDiagramSvg(slide, sceneIdx) {
      const rawNodes = (Array.isArray(slide.nodes) && slide.nodes.length >= 3)
        ? slide.nodes.slice(0, 3)
        : [
            (slide.badge || `Scene ${sceneIdx + 1}`).split('·').pop().trim(),
            ((slide.code || '').split('\n').find(l => l.trim() && !l.trim().startsWith('#')) || 'Execute Step Invariant').trim().slice(0, 36),
            ['1. Build Intuition', '2. Run Starter Code', '3. Spot Scaling Trap', '4. Apply Staff Math'][sceneIdx % 4]
          ];
      const activeIdx = typeof slide.activeNode === 'number' ? slide.activeNode : Math.min(2, sceneIdx % 3);
      let svg = `<svg viewBox="0 0 380 170" class="w-full h-40">`;
      rawNodes.forEach((lbl, i) => {
        const y = 8 + i * 54;
        const isAct = i === activeIdx;
        const fill = isAct ? '#112A24' : '#232329';
        const stroke = isAct ? '#34D399' : '#3F3F46';
        const textCol = isAct ? '#A7F3D0' : '#E4E4E7';
        const cleanLbl = String(lbl || '').slice(0, 40);
        svg += `<rect x="24" y="${y}" width="332" height="36" rx="9" fill="${fill}" stroke="${stroke}" stroke-width="${isAct ? 2 : 1.2}"/>`;
        svg += `<text x="190" y="${y + 22}" text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" font-size="11.5" font-weight="700" fill="${textCol}">${escapeHtml(cleanLbl)}</text>`;
        if (i < rawNodes.length - 1) {
          svg += `<line x1="190" y1="${y + 36}" x2="190" y2="${y + 52}" stroke="#71717A" stroke-width="1.5"/>`;
          svg += `<polygon points="186,${y + 48} 194,${y + 48} 190,${y + 54}" fill="#71717A"/>`;
        }
      });
      svg += `</svg>`;
      return svg;
    }

    function stopWalkthroughPlayback() {
      if (state.wtTimer) {
        clearInterval(state.wtTimer);
        state.wtTimer = null;
      }
      state.wtPlaying = false;
      const audioEl = document.getElementById('kb-wt-audio');
      if (audioEl) {
        try { audioEl.pause(); } catch (_) {}
      }
      if (window.speechSynthesis) {
        try { window.speechSynthesis.cancel(); } catch (_) {}
      }
      const playBtn = document.getElementById('kb-wt-play-btn');
      if (playBtn) playBtn.textContent = '▶ Play Walkthrough';
      const waveEl = document.getElementById('kb-wt-waveform');
      if (waveEl) waveEl.classList.remove('wt-playing');
      const statusEl = document.getElementById('kb-wt-audio-status');
      if (statusEl) statusEl.textContent = 'Ready';
    }

    function renderWalkthroughFrame(currentTimeSec = null) {
      const ch = state.activeKbChapter;
      const shell = document.getElementById('kb-walkthrough-shell');
      if (!ch || !shell) return;
      const slides = (ch.walkthrough && ch.walkthrough.length) ? ch.walkthrough : [];
      if (!slides.length && !ch.videoUrl) {
        shell.classList.add('hidden');
        return;
      }
      shell.classList.remove('hidden');

      const mediaToggle = document.getElementById('kb-wt-media-toggle');
      if (mediaToggle) {
        mediaToggle.classList.toggle('hidden', !ch.videoUrl);
        mediaToggle.classList.toggle('flex', Boolean(ch.videoUrl));
      }

      if (slides.length) {
        state.wtSlideIdx = Math.max(0, Math.min(slides.length - 1, state.wtSlideIdx));
        const cur = slides[state.wtSlideIdx];
        const totalDur = Number(slides[slides.length - 1].t_end) || (slides.length * 12);
        const curSec = currentTimeSec !== null ? currentTimeSec : (Number(cur.t_start) || (state.wtSlideIdx * (totalDur / slides.length)));

        const badgeEl = document.getElementById('kb-wt-slide-badge');
        if (badgeEl) badgeEl.textContent = `🎬 ${cur.badge || ('SCENE ' + (state.wtSlideIdx + 1) + ' / ' + slides.length)}`;

        const syncPill = document.getElementById('kb-wt-step-sync-pill');
        if (syncPill) {
          const stepTitle = cur.stepName || `Step ${Math.min(4, state.wtSlideIdx + 1)}`;
          syncPill.textContent = `🔗 Synced with ${stepTitle}`;
        }

        const svgCanvas = document.getElementById('kb-wt-svg-canvas');
        if (svgCanvas) svgCanvas.innerHTML = renderWalkthroughDiagramSvg(cur, state.wtSlideIdx);

        // Timed On-Screen Visual Cues (`stock-analysis` `_stamp_visual_cue_on_frame` pattern)
        const cueEl = document.getElementById('kb-wt-visual-cue');
        if (cueEl) {
          const activeCue = (cur.visual_cues || []).find(
            c => curSec >= Number(c.t_start) && curSec <= (Number(c.t_start) + Number(c.duration || 2.2))
          );
          if (activeCue && activeCue.text) {
            cueEl.textContent = `⚡ ${activeCue.text}`;
            cueEl.classList.remove('hidden');
          } else {
            cueEl.classList.add('hidden');
          }
        }

        const capEl = document.getElementById('kb-wt-caption');
        if (capEl) capEl.innerHTML = formatWalkthroughCaptionHtml(cur.caption || '');
        const codeEl = document.getElementById('kb-wt-code');
        if (codeEl) codeEl.textContent = cur.code || '';

        const progEl = document.getElementById('kb-wt-progress-fill');
        if (progEl) {
          const pct = totalDur > 0 ? Math.min(100, Math.max(6, Math.round((curSec / totalDur) * 100))) : Math.round(((state.wtSlideIdx + 1) / slides.length) * 100);
          progEl.style.width = `${pct}%`;
        }
        const timeEl = document.getElementById('kb-wt-time-label');
        if (timeEl) {
          timeEl.textContent = `${formatSecondsMmSs(curSec)} / ${formatSecondsMmSs(totalDur)}`;
        }

        const pillsEl = document.getElementById('kb-wt-pills');
        if (pillsEl) {
          pillsEl.innerHTML = slides.map((s, idx) => {
            const shortLbl = (s.badge || `Scene ${idx + 1}`).split('·').pop().trim();
            const isAct = idx === state.wtSlideIdx;
            return `
              <button
                onclick="jumpWalkthroughSlide(${idx})"
                class="mono text-[10.5px] px-2.5 py-1.5 rounded-lg border text-left cursor-pointer transition truncate"
                style="background:${isAct ? '#2A1E19' : '#18181B'}; color:${isAct ? '#FFFFFF' : '#A1A1AA'}; border-color:${isAct ? '#C85A32' : '#2E2E36'}; font-weight:${isAct ? '700' : '500'};"
              >
                ${idx + 1}. ${escapeHtml(shortLbl)} (${escapeHtml(s.time || formatSecondsMmSs(s.t_start || 0))})
              </button>
            `;
          }).join('');
        }
      }
    }

    function setWalkthroughAudioMode(mode) {
      state.wtAudioMode = mode;
      const vBtn = document.getElementById('kb-wt-audio-voice');
      const sBtn = document.getElementById('kb-wt-audio-silent');
      if (vBtn) vBtn.className = mode === 'voice' ? 'px-2 py-0.5 rounded bg-[#C85A32] text-white font-semibold cursor-pointer' : 'px-2 py-0.5 rounded text-zinc-300 cursor-pointer';
      if (sBtn) sBtn.className = mode === 'silent' ? 'px-2 py-0.5 rounded bg-[#C85A32] text-white font-semibold cursor-pointer' : 'px-2 py-0.5 rounded text-zinc-300 cursor-pointer';
      if (state.wtPlaying) {
        stopWalkthroughPlayback();
        toggleWalkthroughPlay();
      }
    }

    function scrubWalkthroughTimeline(evt) {
      const ch = state.activeKbChapter;
      if (!ch || !ch.walkthrough || !ch.walkthrough.length) return;
      const slides = ch.walkthrough;
      const rect = evt.currentTarget.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(0.999, (evt.clientX - rect.left) / Math.max(1, rect.width)));
      const totalDur = Number(slides[slides.length - 1].t_end) || (slides.length * 12);
      const targetSec = ratio * totalDur;
      const matchedIdx = slides.findIndex(s => targetSec >= Number(s.t_start || 0) && targetSec <= Number(s.t_end || 9999));
      state.wtSlideIdx = matchedIdx >= 0 ? matchedIdx : Math.floor(ratio * slides.length);
      const audioEl = document.getElementById('kb-wt-audio');
      if (audioEl && audioEl.src && !audioEl.paused) {
        try { audioEl.currentTime = targetSec; } catch (_) {}
      }
      renderWalkthroughFrame(targetSec);
    }

    function jumpWalkthroughSlide(idx) {
      const ch = state.activeKbChapter;
      const slides = (ch && ch.walkthrough) || [];
      if (!slides.length) return;
      state.wtSlideIdx = Math.max(0, Math.min(slides.length - 1, idx));
      const targetSlide = slides[state.wtSlideIdx];
      const audioEl = document.getElementById('kb-wt-audio');
      if (state.wtPlaying && audioEl && audioEl.src && (state.wtAudioMode || 'voice') === 'voice') {
        try { audioEl.currentTime = Number(targetSlide.t_start || 0); } catch (_) {}
      }
      renderWalkthroughFrame(Number(targetSlide.t_start || 0));
    }

    function stepWalkthrough(delta) {
      const slides = (state.activeKbChapter && state.activeKbChapter.walkthrough) || [];
      if (!slides.length) return;
      const nextIdx = (state.wtSlideIdx + delta + slides.length) % slides.length;
      jumpWalkthroughSlide(nextIdx);
    }

    async function toggleWalkthroughPlay() {
      if (state.wtPlaying) {
        stopWalkthroughPlayback();
        return;
      }
      const ch = state.activeKbChapter;
      const slides = (ch && ch.walkthrough) || [];
      if (!slides.length) return;

      if (state.wtCollapsed) {
        state.wtCollapsed = false;
        const wtBody = document.getElementById('kb-wt-body');
        const wtBtn = document.getElementById('kb-wt-collapse-btn');
        if (wtBody) wtBody.classList.remove('hidden');
        if (wtBtn) wtBtn.textContent = 'Hide ▲';
      }

      state.wtPlaying = true;
      const playBtn = document.getElementById('kb-wt-play-btn');
      if (playBtn) playBtn.textContent = '⏸ Pause';
      const waveEl = document.getElementById('kb-wt-waveform');
      if (waveEl) waveEl.classList.add('wt-playing');
      const statusEl = document.getElementById('kb-wt-audio-status');

      const audioMode = state.wtAudioMode || 'voice';
      const speed = state.wtSpeed || 1.0;

      // Mode 1: Neural / TTS Audio MP3 Sync (`stock-analysis` `tts_engine.py` + `_normalize_section_durations`)
      if (audioMode === 'voice') {
        try {
          if (statusEl) statusEl.textContent = 'Syncing Audio…';
          const res = await fetch('/api/kb/walkthrough-audio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slug: ch.slug })
          });
          if (res.ok && state.wtPlaying) {
            const data = await res.json();
            if (Array.isArray(data.slides) && data.slides.length) {
              ch.walkthrough = data.slides;
            }
            const audioEl = document.getElementById('kb-wt-audio');
            if (audioEl && data.audioUrl) {
              audioEl.src = data.audioUrl;
              audioEl.playbackRate = speed;
              const startSlide = ch.walkthrough[state.wtSlideIdx] || ch.walkthrough[0];
              audioEl.currentTime = Number(startSlide.t_start || 0);
              if (statusEl) statusEl.textContent = `${data.backend || 'Voice'} (${speed}x)`;

              audioEl.ontimeupdate = () => {
                if (!state.wtPlaying) return;
                const t = audioEl.currentTime;
                const activeSlides = ch.walkthrough || [];
                const foundIdx = activeSlides.findIndex((s, i) =>
                  t >= Number(s.t_start || 0) && (t < Number(s.t_end || 9999) || i === activeSlides.length - 1)
                );
                if (foundIdx >= 0 && foundIdx !== state.wtSlideIdx) {
                  state.wtSlideIdx = foundIdx;
                }
                renderWalkthroughFrame(t);
              };
              audioEl.onended = () => {
                stopWalkthroughPlayback();
                if (statusEl) statusEl.textContent = 'Completed ✓';
              };
              await audioEl.play();
              return;
            }
          }
        } catch (_) {}
      }

      // Mode 2: Visual-Only or Web Speech API (`utter.onend`) Fallback
      if (statusEl) statusEl.textContent = audioMode === 'voice' ? `Speaking (${speed}x)` : `Visual Play (${speed}x)`;
      const totalDur = Number(slides[slides.length - 1].t_end) || (slides.length * 10);
      let curSec = Number((slides[state.wtSlideIdx] || {}).t_start || 0);

      if (audioMode === 'voice' && window.speechSynthesis) {
        try {
          window.speechSynthesis.cancel();
          const cur = slides[state.wtSlideIdx];
          const utter = new SpeechSynthesisUtterance(sanitizeCaptionForSpeech(cur.caption || ''));
          utter.rate = speed;
          window.speechSynthesis.speak(utter);
        } catch (_) {}
      }

      state.wtTimer = setInterval(() => {
        if (!state.wtPlaying) return;
        curSec += 0.15 * speed;
        if (curSec >= totalDur) {
          renderWalkthroughFrame(totalDur);
          stopWalkthroughPlayback();
          if (statusEl) statusEl.textContent = 'Completed ✓';
          return;
        }
        const nextIdx = slides.findIndex((s, i) =>
          curSec >= Number(s.t_start || 0) && (curSec < Number(s.t_end || 9999) || i === slides.length - 1)
        );
        if (nextIdx >= 0 && nextIdx !== state.wtSlideIdx) {
          state.wtSlideIdx = nextIdx;
          if (audioMode === 'voice' && window.speechSynthesis) {
            try {
              window.speechSynthesis.cancel();
              const u = new SpeechSynthesisUtterance(sanitizeCaptionForSpeech(slides[nextIdx].caption || ''));
              u.rate = speed;
              window.speechSynthesis.speak(u);
            } catch (_) {}
          }
        }
        renderWalkthroughFrame(curSec);
      }, 150);
    }

    function cycleWalkthroughSpeed() {
      const speeds = [1.0, 1.25, 1.5];
      const nextIdx = (speeds.indexOf(state.wtSpeed || 1.0) + 1) % speeds.length;
      state.wtSpeed = speeds[nextIdx];
      const btn = document.getElementById('kb-wt-speed-btn');
      if (btn) btn.textContent = `${state.wtSpeed.toFixed(state.wtSpeed === 1 ? 1 : 2).replace(/0$/, '')}x`;
      const audioEl = document.getElementById('kb-wt-audio');
      if (audioEl) audioEl.playbackRate = state.wtSpeed;
    }

    function toggleWalkthroughCollapse() {
      state.wtCollapsed = !state.wtCollapsed;
      const body = document.getElementById('kb-wt-body');
      const btn = document.getElementById('kb-wt-collapse-btn');
      if (body) body.classList.toggle('hidden', state.wtCollapsed);
      if (btn) btn.textContent = state.wtCollapsed ? 'Expand Studio ▼' : 'Hide ▲';
      if (state.wtCollapsed) stopWalkthroughPlayback();
    }

    function switchWalkthroughMediaMode(mode) {
      state.wtMediaMode = mode;
      const sbPane = document.getElementById('kb-wt-storyboard-pane');
      const vidPane = document.getElementById('kb-wt-video-pane');
      const sbBtn = document.getElementById('kb-wt-mode-story');
      const vidBtn = document.getElementById('kb-wt-mode-video');
      if (!sbPane || !vidPane) return;

      if (mode === 'video' && state.activeKbChapter && state.activeKbChapter.videoUrl) {
        stopWalkthroughPlayback();
        sbPane.classList.add('hidden');
        vidPane.classList.remove('hidden');
        const vUrl = state.activeKbChapter.videoUrl;
        if (/\.(mp4|webm)(\?|$)/i.test(vUrl) || vUrl.startsWith('/media/')) {
          vidPane.innerHTML = `<video controls preload="metadata" class="w-full rounded-lg border border-zinc-800 max-h-80 bg-black" src="${escapeHtml(vUrl)}"></video>`;
        } else {
          vidPane.innerHTML = `<iframe src="${escapeHtml(vUrl)}" class="w-full h-72 rounded-lg border border-zinc-800" allowfullscreen></iframe>`;
        }
      } else {
        vidPane.classList.add('hidden');
        vidPane.innerHTML = '';
        sbPane.classList.remove('hidden');
      }
      if (sbBtn && vidBtn) {
        sbBtn.style.background = mode === 'storyboard' ? '#C85A32' : '#27272A';
        vidBtn.style.background = mode === 'video' ? '#C85A32' : '#27272A';
      }
    }

    function renderPretrainingStrip(primitives) {
      const sec = document.getElementById('kb-sec-pretraining');
      const grid = document.getElementById('kb-pretraining-grid');
      const pill = document.getElementById('kb-vocab-count-pill');
      if (!sec || !grid) return;
      if (!primitives || !primitives.length) {
        sec.classList.add('hidden');
        return;
      }
      sec.classList.remove('hidden');
      const allItems = primitives.slice(0, 4);
      const unlockedCount = state.kbReadingMode === 'full'
        ? allItems.length
        : Math.min(allItems.length, state.kbActiveStepIdx + 1);
      const showFormula = state.kbReadingMode === 'full' || state.kbActiveStepIdx >= 2;

      if (pill) pill.textContent = `${unlockedCount} / ${allItems.length} Unlocked`;

      grid.innerHTML = allItems.slice(0, unlockedCount).map(p => `
        <div class="bg-[#FAF7F2] rounded-lg p-2.5 border border-[#E6DEC8] space-y-1">
          <div class="font-bold text-xs" style="color: var(--ink-primary);">${escapeHtml(p.term || '')}</div>
          <p class="text-[11px] leading-relaxed" style="color: var(--ink-secondary); margin: 0;">${escapeHtml(p.meaning || '')}</p>
          ${(showFormula && p.formula) ? `<div class="mono text-[10px] px-2 py-0.5 rounded bg-white border border-[#E6DEC8] font-semibold inline-block" style="color: var(--accent-terra);">${escapeHtml(p.formula)}</div>` : ''}
        </div>
      `).join('');
    }

    function setKbReadingMode(mode) {
      state.kbReadingMode = mode;
      const gBtn = document.getElementById('kb-mode-guided');
      const fBtn = document.getElementById('kb-mode-full');
      const rBtn = document.getElementById('kb-mode-revise');
      if (gBtn) gBtn.classList.toggle('active', mode === 'guided');
      if (fBtn) fBtn.classList.toggle('active', mode === 'full');
      if (rBtn) rBtn.classList.toggle('active', mode === 'revise');

      const singleChapterIds = [
        'kb-continuity-bridge',
        'kb-walkthrough-shell',
        'kb-step-bar',
        'kb-chapter-body',
        'kb-sec-simulator',
        'kb-lab-callout',
        'kb-sec-quiz',
        'kb-step-continue-bar',
        'kb-prev-next-bar'
      ];
      const compContainer = document.getElementById('kb-compendium-container');

      if (mode === 'revise') {
        stopWalkthroughPlayback();
        singleChapterIds.forEach(id => {
          const el = document.getElementById(id);
          if (el) el.classList.add('hidden');
        });
        if (compContainer) compContainer.classList.remove('hidden');
        const targetCourseId = state.expandedCourseId || (state.activeKbChapter && state.activeKbChapter.courseId) || '01-zero-to-staff-sdet';
        openCourseCompendium(targetCourseId, false);
        return;
      }

      if (compContainer) compContainer.classList.add('hidden');
      if (!state.kbUserWidthOverride && typeof setKbContentWidth === 'function') {
        setKbContentWidth('comfort', false);
      }
      ['kb-continuity-bridge', 'kb-chapter-body', 'kb-prev-next-bar'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('hidden');
      });
      renderWalkthroughFrame();
      renderKbChaptersSpine();
      renderActiveKbStepView();
    }

    async function openCourseCompendium(courseId, switchScreen = true) {
      const targetCourseId = courseId || state.expandedCourseId || (state.activeKbChapter && state.activeKbChapter.courseId) || '01-zero-to-staff-sdet';
      state.expandedCourseId = targetCourseId;
      state.kbReadingMode = 'revise';
      if (switchScreen) showView('textbook');
      if (!state.kbUserWidthOverride && typeof setKbContentWidth === 'function') {
        setKbContentWidth('wide', false);
      }

      const gBtn = document.getElementById('kb-mode-guided');
      const fBtn = document.getElementById('kb-mode-full');
      const rBtn = document.getElementById('kb-mode-revise');
      if (gBtn) gBtn.classList.remove('active');
      if (fBtn) fBtn.classList.remove('active');
      if (rBtn) rBtn.classList.add('active');

      stopWalkthroughPlayback();
      [
        'kb-continuity-bridge',
        'kb-walkthrough-shell',
        'kb-step-bar',
        'kb-chapter-body',
        'kb-sec-simulator',
        'kb-lab-callout',
        'kb-sec-quiz',
        'kb-step-continue-bar',
        'kb-prev-next-bar'
      ].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
      });

      const compContainer = document.getElementById('kb-compendium-container');
      if (compContainer) {
        compContainer.classList.remove('hidden');
        if (!state.kbCompendiumCache[targetCourseId]) {
          compContainer.innerHTML = `<div class="p-6 text-center mono text-xs" style="color: var(--ink-secondary);">⚡ Compiling unabridged single-page course compendium...</div>`;
        }
      }

      renderKbChaptersSpine();

      try {
        let data = state.kbCompendiumCache[targetCourseId];
        if (!data) {
          const res = await fetch(`/api/kb/course-compendium?course=${encodeURIComponent(targetCourseId)}`);
          if (!res.ok) return;
          data = await res.json();
          state.kbCompendiumCache[targetCourseId] = data;
        }
        state.activeCompendium = data;
        renderCourseCompendiumView(data);
      } catch (_) {}
    }

    function toggleCompendiumLayer(layerKey) {
      state.compendiumLayers[layerKey] = !state.compendiumLayers[layerKey];
      state.compendiumCramOnly = false;
      const cramBtn = document.getElementById('comp-cram-preset-btn');
      if (cramBtn) cramBtn.classList.remove('active');
      const active = Boolean(state.compendiumLayers[layerKey]);
      const btn = document.getElementById(`comp-layer-btn-${layerKey}`);
      if (btn) btn.classList.toggle('active', active);
      document.querySelectorAll(`[data-comp-layer="${layerKey}"]`).forEach(el => {
        el.classList.toggle('hidden', !active);
      });
    }

    function toggleCompendiumCramPreset() {
      state.compendiumCramOnly = !state.compendiumCramOnly;
      const hasStep5 = document.querySelectorAll('[data-comp-layer="step5"]').length > 0;
      const nextLayers = state.compendiumCramOnly
        ? { step1: false, step2: false, step3: false, step4: !hasStep5, step5: true, qa: true }
        : { step1: true, step2: true, step3: true, step4: true, step5: true, qa: true };
      state.compendiumLayers = nextLayers;
      Object.keys(nextLayers).forEach(lk => {
        const active = Boolean(nextLayers[lk]);
        const btn = document.getElementById(`comp-layer-btn-${lk}`);
        if (btn) btn.classList.toggle('active', active);
        document.querySelectorAll(`[data-comp-layer="${lk}"]`).forEach(el => {
          el.classList.toggle('hidden', !active);
        });
      });
      const cramBtn = document.getElementById('comp-cram-preset-btn');
      if (cramBtn) {
        cramBtn.classList.toggle('active', state.compendiumCramOnly);
        cramBtn.textContent = state.compendiumCramOnly ? '⚡ Cram Mode ON (Show All)' : '⚡ Interview Cram';
      }
    }

    function toggleCompendiumAnswerBlur() {
      state.compendiumBlurAnswers = !state.compendiumBlurAnswers;
      const btn = document.getElementById('comp-qa-blur-btn');
      if (btn) {
        btn.classList.toggle('active', !state.compendiumBlurAnswers);
        btn.textContent = state.compendiumBlurAnswers ? '🙈 Answers Blurred (Click to Reveal)' : '👁️ Answers Shown';
      }
      document.querySelectorAll('.comp-qa-answer-target').forEach(el => {
        el.classList.toggle('qa-answer-blur', state.compendiumBlurAnswers);
        el.classList.remove('revealed');
      });
    }

    function filterCompendiumChapters(query) {
      state.compendiumFilterQuery = (query || '').trim().toLowerCase();
      const q = state.compendiumFilterQuery;
      let visibleCount = 0;
      document.querySelectorAll('.compendium-chapter-card').forEach(card => {
        if (!q) {
          card.classList.remove('hidden');
          visibleCount++;
          return;
        }
        const text = (card.textContent || '').toLowerCase();
        const matched = text.includes(q);
        card.classList.toggle('hidden', !matched);
        if (matched) visibleCount++;
      });
      const countEl = document.getElementById('comp-filter-count');
      if (countEl && state.activeCompendium) {
        const total = (state.activeCompendium.chapters || []).length;
        countEl.textContent = q ? `${visibleCount}/${total} Ch match` : `${total} Chapters`;
      }
    }

    function renderCourseCompendiumView(data) {
      const compContainer = document.getElementById('kb-compendium-container');
      if (!compContainer || !data || !data.course) return;

      const c = data.course;
      const st = data.stats || {};
      const chapters = data.chapters || [];
      const redThread = data.redThreadMap || [];
      const glossary = data.masterGlossary || [];

      // Update main header banner to reflect Course-Level Single-Page Compendium
      const kickerEl = document.getElementById('kb-chapter-kicker');
      const titleEl = document.getElementById('kb-chapter-title');
      const sumEl = document.getElementById('kb-chapter-summary');
      const tagsEl = document.getElementById('kb-chapter-tags');
      const mBadge = document.getElementById('kb-chapter-mastery-badge');

      if (kickerEl) {
        kickerEl.textContent = `SINGLE-PAGE MASTER COMPENDIUM · ${st.chapterCount || chapters.length} CHAPTERS · ${(st.totalWords || 0).toLocaleString()} WORDS · ZERO OMISSIONS`;
      }
      if (titleEl) {
        titleEl.textContent = `${c.title} — Complete Single-Page Revision Guide`;
      }
      if (sumEl) {
        sumEl.textContent = `Every chapter (Ch 01 → Ch ${String(chapters.length).padStart(2, '0')}) compiled into one continuous, unabridged reference page—preserving 100% of prose, mental models, Mermaid architecture diagrams, Naive-vs-Staff contrast matrices, dual-language code blueprints, Staff equations, trade-off tables, and Self-Check Q&A keys without video or widget chrome.`;
      }
      if (tagsEl) {
        tagsEl.innerHTML = `
          <span class="tag">📚 ${st.chapterCount || chapters.length} Chapters in 1 Page</span>
          <span class="tag">📝 ${(st.totalWords || 0).toLocaleString()} Unabridged Words</span>
          <span class="tag">💻 ${st.totalCodeBlocks || 0} Code Blueprints</span>
          <span class="tag">🗺️ ${st.totalMermaidDiagrams || 0} Architecture Diagrams</span>
          <span class="tag">📐 ${st.totalDisplayEquations || 0} Staff Equations</span>
          <span class="tag">🎯 ${st.totalSelfCheckQuestions || 0} Self-Check Q&amp;As</span>
          <span class="tag">⚡ Compiled in ${data.latencyMs || 4}ms</span>
        `;
      }
      if (mBadge) {
        mBadge.textContent = `⚡ ~${st.reviseEstimatedMinutes || 45}m Rapid Revision`;
        mBadge.className = 'mono text-[11px] font-semibold px-2.5 py-1 rounded-full bg-[#FCEEE8] text-[#C85A32] border border-[#F3C6B6]';
      }

      // Update Right-Rail Progress Ring & Glossary summary for Course Compendium Mode
      const arc = document.getElementById('kb-journey-ring-arc');
      const pctLabel = document.getElementById('kb-journey-ring-pct');
      const stepTitle = document.getElementById('kb-journey-step-title');
      const altPill = document.getElementById('kb-journey-altitude-pill');
      const hintEl = document.getElementById('kb-journey-upnext-hint');
      if (arc) arc.setAttribute('stroke-dashoffset', '0');
      if (pctLabel) pctLabel.textContent = `${chapters.length}Ch`;
      if (stepTitle) stepTitle.textContent = `All ${chapters.length} Chapters (1 Page)`;
      if (altPill) altPill.textContent = `⚡ Unabridged Compendium`;
      if (hintEl) hintEl.textContent = `${(st.totalWords || 0).toLocaleString()} words · Use spine to jump to any chapter.`;
      renderPretrainingStrip(glossary.slice(0, 4));

      const layers = state.compendiumLayers;
      const prefLang = state.preferredKbLang || 'python';

      const redThreadRowsHtml = redThread.map(rt => {
        const chNum = String(rt.chapterNumber).padStart(2, '0');
        return `
          <tr class="hover:bg-[#FAF7F2] transition">
            <td class="mono font-bold text-xs whitespace-nowrap" style="color: var(--accent-terra);">
              <a href="#comp-ch-${escapeHtml(rt.slug)}" onclick="event.preventDefault(); handleSpineChapterClick('${escapeHtml(rt.slug)}')" class="hover:underline">
                Ch ${chNum}
              </a>
            </td>
            <td class="font-bold text-xs" style="color: var(--ink-primary);">
              <a href="#comp-ch-${escapeHtml(rt.slug)}" onclick="event.preventDefault(); handleSpineChapterClick('${escapeHtml(rt.slug)}')" class="hover:underline">
                ${escapeHtml(rt.title)}
              </a>
              <div class="mono text-[10px] font-normal mt-0.5" style="color: var(--ink-muted);">${escapeHtml(rt.moduleTitle || '')}</div>
            </td>
            <td class="text-xs" style="color: var(--ink-secondary);">${escapeHtml(rt.painPoint || '')}</td>
            <td class="text-xs font-medium" style="color: #1E6F5C;">${escapeHtml(rt.unlock || '')}</td>
          </tr>
        `;
      }).join('');

      const glossaryGridHtml = glossary.map(g => `
        <div class="bg-[#FAF7F2] rounded-lg p-2.5 border border-[#E6DEC8] space-y-1">
          <div class="flex items-center justify-between gap-1.5">
            <span class="font-bold text-xs" style="color: var(--ink-primary);">${escapeHtml(g.term || '')}</span>
            <a href="#comp-ch-${escapeHtml(g.chapterSlug)}" onclick="event.preventDefault(); handleSpineChapterClick('${escapeHtml(g.chapterSlug)}')" class="mono text-[9.5px] font-bold px-1.5 py-0.5 rounded bg-white border border-[#E6DEC8]" style="color: var(--accent-terra);">
              Ch ${String(g.chapterNumber).padStart(2, '0')}
            </a>
          </div>
          <p class="text-[11px] leading-snug" style="color: var(--ink-secondary); margin: 0;">${escapeHtml(g.meaning || '')}</p>
          ${g.formula ? `<div class="mono text-[10px] px-1.5 py-0.5 rounded bg-white border border-[#E6DEC8] inline-block" style="color: var(--accent-indigo);">${escapeHtml(g.formula)}</div>` : ''}
        </div>
      `).join('');

      const chaptersHtml = chapters.map((ch, cIdx) => {
        const chNum = String(ch.chapterNumber).padStart(2, '0');
        const steps = (ch.steps && ch.steps.length)
          ? ch.steps
          : [{ stepNumber: 1, shortLabel: 'Full Chapter', title: ch.title, markdown: ch.markdownBody }];

        const stepsHtml = steps.map((stObj, sIdx) => {
          const layerKey = `step${Math.min(5, sIdx + 1)}`;
          const isVis = Boolean(layers[layerKey]);
          return `
            <div data-comp-layer="${layerKey}" class="${isVis ? '' : 'hidden'} kb-prose">
              ${renderEditorialMarkdown(stObj.markdown || '')}
            </div>
          `;
        }).join('\n');

        const vocabBarHtml = (ch.pretraining && ch.pretraining.length) ? `
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 my-3">
            ${ch.pretraining.map(pt => `
              <div class="bg-[#FAF7F2] rounded-lg p-2.5 border border-[#E6DEC8] space-y-1">
                <div class="font-bold text-xs" style="color: var(--ink-primary);">${escapeHtml(pt.term || '')}</div>
                <p class="text-[11px] leading-snug" style="color: var(--ink-secondary); margin:0;">${escapeHtml(pt.meaning || '')}</p>
                ${pt.formula ? `<div class="mono text-[10px] px-1.5 py-0.5 rounded bg-white border border-[#E6DEC8] inline-block" style="color: var(--accent-terra);">${escapeHtml(pt.formula)}</div>` : ''}
              </div>
            `).join('')}
          </div>
        ` : '';

        const qaList = ch.selfCheckKey || [];
        const qaHtml = qaList.length ? `
          <div data-comp-layer="qa" class="${layers.qa ? '' : 'hidden'} mt-5 pt-4 border-t border-[#E6DEC8] space-y-2.5">
            <div class="flex items-center justify-between gap-2">
              <span class="mono text-[11px] font-bold uppercase" style="color: var(--accent-sage);">
                ✓ Ch ${chNum} Rapid Self-Check Q&amp;A Key (${qaList.length} Questions · Answer + Staff Rationale)
              </span>
              ${ch.labPath ? `<span class="mono text-[10.5px]" style="color: var(--ink-muted);">🧪 Paired Lab: <code>${escapeHtml(ch.labPath)}</code></span>` : ''}
            </div>
            <div class="grid grid-cols-1 gap-2.5">
              ${qaList.map((qItem, qIdx) => `
                <div class="rounded-xl p-3 bg-[#F3FBF8] border border-[#B7E4D8] space-y-1.5">
                  <div class="flex items-center justify-between gap-2">
                    <span class="mono text-[10px] font-bold uppercase" style="color: #1E6F5C;">Q${qIdx + 1} · ${escapeHtml(qItem.kind || 'Scenario Check')}</span>
                  </div>
                  <div class="text-xs font-bold" style="color: var(--ink-primary);">${escapeHtml(qItem.question || '')}</div>
                  <div onclick="this.classList.add('revealed')" class="comp-qa-answer-target ${state.compendiumBlurAnswers ? 'qa-answer-blur' : ''} text-xs space-y-1 pt-1 border-t border-[#D1FAE5]">
                    <div style="color: #065F46;"><strong>✓ Answer:</strong> ${escapeHtml(qItem.correctAnswer || '')}</div>
                    ${qItem.explanation ? `<div class="text-[11.5px]" style="color: #1F3A33;"><strong>Why:</strong> ${escapeHtml(qItem.explanation)}</div>` : ''}
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : '';

        return `
          <article id="comp-ch-${escapeHtml(ch.slug)}" class="compendium-chapter-card space-y-3">
            <div class="flex flex-wrap items-start justify-between gap-3 pb-3 border-b border-[#E6DEC8]">
              <div class="space-y-1">
                <div class="mono text-[11px] font-bold uppercase" style="color: var(--accent-terra);">
                  CHAPTER ${chNum} OF ${String(chapters.length).padStart(2, '0')} · ${escapeHtml(ch.moduleTitle || ('MODULE ' + ch.moduleNumber))} · ${ch.readingTimeMinutes} MIN (${(ch.wordCount || 0).toLocaleString()} WORDS)
                </div>
                <h2 style="font-size: 1.42rem; font-weight: 700; line-height: 1.28; margin: 0;">
                  Ch ${chNum}: ${escapeHtml(ch.title)}
                </h2>
                <p class="text-xs" style="color: var(--ink-secondary); margin: 0;">${escapeHtml(ch.summary || '')}</p>
              </div>
              <div class="flex items-center gap-2 shrink-0">
                <button onclick="toggleRoadmapItemDone('${escapeHtml(ch.slug)}')" class="mark-done-btn ${ch.mastered ? 'completed' : ''}" title="Mark this Chapter as Done in your Staff SDET Roadmap">
                  ${ch.mastered ? '✓ Completed' : '○ Mark Done'}
                </button>
                <button onclick="state.kbReadingMode='guided'; openTextbookChapter('${escapeHtml(ch.slug)}', false);" class="btn-subtle" style="padding: 5px 10px; font-size: 0.72rem;" title="Switch to Guided 4-Step Mode for this specific chapter">
                  🎯 Open in Guided Mode ↗
                </button>
              </div>
            </div>

            <!-- Compact Causal Continuity Ribbon -->
            <div class="continuity-bridge text-xs" style="margin-top: 8px;">
              <div>
                <div class="mono text-[10px] font-bold uppercase" style="color: var(--accent-sage);">⏪ Context</div>
                <p class="mt-0.5 leading-snug" style="color: var(--ink-secondary); margin:0;">${escapeHtml((ch.continuity && ch.continuity.previously) || '')}</p>
              </div>
              <div>
                <div class="mono text-[10px] font-bold uppercase" style="color: var(--accent-terra);">💥 Bottleneck</div>
                <p class="mt-0.5 leading-snug" style="color: var(--ink-secondary); margin:0;">${escapeHtml((ch.continuity && ch.continuity.painPoint) || '')}</p>
              </div>
              <div>
                <div class="mono text-[10px] font-bold uppercase" style="color: var(--accent-indigo);">🎯 Staff Unlock</div>
                <p class="mt-0.5 leading-snug" style="color: var(--ink-secondary); margin:0;">${escapeHtml((ch.continuity && ch.continuity.unlock) || '')}</p>
              </div>
            </div>

            <!-- Inline Chapter Vocabulary Strip -->
            ${vocabBarHtml}

            <!-- Unabridged 4-Step Technical Content (Story + Mermaid + Code + Contrast + Staff Math & Gotchas) -->
            <div class="space-y-2">
              ${stepsHtml}
            </div>

            <!-- Inline Self-Check Q&A Answer Key -->
            ${qaHtml}
          </article>
        `;
      }).join('\n');

      compContainer.innerHTML = `
        <!-- Sticky Revision Control Bar -->
        <div class="revise-sticky-bar space-y-2.5">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="mono text-[10px] font-bold uppercase mr-1" style="color: var(--ink-muted);">LAYERS:</span>
              <button id="comp-layer-btn-step1" onclick="toggleCompendiumLayer('step1')" class="revise-filter-pill ${layers.step1 ? 'active' : ''}">✓ 1. Story</button>
              <button id="comp-layer-btn-step2" onclick="toggleCompendiumLayer('step2')" class="revise-filter-pill ${layers.step2 ? 'active' : ''}">✓ 2. Starter &amp; CLI</button>
              <button id="comp-layer-btn-step3" onclick="toggleCompendiumLayer('step3')" class="revise-filter-pill ${layers.step3 ? 'active' : ''}">✓ 3. How-To &amp; Contrast</button>
              <button id="comp-layer-btn-step4" onclick="toggleCompendiumLayer('step4')" class="revise-filter-pill ${layers.step4 ? 'active' : ''}">✓ 4. Big Tech &amp; Math</button>
              <button id="comp-layer-btn-step5" onclick="toggleCompendiumLayer('step5')" class="revise-filter-pill ${layers.step5 ? 'active' : ''}">✓ 5. Cheat-Sheets &amp; Pitch</button>
              <button id="comp-layer-btn-qa" onclick="toggleCompendiumLayer('qa')" class="revise-filter-pill ${layers.qa ? 'active' : ''}">✓ Q&amp;A Key</button>
              <button id="comp-cram-preset-btn" onclick="toggleCompendiumCramPreset()" class="revise-filter-pill ${state.compendiumCramOnly ? 'active' : ''}" title="1-Click Pre-Interview Cram Mode: Show Cheat-Sheets, 60s Interview Pitches &amp; Q&amp;A Keys Only">${state.compendiumCramOnly ? '⚡ Cram Mode ON (Show All)' : '⚡ Interview Cram'}</button>
            </div>
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="mono text-[10px] font-bold uppercase" style="color: var(--ink-muted);">GLOBAL CODE:</span>
              <button id="comp-lang-btn-python" onclick="switchAllCompendiumCodeLang('python')" class="revise-filter-pill ${prefLang === 'python' ? 'active' : ''}">🐍 All Python 3</button>
              <button id="comp-lang-btn-java" onclick="switchAllCompendiumCodeLang('java')" class="revise-filter-pill ${prefLang === 'java' ? 'active' : ''}">☕ All Java 17</button>
              <button id="comp-lang-btn-both" onclick="switchAllCompendiumCodeLang('both')" class="revise-filter-pill ${prefLang === 'both' ? 'active' : ''}">⚖️ Split Both</button>
            </div>
          </div>

          <div class="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-[#ECE5D5]">
            <div class="flex items-center gap-2 flex-1 min-w-[220px]">
              <input
                type="search"
                placeholder="Instant filter across all ${chapters.length} chapters on this page (e.g. Rogan-Gladen, LIFO, Token Bucket)..."
                oninput="filterCompendiumChapters(this.value)"
                class="mono text-xs px-3 py-1.5 rounded-lg border border-[#E6DEC8] bg-white w-full focus:outline-none focus:border-zinc-900"
              />
              <span id="comp-filter-count" class="mono text-[10.5px] font-semibold whitespace-nowrap" style="color: var(--ink-muted);">
                ${chapters.length} Chapters
              </span>
            </div>
            <div class="flex flex-wrap items-center gap-1.5">
              <button id="comp-qa-blur-btn" onclick="toggleCompendiumAnswerBlur()" class="revise-filter-pill ${!state.compendiumBlurAnswers ? 'active' : ''}">
                ${state.compendiumBlurAnswers ? '🙈 Answers Blurred (Click to Reveal)' : '👁️ Answers Shown'}
              </button>
              <button onclick="window.print()" class="revise-filter-pill" title="Print or Save Complete Course Compendium as PDF">
                🖨️ Print / PDF
              </button>
              <button onclick="toggleCenterContentExpand()" class="expand-cta-btn" title="Expand Revision Guide Only — Hide Sidebars &amp; Topbar (Shortcut: Z or F)">
                ⤢ Expand Content · Z
              </button>
            </div>
          </div>
        </div>

        <!-- Executive Course Red-Thread Architecture Map (Ch 01 -> Ch N) -->
        <section class="news-card space-y-3" style="padding: 18px 20px; background: #FFFDF9;">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <div class="mono text-[10.5px] font-bold uppercase" style="color: var(--accent-terra);">
                🗺️ EXECUTIVE COURSE ARCHITECTURE MAP · CAUSAL PROGRESSION (CH 01 → CH ${String(chapters.length).padStart(2, '0')})
              </div>
              <h3 style="font-size: 1.12rem; font-weight: 700; margin-top: 2px;">
                How All ${chapters.length} Chapters Connect as One System
              </h3>
            </div>
            <span class="mono text-[10.5px] px-2.5 py-1 rounded-full bg-[#F3EDE2] font-semibold" style="color: var(--ink-secondary);">
              Click any row to jump to chapter ↓
            </span>
          </div>
          <div class="overflow-x-auto kb-prose">
            <table style="margin: 0;">
              <thead>
                <tr>
                  <th>Ch</th>
                  <th>Chapter &amp; Module</th>
                  <th>Real-World Pain Point / Trigger</th>
                  <th>Staff Unlock &amp; Core Invariant</th>
                </tr>
              </thead>
              <tbody>
                ${redThreadRowsHtml}
              </tbody>
            </table>
          </div>

          <details class="pt-2 border-t border-[#ECE5D5]">
            <summary class="mono text-xs font-bold cursor-pointer" style="color: var(--accent-indigo);">
              📖 Expand Complete Course-Wide Master Glossary (${glossary.length} Primitives &amp; Formulas Across All ${chapters.length} Chapters)
            </summary>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 mt-3">
              ${glossaryGridHtml}
            </div>
          </details>
        </section>

        <!-- Continuous Unabridged Chapter Stream (Ch 01 -> Ch N) -->
        <div class="space-y-6">
          ${chaptersHtml}
        </div>
      `;
    }

    function selectKbStep(stepIdx) {
      if (!state.activeKbChapter) return;
      const steps = state.activeKbChapter.steps || [];
      state.kbActiveStepIdx = Math.max(0, Math.min(Math.max(steps.length - 1, 0), stepIdx));
      const wtSlides = state.activeKbChapter.walkthrough || [];
      if (wtSlides.length && !state.wtPlaying) {
        state.wtSlideIdx = Math.min(wtSlides.length - 1, state.kbActiveStepIdx);
        renderWalkthroughFrame();
      }
      if (state.kbReadingMode !== 'guided') {
        setKbReadingMode('guided');
        return;
      }
      renderActiveKbStepView();
      const stepBar = document.getElementById('kb-step-bar');
      if (stepBar) stepBar.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function advanceKbStep(delta) {
      if (!state.activeKbChapter) return;
      const steps = state.activeKbChapter.steps || [];
      const nextIdx = state.kbActiveStepIdx + delta;
      if (nextIdx >= steps.length && delta > 0) {
        if (state.activeKbChapter.nextChapter) {
          openTextbookChapter(state.activeKbChapter.nextChapter.slug);
        }
        return;
      }
      selectKbStep(Math.max(0, nextIdx));
    }

    function renderActiveKbStepView() {
      const ch = state.activeKbChapter;
      if (!ch) return;
      const steps = (ch.steps && ch.steps.length)
        ? ch.steps
        : [{ stepNumber: 1, shortLabel: '🌱 1. Guided Lesson', title: ch.title, markdown: ch.markdownBody, estMinutes: ch.readingTimeMinutes || 10 }];

      const totalSteps = steps.length;
      const curIdx = Math.min(state.kbActiveStepIdx, totalSteps - 1);
      const isGuided = state.kbReadingMode === 'guided';

      // 1. Render 4-Step Stepper Bar
      const stepBar = document.getElementById('kb-step-bar');
      if (stepBar) {
        stepBar.classList.toggle('hidden', !isGuided || totalSteps <= 1);
        stepBar.innerHTML = steps.map((st, idx) => {
          const isAct = idx === curIdx;
          const isDone = idx < curIdx;
          return `
            <button onclick="selectKbStep(${idx})" class="lesson-step-btn ${isAct ? 'active' : (isDone ? 'done' : '')}">
              <div class="flex items-center justify-between mono text-[10px] font-bold" style="color: ${isAct ? 'var(--accent-terra)' : (isDone ? 'var(--accent-sage)' : 'var(--ink-muted)')};">
                <span>${isDone ? '✓ ' : (isAct ? '● ' : '')}STEP ${idx + 1}</span>
                <span>${st.estMinutes || 3}m</span>
              </div>
              <div class="text-xs font-bold mt-0.5 truncate" style="color: var(--ink-primary);">
                ${escapeHtml((st.shortLabel || st.title || '').replace(/^[^\w]*\d+\.\s*/, ''))}
              </div>
            </button>
          `;
        }).join('');
      }

      // 2. Render Body Markdown (Single bite in Guided mode vs Full scroll in Staff mode)
      const bodyEl = document.getElementById('kb-chapter-body');
      if (bodyEl) {
        const mdToRender = isGuided ? (steps[curIdx] ? steps[curIdx].markdown : ch.markdownBody) : ch.markdownBody;
        bodyEl.innerHTML = renderEditorialMarkdown(mdToRender);
      }

      // 3. Contextual Visibility for Simulator (Step 3), Lab & Quiz (Last Step)
      const simSec = document.getElementById('kb-sec-simulator');
      const labSec = document.getElementById('kb-lab-callout');
      const quizSec = document.getElementById('kb-sec-quiz');
      const contBar = document.getElementById('kb-step-continue-bar');

      const simStepTarget = Math.min(2, totalSteps - 1);
      const lastStepTarget = totalSteps - 1;

      if (simSec) simSec.classList.toggle('hidden', isGuided && curIdx !== simStepTarget);
      if (labSec) labSec.classList.toggle('hidden', isGuided && curIdx !== lastStepTarget);
      if (quizSec) quizSec.classList.toggle('hidden', isGuided && curIdx !== lastStepTarget);
      if (contBar) {
        contBar.classList.toggle('hidden', !isGuided);
        const prevBtn = document.getElementById('kb-prev-step-btn');
        const nextBtn = document.getElementById('kb-next-step-btn');
        if (prevBtn) prevBtn.style.visibility = curIdx === 0 ? 'hidden' : 'visible';
        if (nextBtn) {
          if (curIdx < totalSteps - 1) {
            nextBtn.textContent = `Complete Step ${curIdx + 1} & Continue to Step ${curIdx + 2} →`;
          } else if (ch.nextChapter) {
            nextBtn.textContent = `✓ Finish & Start Next Chapter (Ch ${String(ch.nextChapter.chapterNumber).padStart(2, '0')}) →`;
          } else {
            nextBtn.textContent = `🏆 Course Volume Complete!`;
          }
        }
      }

      // 4. Update Right-Rail Journey Progress Ring & Just-in-Time Vocabulary
      const pct = isGuided ? Math.round(((curIdx + 1) / totalSteps) * 100) : 100;
      const circumference = 163.36;
      const offset = circumference - (pct / 100) * circumference;
      const arc = document.getElementById('kb-journey-ring-arc');
      const pctLabel = document.getElementById('kb-journey-ring-pct');
      const stepTitle = document.getElementById('kb-journey-step-title');
      const altPill = document.getElementById('kb-journey-altitude-pill');
      const hintEl = document.getElementById('kb-journey-upnext-hint');

      const altitudes = totalSteps >= 5 ? [
        ['🌱 Plain-English Story', 'Zero jargon — build intuition first!'],
        ['🔨 Starter & CLI Run', 'Terminal setup + subgoal-labeled code!'],
        ['🛠️ Practitioner & Sim', 'Everyday configs, debugging & POE sim!'],
        ['🏢 Big Tech & Staff Math', '30–500+ service scale, equations & blueprint!'],
        ['📋 Cheat-Sheet & Pitch', 'Lookup table, 60s pitch, 1-click lab & quiz!']
      ] : [
        ['🌱 Plain-English Story', 'Zero jargon — build intuition first!'],
        ['🔨 First Lines of Code', 'Hands-on baby step — run & see it work!'],
        ['⚡ Real-World & Sim', 'Test where naive code breaks at scale.'],
        ['🚀 Staff Mastery Gate', 'Production blueprint, 1-click lab & quiz!']
      ];
      const maxAltIdx = altitudes.length - 1;
      const altInfo = altitudes[Math.min(isGuided ? curIdx : maxAltIdx, maxAltIdx)];
      if (arc) arc.setAttribute('stroke-dashoffset', String(offset.toFixed(2)));
      if (pctLabel) pctLabel.textContent = `${pct}%`;
      if (stepTitle) stepTitle.textContent = isGuided ? `Step ${curIdx + 1} of ${totalSteps}` : `Full Staff View (${totalSteps} Steps)`;
      if (altPill) altPill.textContent = altInfo[0];
      if (hintEl) hintEl.textContent = altInfo[1];

      renderPretrainingStrip(ch.pretraining || []);
    }

    function renderPoePrompt(poe) {
      const box = document.getElementById('kb-poe-box');
      const qEl = document.getElementById('kb-poe-question');
      const optsEl = document.getElementById('kb-poe-options');
      const revEl = document.getElementById('kb-poe-reveal');
      const statusEl = document.getElementById('kb-poe-status');
      if (!box || !qEl || !optsEl || !revEl) return;

      if (!poe || !poe.question || !Array.isArray(poe.options) || !poe.options.length) {
        box.classList.add('hidden');
        return;
      }
      box.classList.remove('hidden');
      state.poeSelectedIdx = null;
      qEl.textContent = poe.question;
      statusEl.textContent = 'Commit Prediction First';
      revEl.classList.add('hidden');
      revEl.innerHTML = '';

      optsEl.innerHTML = poe.options.map((opt, idx) => `
        <button
          id="poe-opt-${idx}"
          onclick="selectPoeOption(${idx})"
          class="nav-tab text-left"
          style="padding: 6px 11px; font-size: 0.76rem; background: #FFFFFF;"
        >
          ${escapeHtml(opt)}
        </button>
      `).join('');
    }

    function selectPoeOption(optIdx) {
      if (!state.activeKbChapter || !state.activeKbChapter.predictionPrompt) return;
      const poe = state.activeKbChapter.predictionPrompt;
      const ansIdx = Number(poe.answerIndex || 0);
      const isCorrect = optIdx === ansIdx;
      state.poeSelectedIdx = optIdx;

      (poe.options || []).forEach((_, idx) => {
        const btn = document.getElementById(`poe-opt-${idx}`);
        if (!btn) return;
        if (idx === ansIdx) {
          btn.style.background = '#E6F4F0';
          btn.style.borderColor = '#1E6F5C';
          btn.style.color = '#064E3B';
          btn.style.fontWeight = '700';
        } else if (idx === optIdx && !isCorrect) {
          btn.style.background = '#FFF5F5';
          btn.style.borderColor = '#E53E3E';
          btn.style.color = '#9B2C2C';
        }
      });

      const statusEl = document.getElementById('kb-poe-status');
      if (statusEl) statusEl.textContent = isCorrect ? '✓ Prediction Verified!' : '💡 Hypothesis Updated — Step Simulator Below';

      const revEl = document.getElementById('kb-poe-reveal');
      if (revEl) {
        revEl.classList.remove('hidden');
        revEl.innerHTML = `<strong>${isCorrect ? '✓ Spot-on Intuition:' : '🔍 First-Principles Insight:'}</strong> ${escapeHtml(poe.explanation || 'Step through the state simulator below to observe the invariant in action.')}`;
      }
    }

    async function openTextbookChapter(slug, switchScreen = true) {
      if (switchScreen) showView('textbook');
      stopWalkthroughPlayback();
      if (state.kbReadingMode === 'revise') {
        state.kbReadingMode = 'guided';
        if (!state.kbUserWidthOverride && typeof setKbContentWidth === 'function') {
          setKbContentWidth('comfort', false);
        }
        const gBtn = document.getElementById('kb-mode-guided');
        const fBtn = document.getElementById('kb-mode-full');
        const rBtn = document.getElementById('kb-mode-revise');
        if (gBtn) gBtn.classList.add('active');
        if (fBtn) fBtn.classList.remove('active');
        if (rBtn) rBtn.classList.remove('active');
        const compContainer = document.getElementById('kb-compendium-container');
        if (compContainer) compContainer.classList.add('hidden');
        ['kb-continuity-bridge', 'kb-chapter-body', 'kb-prev-next-bar'].forEach(id => {
          const el = document.getElementById(id);
          if (el) el.classList.remove('hidden');
        });
      }
      try {
        const res = await fetch(`/api/kb/chapter?slug=${encodeURIComponent(slug)}`);
        if (!res.ok) return;
        const ch = await res.json();
        state.activeKbChapter = ch;
        state.kbActiveStepIdx = 0;
        state.wtSlideIdx = 0;
        state.wtMediaMode = 'storyboard';
        if (ch.courseId) state.expandedCourseId = ch.courseId;
        state.kbQuizSelections = {};
        renderKbChaptersSpine();

        const courseLabel = (ch.courseTitle || ch.volume || '').toUpperCase();
        const modLabel = ch.moduleNumber ? `MOD ${ch.moduleNumber}` : '';
        document.getElementById('kb-chapter-kicker').textContent =
          `${courseLabel} · ${modLabel ? modLabel + ' · ' : ''}CH ${String(ch.chapterNumber).padStart(2, '0')} · ${ch.readingTimeMinutes} MIN GUIDED`;
        document.getElementById('kb-chapter-title').textContent = ch.title;

        const sumEl = document.getElementById('kb-chapter-summary');
        if (sumEl) sumEl.textContent = ch.summary || '';

        const lvlPill = document.getElementById('kb-chapter-level-pill');
        if (lvlPill) {
          lvlPill.textContent = ch.levelTag || 'Zero → Staff';
          lvlPill.style.background = '#F3EDE2';
          lvlPill.style.color = ch.courseAccent || 'var(--accent-terra)';
        }

        const mBadge = document.getElementById('kb-chapter-mastery-badge');
        if (ch.mastered) {
          mBadge.textContent = ch.quizTotal ? `✓ Mastered (${ch.quizScore}/${ch.quizTotal})` : `✓ Completed in Roadmap`;
          mBadge.className = 'mono text-[11px] font-semibold px-2.5 py-1 rounded-full bg-[#E6F4F0] text-[#1E6F5C] border border-[#B7E4D8]';
        } else {
          mBadge.textContent = ch.quizTotal ? `Quiz: ${ch.quizScore || 0}/${ch.quizTotal}` : `${ch.quizCount || (ch.quizzes || []).length} Quiz Questions`;
          mBadge.className = 'mono text-[11px] font-semibold px-2.5 py-1 rounded-full bg-[#F3EDE2] border border-[#E6DEC8]';
        }

        const kbDoneBtn = document.getElementById('kb-mark-done-btn');
        if (kbDoneBtn) {
          kbDoneBtn.classList.toggle('completed', Boolean(ch.mastered));
          kbDoneBtn.textContent = ch.mastered ? '✓ Completed' : '○ Mark Done';
        }
        renderRoadmapEverywhere();

        document.getElementById('kb-chapter-tags').innerHTML = (ch.tags || []).map(t => `
          <span class="tag">#${escapeHtml(t)}</span>
        `).join('');

        // Populate Udemy Continuity Story Bridge
        const cont = ch.continuity || {};
        const prevEl = document.getElementById('kb-cont-prev');
        const painEl = document.getElementById('kb-cont-pain');
        const unlkEl = document.getElementById('kb-cont-unlock');
        if (prevEl) prevEl.textContent = cont.previously || 'Welcome! Zero prior background needed.';
        if (painEl) painEl.textContent = cont.painPoint || '';
        if (unlkEl) unlkEl.textContent = cont.unlock || ch.summary || '';

        // Populate 90s Narrated Visual Walkthrough + Video Toggle
        switchWalkthroughMediaMode('storyboard');
        renderWalkthroughFrame();

        // Populate POE prompt, Lab path, Quiz & Guided 4-Step View
        renderPoePrompt(ch.predictionPrompt || null);
        document.getElementById('kb-lab-path-label').textContent = ch.labPath || ch.sourcePath;
        const labConsole = document.getElementById('kb-lab-console');
        if (labConsole) labConsole.classList.add('hidden');

        renderKbQuizQuestions(ch.quizzes || []);
        renderActiveKbStepView();

        const pnBar = document.getElementById('kb-prev-next-bar');
        if (pnBar) {
          const prevBtn = ch.prevChapter
            ? `<button onclick="openTextbookChapter('${ch.prevChapter.slug}')" class="btn-subtle">← Ch ${String(ch.prevChapter.chapterNumber).padStart(2, '0')}: ${escapeHtml(ch.prevChapter.title.slice(0, 34))}</button>`
            : `<span></span>`;
          const markFooterBtn = `<button onclick="toggleActiveChapterDone()" id="kb-footer-mark-done-btn" class="mark-done-btn ${ch.mastered ? 'completed' : ''}" title="Mark or unmark this chapter as Done in your Staff SDET Roadmap">${ch.mastered ? '✓ Chapter Completed' : '○ Mark Chapter Done'}</button>`;
          const nextBtn = ch.nextChapter
            ? `<button onclick="openTextbookChapter('${ch.nextChapter.slug}')" class="btn-primary">Next: Ch ${String(ch.nextChapter.chapterNumber).padStart(2, '0')}: ${escapeHtml(ch.nextChapter.title.slice(0, 34))} →</button>`
            : `<span class="mono text-xs font-semibold" style="color: var(--accent-sage);">✓ End of Course Volume</span>`;
          pnBar.innerHTML = `${prevBtn}<div class="flex flex-wrap items-center gap-2">${markFooterBtn}${nextBtn}</div>`;
        }

        const relEl = document.getElementById('kb-related-news');
        relEl.innerHTML = (ch.relatedNews || []).map(art => `
          <div class="news-card space-y-1">
            <div class="flex items-center justify-between mono text-[10px] font-semibold" style="color: var(--accent-terra);">
              <span>${escapeHtml(art.sourceName)}</span>
              <span>${escapeHtml(art.publishedAt)}</span>
            </div>
            <a href="${escapeHtml(art.url)}" target="_blank" rel="noopener" class="font-bold text-xs hover:underline block leading-snug" style="color: var(--ink-primary);">
              ${escapeHtml(art.title)} ↗
            </a>
            <p class="text-[11px] leading-relaxed" style="color: var(--ink-secondary);">${escapeHtml(art.summary)}</p>
          </div>
        `).join('') || `<div class="text-xs" style="color: var(--ink-muted);">No cross-linked articles yet.</div>`;

        const mappedVizId = VIZ_ALIAS_MAP[ch.visualizerId] || ch.visualizerId || 'arch-endpoint-cloud-sync';
        await loadKbInlineSimulator(mappedVizId);
      } catch (_) {}
    }

    async function runPairedChapterLab() {
      if (!state.activeKbChapter) return;
      const rawLabPath = (state.activeKbChapter.labPath || '').replace(/\/+$/, '');
      if (!rawLabPath) return;

      const btn = document.getElementById('kb-run-lab-btn');
      const consoleBox = document.getElementById('kb-lab-console');
      const statusEl = document.getElementById('kb-lab-console-status');
      const latencyEl = document.getElementById('kb-lab-console-latency');
      const outEl = document.getElementById('kb-lab-console-output');
      if (btn) btn.textContent = '⏳ Running Local Lab...';
      if (consoleBox) consoleBox.classList.remove('hidden');
      if (statusEl) statusEl.textContent = '⏳ Executing deterministic Python 3 / Java 17 harness...';
      if (outEl) outEl.textContent = '';

      try {
        const wbId = WORKBENCH_PATH_TO_ID[rawLabPath];
        if (wbId) {
          const res = await fetch('/api/workbench/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ itemId: wbId })
          });
          const data = await res.json();
          const ok = data.status === 'PASS';
          statusEl.textContent = `${ok ? '✓ PASS' : '✗ FAIL'} · ${data.title || rawLabPath}`;
          statusEl.className = ok ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold';
          latencyEl.textContent = `${data.durationMs || 0}ms`;
          outEl.textContent = data.output || JSON.stringify(data, null, 2);
        } else {
          const targetSlug = rawLabPath.split('/').pop();
          const res = await fetch('/api/run-test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: targetSlug, lang: 'all' })
          });
          const data = await res.json();
          const ok = data.status === 'PASS' || data.status === 'PASSED';
          statusEl.textContent = `${ok ? '✓ PASS (Python 3 + Java 17)' : '✗ ' + (data.status || 'FAIL')} · ${targetSlug}`;
          statusEl.className = ok ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold';
          latencyEl.textContent = `${data.totalDurationMs || 0}ms`;
          const lines = (data.runs || []).map(r => `[${(r.language || '').toUpperCase()} · ${r.status} · ${r.durationMs || 0}ms]\n${(r.stdout || r.stderr || 'All assertions passed.').trim()}`);
          outEl.textContent = lines.join('\n\n') || JSON.stringify(data, null, 2);
        }
      } catch (err) {
        statusEl.textContent = '✗ Lab Execution Error';
        outEl.textContent = String(err);
      }
      if (btn) btn.textContent = '▶ Run Paired Lab Locally';
    }

    async function loadKbInlineSimulator(vizId) {
      try {
        const res = await fetch('/api/visualize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ visualizerId: vizId })
        });
        if (!res.ok) return;
        const trace = await res.json();
        document.getElementById('kb-sim-title').textContent = trace.title || 'Interactive Architecture Trace';
        state.kbSimSteps = trace.steps || [];
        state.kbSimIdx = 0;
        renderKbSimulatorStep();
      } catch (_) {}
    }

    function stepKbSimulator(delta) {
      if (!state.kbSimSteps.length) return;
      state.kbSimIdx = Math.max(0, Math.min(state.kbSimSteps.length - 1, state.kbSimIdx + delta));
      renderKbSimulatorStep();
    }

    function renderKbSimulatorStep() {
      if (!state.kbSimSteps.length) return;
      const step = state.kbSimSteps[state.kbSimIdx];
      document.getElementById('kb-sim-step-pill').textContent = `${state.kbSimIdx + 1} / ${state.kbSimSteps.length}`;
      document.getElementById('kb-sim-narration').textContent = `${step.title ? step.title + ' — ' : ''}${step.narration || ''}`;
      document.getElementById('kb-sim-codeline').textContent = step.codeLine || '';

      const grid = document.getElementById('kb-sim-compare-grid');
      const leftMetrics = Object.entries(step.leftMetrics || {}).map(([k, v]) => `<div class="flex justify-between"><span style="color:var(--ink-muted);">${escapeHtml(k)}:</span><strong class="mono">${escapeHtml(v)}</strong></div>`).join('');
      const rightMetrics = Object.entries(step.rightMetrics || {}).map(([k, v]) => `<div class="flex justify-between"><span style="color:var(--ink-muted);">${escapeHtml(k)}:</span><strong class="mono" style="color:var(--accent-sage);">${escapeHtml(v)}</strong></div>`).join('');

      grid.innerHTML = `
        <div class="bg-white rounded-lg p-3.5 border border-[#E6DEC8] space-y-1.5">
          <div class="font-bold border-b border-[#EFEAE0] pb-1">${escapeHtml(step.leftTitle || 'Baseline State')}</div>
          <div class="space-y-1 text-[11px]">${leftMetrics}</div>
        </div>
        <div class="bg-white rounded-lg p-3.5 border-2 border-[#1E6F5C] space-y-1.5">
          <div class="font-bold border-b border-[#EFEAE0] pb-1" style="color: var(--accent-sage);">${escapeHtml(step.rightTitle || 'Production Architecture')}</div>
          <div class="space-y-1 text-[11px]">${rightMetrics}</div>
        </div>
      `;
    }

    function renderKbQuizQuestions(quizzes, feedbackMap = null) {
      const container = document.getElementById('kb-quiz-questions');
      const resPill = document.getElementById('kb-quiz-result-pill');
      if (!feedbackMap) resPill.classList.add('hidden');

      container.innerHTML = (quizzes || []).map((q, qIdx) => {
        const qid = q.id || `q${qIdx + 1}`;
        const fb = feedbackMap ? feedbackMap[qid] : null;
        return `
          <div class="bg-white rounded-xl p-4 border border-[#CBE6DB] space-y-2.5">
            <div class="font-bold text-sm">Q${qIdx + 1}. ${escapeHtml(q.question)}</div>
            <div class="space-y-1.5">
              ${(q.options || []).map((opt, optIdx) => {
                const selected = state.kbQuizSelections[qid] === optIdx;
                let borderCls = selected ? 'border-zinc-900 bg-[#FAF7F2] font-semibold' : 'border-[#E6DEC8] hover:bg-[#FAF7F2]';
                if (fb) {
                  if (optIdx === fb.answerIndex) borderCls = 'border-emerald-600 bg-emerald-50 font-bold text-emerald-950';
                  else if (selected && !fb.correct) borderCls = 'border-rose-500 bg-rose-50 text-rose-900';
                }
                return `
                  <label onclick="selectKbQuizOption('${qid}', ${optIdx})" class="flex items-start gap-2.5 p-2.5 rounded-lg border cursor-pointer text-xs ${borderCls}">
                    <input type="radio" name="quiz-${qid}" ${selected ? 'checked' : ''} class="mt-0.5" />
                    <span>${escapeHtml(opt)}</span>
                  </label>
                `;
              }).join('')}
            </div>
            ${fb ? `
              <div class="p-3 rounded-lg text-xs ${fb.correct ? 'bg-emerald-50 text-emerald-900 border border-emerald-200' : 'bg-amber-50 text-amber-950 border border-amber-200'}">
                <strong>${fb.correct ? '✓ Correct:' : '💡 First-Principles Explanation:'}</strong> ${escapeHtml(fb.explanation)}
              </div>
            ` : ''}
          </div>
        `;
      }).join('');
    }

    function selectKbQuizOption(qid, optIdx) {
      state.kbQuizSelections[qid] = optIdx;
    }

    async function submitActiveKbQuiz() {
      if (!state.activeKbChapter) return;
      const slug = state.activeKbChapter.slug;
      try {
        const res = await fetch('/api/kb/quiz', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ slug, answers: state.kbQuizSelections })
        });
        if (!res.ok) return;
        const data = await res.json();
        const fbMap = {};
        (data.feedback || []).forEach(f => { fbMap[f.id] = f; });
        renderKbQuizQuestions(state.activeKbChapter.quizzes || [], fbMap);

        const pill = document.getElementById('kb-quiz-result-pill');
        pill.classList.remove('hidden');
        pill.textContent = data.mastered
          ? `🏆 Mastered! ${data.score}/${data.total} Correct`
          : `Score: ${data.score}/${data.total} — Review explanations below`;
        pill.className = data.mastered
          ? 'mono px-3 py-1 rounded-full text-xs font-semibold bg-emerald-600 text-white'
          : 'mono px-3 py-1 rounded-full text-xs font-semibold bg-amber-200 text-amber-950';

        await loadKbCatalogAndDefaultChapter();
        await loadTracksAndHome();
        await loadRoadmapStatus();
      } catch (_) {}
    }

    /* ========================================================================
       ENGINEERING PULSE NEWSFEED CONTROLLER
       ======================================================================== */
    async function loadNewsfeedView(category = 'all', bookmarkedOnly = false) {
      state.newsCategory = category;
      state.newsBookmarkedOnly = bookmarkedOnly;

      ['all', 'system-design', 'ai-engineering', 'core-cs', 'sdet-architecture'].forEach(c => {
        const btn = document.getElementById('news-cat-' + c);
        if (btn) btn.classList.toggle('active', !bookmarkedOnly && c === category);
      });
      const bmBtn = document.getElementById('news-cat-bookmarked');
      if (bmBtn) bmBtn.classList.toggle('active', bookmarkedOnly);

      try {
        const res = await fetch(`/api/newsfeed?category=${encodeURIComponent(category)}&bookmarked=${bookmarkedOnly ? '1' : '0'}`);
        if (!res.ok) return;
        const data = await res.json();
        const articles = data.articles || [];

        if (category === 'all' && !bookmarkedOnly) {
          const homeStrip = document.getElementById('home-pulse-strip');
          if (homeStrip) {
            homeStrip.innerHTML = articles.slice(0, 3).map(a => `
              <div class="news-card flex flex-col justify-between space-y-2.5">
                <div class="space-y-1">
                  <div class="mono text-[10px] font-semibold uppercase" style="color: var(--accent-terra);">${escapeHtml(a.sourceName)} · ${escapeHtml(a.publishedAt)}</div>
                  <a href="${escapeHtml(a.url)}" target="_blank" rel="noopener" class="font-bold text-sm hover:underline block leading-snug" style="color: var(--ink-primary);">${escapeHtml(a.title)} ↗</a>
                  <p class="text-xs line-clamp-2" style="color: var(--ink-secondary);">${escapeHtml(a.summary)}</p>
                </div>
                ${(a.relatedChapters && a.relatedChapters[0]) ? `
                  <button onclick="openTextbookChapter('${a.relatedChapters[0]}')" class="text-left mono text-[11px] font-semibold hover:underline" style="color: var(--accent-sage);">
                    → Linked: ${escapeHtml(a.relatedChapters[0])}
                  </button>
                ` : ''}
              </div>
            `).join('');
          }
        }

        const grid = document.getElementById('newsfeed-articles-grid');
        grid.innerHTML = articles.map(a => `
          <div class="news-card flex flex-col justify-between space-y-3" style="background: var(--bg-card); box-shadow: var(--shadow-tactile); border-radius: 14px; padding: 18px 20px;">
            <div class="space-y-2">
              <div class="flex items-center justify-between gap-2 mono text-[11px]">
                <span class="font-semibold" style="color: var(--accent-terra);">${escapeHtml(a.sourceName)} · ${escapeHtml(a.publishedAt)} (${a.readingMinutes}m)</span>
                <button onclick="toggleArticleBookmark('${a.id}')" class="nav-tab" style="padding: 3px 9px; font-size: 0.72rem; ${a.bookmarked ? 'background:#FEF3C7; color:#92400E; border-color:#F59E0B;' : ''}">
                  ${a.bookmarked ? '★ Saved' : '☆ Save'}
                </button>
              </div>
              <a href="${escapeHtml(a.url)}" target="_blank" rel="noopener" class="font-serif-display text-lg font-bold hover:underline block leading-snug">
                ${escapeHtml(a.title)} ↗
              </a>
              <p class="text-xs leading-relaxed" style="color: var(--ink-secondary);">${escapeHtml(a.summary)}</p>
              ${a.whyItMatters ? `
                <div class="news-card text-[11px]" style="padding: 10px 12px; color: var(--ink-secondary);">
                  <strong style="color: var(--ink-primary);">Why It Matters:</strong> ${escapeHtml(a.whyItMatters)}
                </div>
              ` : ''}
            </div>
            <div class="space-y-2 pt-2 border-t border-[#EFEAE0]">
              <div class="flex flex-wrap gap-1">
                ${(a.tags || []).map(t => `<span class="tag">#${escapeHtml(t)}</span>`).join('')}
              </div>
              <div class="flex flex-wrap gap-2">
                ${(a.relatedChapters || []).map(slug => `
                  <button onclick="openTextbookChapter('${slug}')" class="archetype-pill hover:underline" style="background:#E6F4F0; color:#1E6F5C; cursor:pointer;">
                    → Linked: ${escapeHtml(slug)}
                  </button>
                `).join('')}
              </div>
            </div>
          </div>
        `).join('') || `<div class="col-span-2 text-sm p-4" style="color: var(--ink-muted);">No articles match this filter.</div>`;
      } catch (_) {}
    }

    async function toggleArticleBookmark(articleId) {
      try {
        await fetch('/api/newsfeed/bookmark', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ articleId })
        });
        await loadNewsfeedView(state.newsCategory, state.newsBookmarkedOnly);
      } catch (_) {}
    }

    async function refreshLiveNewsfeed() {
      const btn = document.getElementById('news-refresh-btn');
      btn.textContent = '⏳ Polling RSS/Atom Feeds...';
      try {
        await fetch('/api/newsfeed/refresh', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fetchRemote: true })
        });
        await loadNewsfeedView(state.newsCategory, state.newsBookmarkedOnly);
      } catch (_) {}
      btn.textContent = '↻ Sync Live RSS/Atom Feeds';
    }

