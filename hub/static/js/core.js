    const VIZ_ALIAS_MAP = {
      "arch-backpressure-jitter": "arch-endpoint-cloud-sync",
      "ai-rag-triad-eval": "ai-rag-triad-gate",
      "cs-os-memory-gc-sawtooth": "cs-os-leak-detector"
    };

    const WORKBENCH_PATH_TO_ID = {
      "frameworks/sdet-system-design/01-distributed-concurrency-isolation": "wb-concurrency-isolation",
      "frameworks/sdet-system-design/02-ci-shard-bin-packer-and-tia": "wb-ci-shard-bin-packer-tia",
      "frameworks/design-challenges/01-custom-retry-analyzer": "wb-custom-retry-analyzer",
      "frameworks/design-challenges/02-json-payload-diff-engine": "wb-json-payload-diff-engine",
      "frameworks/design-challenges/03-rate-limited-test-client": "wb-rate-limiter-backpressure",
      "frameworks/design-challenges/04-test-data-builder": "wb-test-data-builder",
      "frameworks/design-challenges/05-microservice-mocking": "wb-microservice-mocking",
      "frameworks/ui-automation/playwright-python": "wb-playwright-ui-framework",
      "frameworks/api-automation/pytest-requests-python": "wb-api-automation-suite",
      "frameworks/api-automation/pytest-requests": "wb-api-automation-suite",
      "frameworks/data-validation/01-sql-reconciliation-and-isolation": "wb-sql-data-reconciliation",
      "frameworks/cicd-infra/01-container-and-sharding-orchestrator": "wb-cicd-container-sharding",
      "frameworks/performance-sre/01-load-coordinated-omission-and-chaos": "wb-perf-chaos-sre-harness",
      "frameworks/security-testing/01-bola-jwt-and-prompt-shield": "wb-security-bola-jwt-llm"
    };

    const TRACK_VISUAL_THEME = {
      "system-design": {
        pillBg: "#FCEEE8",
        pillColor: "#C85A32",
        pillText: "📖 Archetype 1: Textbook Courses",
        btnBg: "#C85A32",
        btnLabel: "Open Textbook Courses →"
      },
      "ai-engineering": {
        pillBg: "#F0EBFF",
        pillColor: "#5B3FD9",
        pillText: "📖 Archetype 1: Textbook Courses",
        btnBg: "#5B3FD9",
        btnLabel: "Open Textbook Courses →"
      },
      "core-cs": {
        pillBg: "#E6F4F0",
        pillColor: "#1E6F5C",
        pillText: "📖 Archetype 1: Textbook Courses",
        btnBg: "#1E6F5C",
        btnLabel: "Open Textbook Courses →"
      },
      "dsa": {
        pillBg: "#FEF3C7",
        pillColor: "#B7791F",
        pillText: "💻 Archetype 2: In-Browser 50/50 Split Studio (WS 1)",
        btnBg: "#B7791F",
        btnLabel: "Open 50/50 Studio →"
      },
      "frameworks": {
        pillBg: "#EBF8FF",
        pillColor: "#2B6CB0",
        pillText: "🛠️ Archetype 3: Local IDE Workbench (Strictly Zero AI)",
        btnBg: "#2B6CB0",
        btnLabel: "Open Workbench →"
      },
      "mock-interviews": {
        pillBg: "#FFF5F5",
        pillColor: "#9B2C2C",
        pillText: "🎙️ Archetype 4: Interactive Mock Interview Studio",
        btnBg: "#9B2C2C",
        btnLabel: "Open Simulator →"
      }
    };

    const FALLBACK_CHAPTERS = [
      {
        chapterId: "ch-01",
        number: "01",
        pattern: "Arrays & Hashing",
        title: "Ch 01: Arrays & Hashing",
        mentalModelTitle: "Mental Model: O(1) Instant Lookup via Canonical Signatures vs O(N) Linear Scan",
        mentalModelSummary: "Pre-index complements or 26-letter frequency signatures in a Hash Table so inner search loops collapse from O(N) to O(1).",
        tiles: [{ label: "E", sub: "a·e·t" }, { label: "A", sub: "a·e·t" }, { label: "T", sub: "a·e·t" }],
        done: 3,
        total: 10,
        problems: [
          { id: 1, title: "Two Sum", slug: "two-sum", folderSlug: "001-two-sum", hasLocalFiles: true, bothDone: true, javaDone: true, pyDone: true, difficulty: "Easy", diagramFormula: "need = target - x", diagramCaption: "Pair complement sum" },
          { id: 3, title: "Valid Anagram", slug: "valid-anagram", folderSlug: "002-valid-anagram", hasLocalFiles: true, bothDone: true, javaDone: true, pyDone: true, difficulty: "Easy", diagramFormula: "[A][E] ⇄ [E][A]", diagramCaption: "26-slot balance scale" },
          { id: 4, title: "Group Anagrams", slug: "group-anagrams", folderSlug: "003-group-anagrams", hasLocalFiles: true, bothDone: true, javaDone: true, pyDone: true, difficulty: "Medium", diagramFormula: "key = tuple(count[26])", diagramCaption: "Canonical frequency bucket" }
        ]
      }
    ];

    const FALLBACK_PROBLEMS = {
      "001-two-sum": {
        slug: "001-two-sum",
        title: "001. Two Sum",
        difficulty: "Easy",
        visualizerId: "dsa-two-sum",
        timeComplexity: "O(N)",
        spaceComplexity: "O(N)",
        prompt: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        invariant: "need = target - nums[i]  →  lookup in seen HashMap in O(1)",
        hints: [
          { tier: 1, title: "Mental Model & Intuition", content: "Imagine each number x asking the front desk: 'Has target - x already checked in?'" },
          { tier: 2, title: "Pattern Identification", content: "Use a single-pass HashMap mapping value -> index." },
          { tier: 3, title: "Algorithmic Invariant", content: "Check if (target - x) is in seen BEFORE inserting x so you never reuse the same index twice." },
          { tier: 4, title: "Edge Cases", content: "Test duplicate values ([3,3], target=6) and negative numbers." }
        ],
        cases: [
          { id: "case-1", label: "Case 1", passed: true, input: { nums: [2, 7, 11, 15], target: 9 }, expected: [0, 1], actual: [0, 1], durationMs: 0.3 }
        ],
        pythonCode: "from typing import List\n\nclass Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        seen = {}\n        for i, num in enumerate(nums):\n            diff = target - num\n            if diff in seen:\n                return [seen[diff], i]\n            seen[num] = i\n        return []\n",
        javaCode: "import java.util.*;\n\npublic class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        Map<Integer, Integer> seen = new HashMap<>();\n        for (int i = 0; i < nums.length; i++) {\n            int need = target - nums[i];\n            if (seen.containsKey(need)) return new int[] { seen.get(need), i };\n            seen.put(nums[i], i);\n        }\n        throw new IllegalArgumentException(\"No match\");\n    }\n}\n"
      },
      "002-valid-anagram": {
        slug: "002-valid-anagram",
        title: "002. Valid Anagram",
        difficulty: "Easy",
        visualizerId: "dsa-valid-anagram",
        timeComplexity: "O(N)",
        spaceComplexity: "O(1) [26 slots]",
        prompt: "Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
        invariant: "count[s[i]-'a']++ and count[t[i]-'a']--  →  all 26 slots == 0",
        hints: [
          { tier: 1, title: "Mental Model & Intuition", content: "Think of a 26-pan balance scale where s adds +1 weight and t subtracts -1 weight." }
        ],
        cases: [
          { id: "case-1", label: "Case 1", passed: true, input: { s: "anagram", t: "nagaram" }, expected: true, actual: true, durationMs: 0.3 }
        ],
        pythonCode: "class Solution:\n    def isAnagram(self, s: str, t: str) -> bool:\n        return sorted(s) == sorted(t)\n",
        javaCode: "public class Solution {\n    public boolean isAnagram(String s, String t) { return true; }\n}\n"
      },
      "003-group-anagrams": {
        slug: "003-group-anagrams",
        title: "003. Group Anagrams",
        difficulty: "Medium",
        visualizerId: "dsa-group-anagrams",
        timeComplexity: "O(N · K)",
        spaceComplexity: "O(N · K)",
        prompt: "Given an array of strings strs, group the anagrams together in O(N · K) time using a 26-letter frequency signature.",
        invariant: "key = tuple(count[26])  →  buckets[key].append(word)",
        hints: [
          { tier: 1, title: "Mental Model & Intuition", content: "Stamp each word with a 26-slot frequency barcode (a..z) in O(K) time instead of sorting in O(K log K)." },
          { tier: 2, title: "Pattern Identification", content: "Use defaultdict(list) keyed by the 26-integer count tuple." },
          { tier: 3, title: "Algorithmic Invariant", content: "Lists are unhashable in Python—convert count to tuple(count) before indexing the dict." },
          { tier: 4, title: "Edge Cases", content: "Empty string [\"\"], single char [\"a\"], and all-distinct words." }
        ],
        cases: [
          { id: "case-1", label: "Case 1", passed: true, input: { strs: ["eat", "tea", "tan", "ate", "nat", "bat"] }, expected: [["ate", "eat", "tea"], ["nat", "tan"], ["bat"]], actual: [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]], durationMs: 0.4 }
        ],
        pythonCode: "from collections import defaultdict\nfrom typing import List\n\nclass Solution:\n    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:\n        anagram_map = defaultdict(list)\n        for s in strs:\n            count = [0] * 26\n            for char in s:\n                count[ord(char) - ord(\"a\")] += 1\n            anagram_map[tuple(count)].append(s)\n        return list(anagram_map.values())\n",
        javaCode: "import java.util.*;\n\npublic class Solution {\n    public List<List<String>> groupAnagrams(String[] strs) {\n        return new ArrayList<>();\n    }\n}\n"
      }
    };

    let state = {
      activeView: 'home',
      workbenchSubmode: 'frameworks',
      roadmap: null,
      activeRoadmapPhase: 1,
      tracks: [],
      kbCourses: [],
      kbChapters: [],
      expandedCourseId: '01-zero-to-staff-sdet',
      kbFilterTrack: 'all',
      activeKbChapter: null,
      kbReadingMode: 'guided',
      kbActiveStepIdx: 0,
      preferredKbLang: 'python',
      kbCompendiumCache: {},
      activeCompendium: null,
      compendiumLayers: { step1: true, step2: true, step3: true, step4: true, step5: true, qa: true },
      compendiumCramOnly: false,
      compendiumBlurAnswers: false,
      compendiumFilterQuery: '',
      wtSlideIdx: 0,
      wtPlaying: false,
      wtTimer: null,
      wtSpeed: 1.0,
      wtCollapsed: true,
      wtMediaMode: 'storyboard',
      kbWidth: 'comfort',
      kbUserWidthOverride: false,
      maximizedSplitPane: null,
      poeSelectedIdx: null,
      kbQuizSelections: {},
      kbSimSteps: [],
      kbSimIdx: 0,
      newsCategory: 'all',
      newsBookmarkedOnly: false,
      interviewSession: null,
      interviewActiveDoc: 'questions',
      chapters: FALLBACK_CHAPTERS,
      activeChapterIdx: 0,
      recommendedProblem: null,
      activeProblemId: 4,
      activeSlug: '003-group-anagrams',
      activeVisualizerId: 'dsa-group-anagrams',
      activeLang: 'python',
      unlockedHintTier: 1,
      isDirty: false,
      files: {
        python: { path: 'dsa/01-arrays-and-hashing/003-group-anagrams/solution.py', content: '', sha256: '' },
        java: { path: 'dsa/01-arrays-and-hashing/003-group-anagrams/Solution.java', content: '', sha256: '' }
      },
      cases: [],
      selectedCaseIdx: 0,
      vizTrace: [],
      vizStepIdx: 0
    };

    function escapeHtml(raw) {
      return String(raw || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    }

    function wrapSvgTextLines(label, maxLen = 24) {
      const cleaned = String(label || '').replace(/<br\s*\/?>/gi, ' · ').replace(/\s+/g, ' ').trim();
      if (cleaned.length <= maxLen) return [cleaned];
      const words = cleaned.split(' ');
      const lines = [];
      let cur = '';
      for (const w of words) {
        if ((cur + ' ' + w).trim().length <= maxLen || !cur) {
          cur = (cur + ' ' + w).trim();
        } else {
          lines.push(cur);
          cur = w;
        }
      }
      if (cur) lines.push(cur);
      if (lines.length > 2) {
        return [lines[0], lines.slice(1).join(' ').slice(0, maxLen + 3) + '…'];
      }
      return lines;
    }

    function inferNodeSemanticPalette(label) {
      const low = String(label || '').toLowerCase();
      if (/(409|429|500|502|503|504|fail|flake|flaky|leak|race|drop|error|hallucin|naive|bottleneck|timeout|deadlock|reject|quarantine-red|oom)/.test(low)) {
        return { fill: '#FFF5F2', stroke: '#C85A32', text: '#7C2D12' };
      }
      if (/(staff|hermetic|pass|200|201|quorum|wal|pact|entail|valid|isolated|verified|green|healthy|idempotent|mastered|calibrated|safe)/.test(low)) {
        return { fill: '#F2FBF7', stroke: '#1E6F5C', text: '#064E3B' };
      }
      if (/(cdp|bidi|kafka|otel|traceparent|mcp|attention|transformer|rag|hnsw|bm25|tls|grpc|graphql|broker|router|shard|judge|lora)/.test(low)) {
        return { fill: '#F5F2FF', stroke: '#5B3FD9', text: '#311B92' };
      }
      return { fill: '#FFFFFF', stroke: '#D6CCBA', text: '#181615' };
    }

    function toggleDiagramSource(blockId) {
      const svgPane = document.getElementById(`${blockId}-svg`);
      const srcPane = document.getElementById(`${blockId}-src`);
      const btn = document.getElementById(`${blockId}-btn`);
      if (!svgPane || !srcPane || !btn) return;
      const showingSrc = !srcPane.classList.contains('hidden');
      srcPane.classList.toggle('hidden', showingSrc);
      svgPane.classList.toggle('hidden', !showingSrc);
      btn.textContent = showingSrc ? 'View Mermaid Source' : 'View Spatial SVG';
    }

    function renderSequenceSvg(rawLines) {
      const participants = [];
      const partMap = new Map();
      const events = [];

      const ensurePart = (id, label) => {
        const cleanId = id.trim();
        if (!partMap.has(cleanId)) {
          const item = { id: cleanId, label: (label || cleanId).replace(/^["']|["']$/g, '').trim() };
          partMap.set(cleanId, item);
          participants.push(item);
        } else if (label) {
          partMap.get(cleanId).label = label.replace(/^["']|["']$/g, '').trim();
        }
      };

      for (const raw of rawLines) {
        const ln = raw.trim();
        if (!ln || ln.startsWith('%%') || /^sequenceDiagram/i.test(ln) || /^(autonumber|activate|deactivate|loop|alt|else|opt|par|rect|end)\b/i.test(ln)) continue;
        const pMatch = ln.match(/^(?:participant|actor)\s+([A-Za-z0-9_.-]+)(?:\s+as\s+(.+))?$/i);
        if (pMatch) {
          ensurePart(pMatch[1], pMatch[2] || pMatch[1]);
          continue;
        }
        const noteMatch = ln.match(/^Note\s+(?:over|left of|right of)\s+([^:]+):\s*(.+)$/i);
        if (noteMatch) {
          events.push({ kind: 'note', targets: noteMatch[1], text: noteMatch[2].trim() });
          continue;
        }
        const msgMatch = ln.match(/^([A-Za-z0-9_.-]+)\s*(-->>|->>|-->|->)\s*([+-]?[A-Za-z0-9_.-]+)\s*:\s*(.+)$/);
        if (msgMatch) {
          const from = msgMatch[1];
          const arrow = msgMatch[2];
          const to = msgMatch[3].replace(/^[+-]/, '');
          ensurePart(from);
          ensurePart(to);
          events.push({ kind: 'msg', from, to, dashed: arrow.startsWith('--'), text: msgMatch[4].trim() });
        }
      }

      if (!participants.length) return '';
      const colGap = Math.max(155, Math.min(220, Math.floor(860 / Math.max(participants.length, 1))));
      const padX = 90;
      const width = Math.max(640, padX * 2 + (participants.length - 1) * colGap);
      const rowH = 48;
      const topY = 58;
      const height = topY + 36 + events.length * rowH + 36;
      const xOf = (id) => {
        const idx = participants.findIndex(p => p.id === id);
        return padX + (idx >= 0 ? idx : 0) * colGap;
      };

      let svg = `<svg viewBox="0 0 ${width} ${height}" width="100%" style="max-height:420px; display:block;" role="img" aria-label="Sequence Architecture Diagram">
        <defs>
          <marker id="seq-arrow-solid" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#181615"/>
          </marker>
          <marker id="seq-arrow-dash" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#1E6F5C"/>
          </marker>
        </defs>`;

      participants.forEach((p, idx) => {
        const cx = padX + idx * colGap;
        const pal = inferNodeSemanticPalette(p.label);
        const lines = wrapSvgTextLines(p.label, 18);
        svg += `<line x1="${cx}" y1="${topY}" x2="${cx}" y2="${height - 20}" stroke="#DED5C3" stroke-width="1.5" stroke-dasharray="4 4"/>`;
        svg += `<rect x="${cx - 66}" y="12" width="132" height="42" rx="9" fill="${pal.fill}" stroke="${pal.stroke}" stroke-width="1.6"/>`;
        if (lines.length === 1) {
          svg += `<text x="${cx}" y="37" text-anchor="middle" font-size="11" font-weight="700" fill="${pal.text}">${escapeHtml(lines[0])}</text>`;
        } else {
          svg += `<text x="${cx}" y="29" text-anchor="middle" font-size="10.5" font-weight="700" fill="${pal.text}">${escapeHtml(lines[0])}</text>`;
          svg += `<text x="${cx}" y="43" text-anchor="middle" font-size="10.5" font-weight="700" fill="${pal.text}">${escapeHtml(lines[1])}</text>`;
        }
      });

      events.forEach((ev, idx) => {
        const y = topY + 34 + idx * rowH;
        if (ev.kind === 'note') {
          svg += `<rect x="${Math.max(24, width / 2 - 210)}" y="${y - 16}" width="${Math.min(420, width - 48)}" height="28" rx="6" fill="#FBF6EC" stroke="#E2D6BE"/>`;
          svg += `<text x="${width / 2}" y="${y + 2}" text-anchor="middle" font-size="10.5" font-family="JetBrains Mono, monospace" fill="#57524E">${escapeHtml(ev.text.slice(0, 68))}</text>`;
          return;
        }
        const x1 = xOf(ev.from);
        const x2 = xOf(ev.to);
        const stroke = ev.dashed ? '#1E6F5C' : '#181615';
        const marker = ev.dashed ? 'url(#seq-arrow-dash)' : 'url(#seq-arrow-solid)';
        if (x1 === x2) {
          svg += `<path d="M ${x1} ${y - 6} C ${x1 + 48} ${y - 6}, ${x1 + 48} ${y + 14}, ${x1 + 4} ${y + 14}" fill="none" stroke="${stroke}" stroke-width="1.6" marker-end="${marker}"/>`;
          svg += `<text x="${x1 + 54}" y="${y + 7}" font-size="10.5" font-family="JetBrains Mono, monospace" fill="#2D2926">${escapeHtml(ev.text.slice(0, 48))}</text>`;
        } else {
          const mid = (x1 + x2) / 2;
          svg += `<line x1="${x1}" y1="${y + 6}" x2="${x2}" y2="${y + 6}" stroke="${stroke}" stroke-width="1.6" ${ev.dashed ? 'stroke-dasharray="5 4"' : ''} marker-end="${marker}"/>`;
          svg += `<text x="${mid}" y="${y - 2}" text-anchor="middle" font-size="10.5" font-family="JetBrains Mono, monospace" font-weight="600" fill="#2D2926">${escapeHtml(ev.text.slice(0, 54))}</text>`;
        }
      });

      svg += `</svg>`;
      return svg;
    }

    function renderFlowchartSvg(rawLines) {
      let isVertical = false;
      const nodes = new Map();
      const edges = [];

      const registerNodeToken = (rawToken) => {
        if (!rawToken) return null;
        const tok = rawToken.trim().replace(/:::.*$/, '');
        const m = tok.match(/^([A-Za-z0-9_.-]+)\s*(?:\[\("?([^"\)]+)"?\)\]|\[\/"?([^"\/]+)"?\/\]|\[\["?([^"\]]+)"?\]\]|\["?([^"\]]+)"?\]|\(\("?([^"\)]+)"?\)\)|\("?([^"\)]+)"?\)|\{\{"?([^"\}]+)"?\}\}|\{"?([^"\}]+)"?\})?$/);
        if (!m) {
          const fallbackId = tok.replace(/[^A-Za-z0-9_.-]/g, '') || `N${nodes.size + 1}`;
          if (!nodes.has(fallbackId)) nodes.set(fallbackId, { id: fallbackId, label: tok.replace(/[\[\]\(\)\{\}"]/g, '').trim() || fallbackId });
          return fallbackId;
        }
        const id = m[1];
        const extracted = m[2] || m[3] || m[4] || m[5] || m[6] || m[7] || m[8] || m[9];
        if (!nodes.has(id)) {
          nodes.set(id, { id, label: (extracted || id).trim() });
        } else if (extracted) {
          nodes.get(id).label = extracted.trim();
        }
        return id;
      };

      for (const raw of rawLines) {
        const ln = raw.trim().replace(/;$/, '');
        if (!ln || ln.startsWith('%%')) continue;
        const hdr = ln.match(/^(?:flowchart|graph)\s+(TD|TB|BT|LR|RL)/i);
        if (hdr) {
          isVertical = /^(TD|TB|BT)$/i.test(hdr[1]);
          continue;
        }
        if (/^(subgraph|end|style|classDef|class|linkStyle|direction)\b/i.test(ln)) continue;

        let edgeMatch = ln.match(/^(.+?)\s*(-\.->|==>|-->>|-->|---)\s*(?:\|([^|]+)\|\s*)?(.+)$/);
        let midLabel = '';
        if (!edgeMatch) {
          const alt = ln.match(/^(.+?)\s*--\s*([^-][^>]*?)\s*(-->|-\.->|==>)\s*(.+)$/);
          if (alt) {
            edgeMatch = [alt[0], alt[1], alt[3], alt[2], alt[4]];
          }
        }
        if (edgeMatch) {
          const splitOutsideQuotes = (expr) => {
            const parts = [];
            let buf = '';
            let inQuotes = false;
            let bracketDepth = 0;
            for (const ch of expr) {
              if (ch === '"') inQuotes = !inQuotes;
              else if (!inQuotes && (ch === '[' || ch === '(' || ch === '{')) bracketDepth++;
              else if (!inQuotes && (ch === ']' || ch === ')' || ch === '}')) bracketDepth = Math.max(0, bracketDepth - 1);
              if (ch === '&' && !inQuotes && bracketDepth === 0) {
                if (buf.trim()) parts.push(buf.trim());
                buf = '';
              } else {
                buf += ch;
              }
            }
            if (buf.trim()) parts.push(buf.trim());
            return parts;
          };
          const leftGroup = splitOutsideQuotes(edgeMatch[1]);
          const arrowKind = edgeMatch[2];
          midLabel = (edgeMatch[3] || '').replace(/^["']|["']$/g, '').trim();
          const rightGroup = splitOutsideQuotes(edgeMatch[4]);
          for (const lTok of leftGroup) {
            for (const rTok of rightGroup) {
              const u = registerNodeToken(lTok);
              const v = registerNodeToken(rTok);
              if (u && v) edges.push({ from: u, to: v, label: midLabel, dashed: arrowKind.includes('.') });
            }
          }
        } else {
          registerNodeToken(ln);
        }
      }

      if (!nodes.size) return '';
      const nodeIds = Array.from(nodes.keys());
      const ranks = {};
      nodeIds.forEach(id => { ranks[id] = 0; });
      for (let iter = 0; iter < Math.min(nodeIds.length + 2, 14); iter++) {
        for (const e of edges) {
          if (e.from !== e.to && ranks[e.to] < ranks[e.from] + 1) {
            ranks[e.to] = Math.min(ranks[e.from] + 1, 7);
          }
        }
      }

      const layers = {};
      nodeIds.forEach(id => {
        const r = ranks[id] || 0;
        if (!layers[r]) layers[r] = [];
        layers[r].push(id);
      });
      const rankKeys = Object.keys(layers).map(Number).sort((a, b) => a - b);
      const maxPerLayer = Math.max(...rankKeys.map(k => layers[k].length), 1);

      const boxW = 166;
      const boxH = 52;
      const pos = {};
      let width = 760;
      let height = 240;

      if (!isVertical) {
        const colStep = 276;
        const rowStep = 94;
        width = Math.max(700, 56 + rankKeys.length * colStep);
        height = Math.max(165, 48 + maxPerLayer * rowStep);
        rankKeys.forEach((rk, cIdx) => {
          const bucket = layers[rk];
          const totalH = (bucket.length - 1) * rowStep;
          const startY = (height - boxH) / 2 - totalH / 2;
          bucket.forEach((id, rIdx) => {
            pos[id] = { x: 28 + cIdx * colStep, y: startY + rIdx * rowStep };
          });
        });
      } else {
        const colStep = 224;
        const rowStep = 108;
        width = Math.max(660, 56 + maxPerLayer * colStep);
        height = Math.max(190, 44 + rankKeys.length * rowStep);
        rankKeys.forEach((rk, rIdx) => {
          const bucket = layers[rk];
          const totalW = (bucket.length - 1) * colStep;
          const startX = (width - boxW) / 2 - totalW / 2;
          bucket.forEach((id, cIdx) => {
            pos[id] = { x: startX + cIdx * colStep, y: 22 + rIdx * rowStep };
          });
        });
      }

      let svg = `<svg viewBox="0 0 ${width} ${height}" width="100%" style="max-height:430px; display:block;" role="img" aria-label="System Architecture Topology SVG">
        <defs>
          <marker id="flow-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#57524E"/>
          </marker>
        </defs>`;

      edges.forEach(e => {
        const p1 = pos[e.from];
        const p2 = pos[e.to];
        if (!p1 || !p2) return;
        let x1, y1, x2, y2, pathD;
        if (!isVertical) {
          const forward = p2.x >= p1.x;
          x1 = forward ? p1.x + boxW : p1.x;
          y1 = p1.y + boxH / 2;
          x2 = forward ? p2.x : p2.x + boxW;
          y2 = p2.y + boxH / 2;
          const dx = Math.max(36, Math.abs(x2 - x1) * 0.45);
          pathD = `M ${x1} ${y1} C ${x1 + (forward ? dx : -dx)} ${y1}, ${x2 - (forward ? dx : -dx)} ${y2}, ${x2} ${y2}`;
        } else {
          const downward = p2.y >= p1.y;
          x1 = p1.x + boxW / 2;
          y1 = downward ? p1.y + boxH : p1.y;
          x2 = p2.x + boxW / 2;
          y2 = downward ? p2.y : p2.y + boxH;
          const dy = Math.max(28, Math.abs(y2 - y1) * 0.45);
          pathD = `M ${x1} ${y1} C ${x1} ${y1 + (downward ? dy : -dy)}, ${x2} ${y2 - (downward ? dy : -dy)}, ${x2} ${y2}`;
        }
        svg += `<path d="${pathD}" fill="none" stroke="#6B645C" stroke-width="1.65" ${e.dashed ? 'stroke-dasharray="5 4"' : ''} marker-end="url(#flow-arrow)"/>`;
        if (e.label) {
          const mx = (x1 + x2) / 2;
          const my = (y1 + y2) / 2 - 5;
          const lbl = e.label.slice(0, 26);
          const pillW = Math.max(44, lbl.length * 6.2 + 12);
          svg += `<rect x="${mx - pillW / 2}" y="${my - 10}" width="${pillW}" height="16" rx="4" fill="#FAF7F2" stroke="#E6DEC8"/>`;
          svg += `<text x="${mx}" y="${my + 1}" text-anchor="middle" font-size="9.5" font-family="JetBrains Mono, monospace" font-weight="600" fill="#57524E">${escapeHtml(lbl)}</text>`;
        }
      });

      nodeIds.forEach(id => {
        const n = nodes.get(id);
        const p = pos[id];
        if (!n || !p) return;
        const pal = inferNodeSemanticPalette(n.label);
        const lines = wrapSvgTextLines(n.label, 22);
        svg += `<rect x="${p.x}" y="${p.y}" width="${boxW}" height="${boxH}" rx="10" fill="${pal.fill}" stroke="${pal.stroke}" stroke-width="1.75"/>`;
        if (lines.length === 1) {
          svg += `<text x="${p.x + boxW / 2}" y="${p.y + 30}" text-anchor="middle" font-size="11" font-weight="700" fill="${pal.text}">${escapeHtml(lines[0])}</text>`;
        } else {
          svg += `<text x="${p.x + boxW / 2}" y="${p.y + 22}" text-anchor="middle" font-size="10.5" font-weight="700" fill="${pal.text}">${escapeHtml(lines[0])}</text>`;
          svg += `<text x="${p.x + boxW / 2}" y="${p.y + 37}" text-anchor="middle" font-size="10.2" font-weight="600" fill="${pal.text}">${escapeHtml(lines[1])}</text>`;
        }
      });

      svg += `</svg>`;
      return svg;
    }

    function renderMermaidDiagramSvg(code, blockId) {
      const trimmed = (code || '').trim();
      const rawLines = trimmed.split('\n');
      const firstLine = (rawLines.find(l => l.trim() && !l.trim().startsWith('%%')) || '').trim();
      const svgMarkup = /^sequenceDiagram/i.test(firstLine)
        ? renderSequenceSvg(rawLines)
        : renderFlowchartSvg(rawLines);

      if (!svgMarkup) {
        return `<div class="my-4 news-card"><pre style="margin:0;">${escapeHtml(trimmed)}</pre></div>`;
      }

      return `
        <div class="svg-diagram-shell">
          <div class="flex flex-wrap items-center justify-between gap-2 mb-2.5 pb-2 border-b border-[#EFEAE0]">
            <div class="flex items-center gap-2">
              <span class="mono text-[10px] font-semibold uppercase" style="color: var(--accent-terra);">
                🗺️ Spatial Architecture Topology (Signaled SVG)
              </span>
              <span class="mono text-[10px]" style="color: var(--ink-muted);">
                <span style="color:#C85A32;">● Bottleneck/Failure</span> · <span style="color:#1E6F5C;">● Staff Invariant</span> · <span style="color:#5B3FD9;">● Protocol/Control</span>
              </span>
            </div>
            <button id="${blockId}-btn" onclick="toggleDiagramSource('${blockId}')" class="btn-subtle" style="padding: 3px 9px; font-size: 0.7rem;">
              View Mermaid Source
            </button>
          </div>
          <div id="${blockId}-svg">${svgMarkup}</div>
          <pre id="${blockId}-src" class="hidden" style="margin:0; background:#18181B; color:#A7F3D0;">${escapeHtml(trimmed)}</pre>
        </div>
      `;
    }

    function renderContrastiveCard(code) {
      try {
        const data = JSON.parse(code.trim());
        const naiveTitle = data.naiveTitle || (data.naive && data.naive.title) || 'Naive / Fragile Anti-Pattern';
        const staffTitle = data.staffTitle || (data.staff && data.staff.title) || 'Staff Production Architecture';
        const naivePts = Array.isArray(data.naivePoints)
          ? data.naivePoints
          : (Array.isArray(data.naive) ? data.naive : [String(data.naive || data.naiveSummary || '')]);
        const staffPts = Array.isArray(data.staffPoints)
          ? data.staffPoints
          : (Array.isArray(data.staff) ? data.staff : [String(data.staff || data.staffSummary || '')]);

        return `
          <div class="my-4 space-y-2">
            ${data.title ? `<div class="mono text-[11px] font-semibold uppercase" style="color: var(--ink-secondary);">⚖️ Contrastive Architecture Case — ${escapeHtml(data.title)}</div>` : ''}
            <div class="contrast-grid" style="margin-top:4px;">
              <div class="contrast-naive space-y-2">
                <div class="flex items-center justify-between gap-2">
                  <span class="mono text-[11px] font-bold uppercase" style="color:#9B2C2C;">❌ ${escapeHtml(naiveTitle)}</span>
                  ${data.naiveMetric ? `<span class="mono text-[10px] px-2 py-0.5 rounded bg-rose-100 text-rose-900 font-semibold">${escapeHtml(data.naiveMetric)}</span>` : ''}
                </div>
                <ul class="list-disc pl-4 space-y-1 text-xs" style="color:#57524E; margin:0;">
                  ${naivePts.filter(Boolean).map(pt => `<li>${escapeHtml(pt)}</li>`).join('')}
                </ul>
              </div>
              <div class="contrast-staff space-y-2">
                <div class="flex items-center justify-between gap-2">
                  <span class="mono text-[11px] font-bold uppercase" style="color:#1E6F5C;">✓ ${escapeHtml(staffTitle)}</span>
                  ${data.staffMetric ? `<span class="mono text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 font-semibold">${escapeHtml(data.staffMetric)}</span>` : ''}
                </div>
                <ul class="list-disc pl-4 space-y-1 text-xs" style="color:#1F3A33; margin:0;">
                  ${staffPts.filter(Boolean).map(pt => `<li>${escapeHtml(pt)}</li>`).join('')}
                </ul>
              </div>
            </div>
          </div>
        `;
      } catch (_) {
        return `<pre>${escapeHtml(code.trim())}</pre>`;
      }
    }

    function switchDualCodeLang(groupId, lang) {
      state.preferredKbLang = lang;
      const pyPane = document.getElementById(`${groupId}-py`);
      const jvPane = document.getElementById(`${groupId}-jv`);
      const pyBtn = document.getElementById(`${groupId}-btn-py`);
      const jvBtn = document.getElementById(`${groupId}-btn-jv`);
      const bothBtn = document.getElementById(`${groupId}-btn-both`);
      if (!pyPane || !jvPane || !pyBtn || !jvBtn) return;
      const showPy = lang === 'python' || lang === 'both';
      const showJv = lang === 'java' || lang === 'both';
      pyPane.classList.toggle('hidden', !showPy);
      jvPane.classList.toggle('hidden', !showJv);
      pyBtn.style.background = lang === 'python' ? '#C85A32' : '#27272A';
      pyBtn.style.color = lang === 'python' ? '#FFFFFF' : '#A1A1AA';
      jvBtn.style.background = lang === 'java' ? '#C85A32' : '#27272A';
      jvBtn.style.color = lang === 'java' ? '#FFFFFF' : '#A1A1AA';
      if (bothBtn) {
        bothBtn.style.background = lang === 'both' ? '#C85A32' : '#27272A';
        bothBtn.style.color = lang === 'both' ? '#FFFFFF' : '#A1A1AA';
      }
    }

    function switchAllCompendiumCodeLang(lang) {
      state.preferredKbLang = lang;
      document.querySelectorAll('[data-dual-code-group]').forEach(el => {
        const gid = el.getAttribute('data-dual-code-group');
        if (gid) switchDualCodeLang(gid, lang);
      });
      ['python', 'java', 'both'].forEach(k => {
        const btn = document.getElementById(`comp-lang-btn-${k}`);
        if (btn) btn.classList.toggle('active', k === lang);
      });
    }

    /* ========================================================================
       ZEN EDITORIAL MARKDOWN RENDERER (SPATIAL SVGs, CONTRASTIVE CARDS & CODE TABS)
       ======================================================================== */
    function renderEditorialMarkdown(md) {
      if (!md) return '';
      const blocks = [];

      // Collapse adjacent Python + Java code blocks (with optional ### Java subheading between them) into a clean Tabbed Switcher
      let preprocessed = md.replace(
        /```python\n([\s\S]*?)```\s*(?:\n###[^\n]*?(?:Java|JUnit|Playwright\s+Java|REST\s+Assured)[^\n]*\n+)?\s*```java\n([\s\S]*?)```/gi,
        (_, pyCode, jvCode) => {
          const idx = blocks.length;
          const gid = `kb-codetab-${idx}-${Math.random().toString(36).slice(2, 6)}`;
          const pref = state.preferredKbLang || 'python';
          const showPy = pref === 'python' || pref === 'both';
          const showJv = pref === 'java' || pref === 'both';
          blocks.push(`
            <div data-dual-code-group="${gid}" class="my-3.5 rounded-[10px] overflow-hidden border border-zinc-800 bg-[#18181B]">
              <div class="flex items-center justify-between px-3.5 py-2 bg-[#121215] border-b border-zinc-800">
                <div class="flex items-center gap-1.5">
                  <button id="${gid}-btn-py" onclick="switchDualCodeLang('${gid}', 'python')" class="mono text-[11px] font-semibold px-2.5 py-1 rounded cursor-pointer transition" style="background:${pref === 'python' ? '#C85A32' : '#27272A'}; color:${pref === 'python' ? '#FFFFFF' : '#A1A1AA'}; border:none;">
                    🐍 Python 3
                  </button>
                  <button id="${gid}-btn-jv" onclick="switchDualCodeLang('${gid}', 'java')" class="mono text-[11px] font-semibold px-2.5 py-1 rounded cursor-pointer transition" style="background:${pref === 'java' ? '#C85A32' : '#27272A'}; color:${pref === 'java' ? '#FFFFFF' : '#A1A1AA'}; border:none;">
                    ☕ Java 17
                  </button>
                  <button id="${gid}-btn-both" onclick="switchDualCodeLang('${gid}', 'both')" class="mono text-[11px] font-semibold px-2.5 py-1 rounded cursor-pointer transition" style="background:${pref === 'both' ? '#C85A32' : '#27272A'}; color:${pref === 'both' ? '#FFFFFF' : '#A1A1AA'}; border:none;">
                    ⚖️ Split Both
                  </button>
                </div>
                <span class="mono text-[10px] text-zinc-400">Dual-Language Blueprint</span>
              </div>
              <pre id="${gid}-py" class="${showPy ? '' : 'hidden'}" style="margin:0; border:none; border-radius:0;">${escapeHtml(pyCode.trim())}</pre>
              <pre id="${gid}-jv" class="${showJv ? '' : 'hidden'}" style="margin:0; border-top:1px solid #27272A; border-radius:0;">${escapeHtml(jvCode.trim())}</pre>
            </div>
          `);
          return `\n@@CODEBLOCK_${idx}@@\n`;
        }
      );

      let working = preprocessed.replace(/```([^\n]*)\n([\s\S]*?)```/g, (_, langSpec, code) => {
        const idx = blocks.length;
        const cleanLang = (langSpec || 'text').trim().toLowerCase();
        if (cleanLang === 'mermaid') {
          blocks.push(renderMermaidDiagramSvg(code, `kb-diag-${idx}-${Math.random().toString(36).slice(2, 6)}`));
        } else if (cleanLang === 'json contrast' || cleanLang === 'contrast') {
          blocks.push(renderContrastiveCard(code));
        } else {
          blocks.push(`
            <div class="my-3">
              <div class="mono text-[10px] uppercase tracking-wider text-zinc-400 bg-[#18181B] px-3.5 pt-2 rounded-t-[10px] border-x border-t border-zinc-800">${escapeHtml(cleanLang)}</div>
              <pre style="margin-top:0; border-top-left-radius:0; border-top-right-radius:0;">${escapeHtml(code.trim())}</pre>
            </div>
          `);
        }
        return `@@CODEBLOCK_${idx}@@`;
      });

      const lines = working.split('\n');
      const out = [];
      let inTable = false;
      let tableRows = [];
      let inList = false;

      const formatInline = (txt) => {
        let outTxt = escapeHtml(txt)
          .replace(/\$(?![0-9])([^$]+)\$/g, (_, mathExpr) => {
            return '<span class="mono" style="font-size:0.84em; color:#2D2926;">' + mathExpr
              .replace(/\\text\{([^}]*)\}/g, '$1')
              .replace(/\\frac\{([^}]*)\}\{([^}]*)\}/g, '($1)/($2)')
              .replace(/\\hat\{([^}]*)\}/g, '$1̂')
              .replace(/\\min/g, 'min')
              .replace(/\\max/g, 'max')
              .replace(/\\log/g, 'log')
              .replace(/\\sqrt\{([^}]*)\}/g, '√($1)')
              .replace(/\\alpha/g, 'α')
              .replace(/\\beta/g, 'β')
              .replace(/\\delta/g, 'δ')
              .replace(/\\Delta/g, 'Δ')
              .replace(/\\epsilon/g, 'ε')
              .replace(/\\lambda/g, 'λ')
              .replace(/\\sigma/g, 'σ')
              .replace(/\\sum/g, '∑')
              .replace(/\\kappa/g, 'κ')
              .replace(/\\to/g, '→')
              .replace(/\\le/g, '≤')
              .replace(/\\ge/g, '≥')
              .replace(/\\times/g, '×')
              .replace(/\\cdot/g, '·')
              .replace(/\\approx/g, '≈')
              .replace(/\\%/g, '%')
              .replace(/_\{([^}]+)\}/g, '<sub>$1</sub>')
              .replace(/_([0-9a-zA-Z]+)/g, '<sub>$1</sub>')
              .replace(/\^\{([^}]+)\}/g, '<sup>$1</sup>')
              .replace(/\^([0-9a-zA-Z]+)/g, '<sup>$1</sup>') + '</span>';
          });
        return outTxt
          .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
          .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
          .replace(/\*([^*]+)\*/g, '<em>$1</em>');
      };

      const flushTable = () => {
        if (!inTable || !tableRows.length) return;
        const headerCells = tableRows[0].split('|').filter(Boolean).map(c => `<th>${formatInline(c.trim())}</th>`).join('');
        const bodyHtml = tableRows.slice(2).map(r => {
          const cols = r.split('|').filter(Boolean).map(c => `<td>${formatInline(c.trim())}</td>`).join('');
          return `<tr>${cols}</tr>`;
        }).join('');
        out.push(`<table><thead><tr>${headerCells}</tr></thead><tbody>${bodyHtml}</tbody></table>`);
        inTable = false;
        tableRows = [];
      };

      const flushList = () => {
        if (inList) {
          out.push('</ul>');
          inList = false;
        }
      };

      for (const rawLine of lines) {
        const line = rawLine.trimEnd();
        if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
          flushList();
          inTable = true;
          tableRows.push(line.trim());
          continue;
        } else if (inTable) {
          flushTable();
        }

        if (/^@@CODEBLOCK_\d+@@$/.test(line.trim())) {
          flushList();
          out.push(line.trim());
          continue;
        }
        if (line.trim() === '---') {
          flushList();
          continue;
        }
        if (line.startsWith('# ')) {
          flushList();
          continue;
        }
        if (line.startsWith('## ')) {
          flushList();
          out.push(`<h2>${formatInline(line.slice(3))}</h2>`);
        } else if (line.startsWith('### ')) {
          flushList();
          out.push(`<h3>${formatInline(line.slice(4))}</h3>`);
        } else if (line.startsWith('> ')) {
          flushList();
          const cleanedQuote = line.slice(2).replace(/^\[!(WARNING|IMPORTANT|TIP|NOTE)\]\s*/i, '');
          if (cleanedQuote.trim()) {
            out.push(`<blockquote>${formatInline(cleanedQuote)}</blockquote>`);
          }
        } else if (/^[-*]\s+/.test(line.trim()) || /^\d+\.\s+/.test(line.trim())) {
          if (!inList) {
            out.push('<ul class="list-disc">');
            inList = true;
          }
          const itemTxt = line.trim().replace(/^([-*]|\d+\.)\s+/, '');
          out.push(`<li>${formatInline(itemTxt)}</li>`);
        } else if (line.trim()) {
          flushList();
          out.push(`<p>${formatInline(line.trim())}</p>`);
        } else {
          flushList();
        }
      }
      flushTable();
      flushList();

      let html = out.join('\n');
      blocks.forEach((b, idx) => {
        html = html.replace(`@@CODEBLOCK_${idx}@@`, b);
      });
      return html;
    }

    /* ========================================================================
       NAVIGATION & VIEW SWITCHER
       ======================================================================== */
    function showView(viewName) {
      if (viewName === 'feed') viewName = 'newsfeed';
      state.activeView = viewName;
      document.body.setAttribute('data-active-view', viewName);
      if (typeof closePeekDrawer === 'function') closePeekDrawer();
      ['home', 'textbook', 'newsfeed', 'roadmap', 'workspace', 'workbench'].forEach(v => {
        const el = document.getElementById('view-' + v);
        if (el) el.classList.toggle('hidden', v !== viewName);
      });

      const navMap = {
        home: 'tab-btn-dashboard',
        textbook: 'tab-btn-textbook',
        newsfeed: 'tab-btn-feed',
        roadmap: 'tab-btn-roadmap',
        workspace: 'tab-btn-visualizer'
      };
      ['tab-btn-dashboard', 'tab-btn-textbook', 'tab-btn-feed', 'tab-btn-roadmap', 'tab-btn-visualizer', 'tab-btn-workbench', 'tab-btn-interviews'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) btn.classList.remove('active');
      });

      if (viewName === 'workbench') {
        const targetId = state.workbenchSubmode === 'interviews' ? 'tab-btn-interviews' : 'tab-btn-workbench';
        const wbBtn = document.getElementById(targetId);
        if (wbBtn) wbBtn.classList.add('active');
      } else if (navMap[viewName]) {
        const activeBtn = document.getElementById(navMap[viewName]);
        if (activeBtn) activeBtn.classList.add('active');
      }
      document.getElementById('global-search-dropdown').classList.add('hidden');
    }

    function setHomeHeroMode(mode) {
      ['featured', 'dsa', 'upnext'].forEach(m => {
        const el = document.getElementById('hero-mode-' + m);
        if (el) el.classList.toggle('active', m === mode);
      });

      if (mode === 'dsa') {
        document.getElementById('home-hero-kicker').textContent = "DSA 50/50 SPLIT STUDIO · CHAPTER 01";
        document.getElementById('home-hero-title').textContent = "003. Group Anagrams — Canonical 26-Slot Frequency Signatures";
        document.getElementById('home-hero-desc').innerHTML =
          'Discover how character frequencies fold words into identical geometric signatures in <code class="mono text-xs bg-white px-1.5 py-0.5 rounded border border-[#E6DEC8]">O(N · K)</code> time—bypassing <code class="mono text-xs">O(K log K)</code> string sorting.';
        document.getElementById('home-hero-cta').textContent = 'Open in 50/50 Studio →';
        document.getElementById('home-hero-cta').onclick = () => openProblemWorkspace('003-group-anagrams');
      } else if (mode === 'upnext' && state.recommendedProblem) {
        const p = state.recommendedProblem;
        document.getElementById('home-hero-kicker').textContent = `UP NEXT IN DSA · CHAPTER ${p.chapterNumber || '01'}`;
        document.getElementById('home-hero-title').textContent = `${String(p.id).padStart(3, '0')}. ${p.title}`;
        document.getElementById('home-hero-desc').textContent = `Master ${p.title} (${p.pattern}) using the core invariant: ${p.diagramFormula}.`;
        document.getElementById('home-hero-cta').textContent = 'Scaffold & Solve →';
        document.getElementById('home-hero-cta').onclick = () => openOrScaffoldProblem(p.id, p.folderSlug || p.slug, p.hasLocalFiles);
      } else {
        document.getElementById('home-hero-kicker').textContent = "LOCAL-FIRST MULTI-MODAL ENGINEERING MASTERY";
        document.getElementById('home-hero-title').textContent = "12 Prioritized Textbook Courses · 4 Execution Archetypes";
        document.getElementById('home-hero-desc').innerHTML =
          'Every track in <strong>The Hub of Learning</strong> uses a purpose-built learning modality: <strong>Textbook Courses</strong> (Zero to Staff SDET, Testing Frameworks, Playwright UI, API &amp; Contracts, AI Engineering, AI QA, System Design, Core CS, SQL &amp; Data, Docker/CI/CD/Cloud, Performance &amp; SRE, App/API Security), <strong>In-Browser 50/50 Split Studio</strong> (DSA), <strong>Local IDE Deterministic Workbench</strong> (Automation Frameworks — strictly zero AI), and <strong>Staff Mock Interview Simulations</strong>.';
        document.getElementById('home-hero-cta').textContent = 'Start Course 01: Zero to Staff SDET →';
        document.getElementById('home-hero-cta').onclick = () => openCourseById('01-zero-to-staff-sdet');
      }
    }

    /* ========================================================================
       ALL 6 CORE TRACKS + 8 PRIORITIZED TEXTBOOK COURSES
       ======================================================================== */
    async function loadTracksAndHome() {
      try {
        const res = await fetch('/api/tracks');
        if (res.ok) {
          const data = await res.json();
          state.tracks = data.tracks || [];
          if (data.textbookCourses && data.textbookCourses.length && !state.kbCourses.length) {
            state.kbCourses = data.textbookCourses;
            renderHomeCoursesGrid();
          }
          renderHomeTracksGrid();
        }
      } catch (_) {}
    }

    function renderHomeCoursesGrid() {
      const grid = document.getElementById('home-courses-grid');
      if (!grid || !state.kbCourses.length) return;
      grid.innerHTML = state.kbCourses.map(c => {
        const pct = c.publishedChapters > 0 ? Math.round((c.masteredChapters / c.publishedChapters) * 100) : 0;
        const numStr = String(c.priorityRank || 1).padStart(2, '0');
        return `
          <div onclick="openCourseById('${c.courseId}')" class="track-card cursor-pointer flex flex-col justify-between gap-2.5" style="padding: 15px 18px;">
            <div class="space-y-1">
              <div class="flex items-center justify-between gap-2 mono text-[10.5px]" style="color: var(--ink-muted);">
                <span>COURSE ${numStr}</span>
                <span>${c.publishedChapters} Chapters · ${c.plannedModules} Modules</span>
              </div>
              <h3 style="font-size: 1.02rem; font-weight: 650; line-height: 1.32;">
                ${escapeHtml(c.shortTitle || c.title)}
              </h3>
              <p style="font-size: 0.8rem; color: var(--ink-secondary); line-height: 1.5; margin: 0;" class="line-clamp-2">
                ${escapeHtml(c.tagline)}
              </p>
            </div>
            <div class="space-y-1.5 pt-1">
              <div class="w-full h-1 rounded-full overflow-hidden" style="background: var(--bg-subtle);">
                <div style="width: ${pct}%; background: var(--accent-terra);" class="h-full rounded-full transition-all"></div>
              </div>
              <div class="flex items-center justify-between mono text-[10.5px]">
                <span style="color: var(--ink-muted);">${c.masteredChapters}/${c.publishedChapters} mastered</span>
                <div class="flex items-center gap-2">
                  <button onclick="event.stopPropagation(); openCourseCompendium('${c.courseId}')" class="px-2 py-0.5 rounded cursor-pointer" style="background: var(--bg-subtle); color: var(--ink-secondary); border: none; font-weight: 600;" title="Open all chapters of this course in a single revision page">
                    ⚡ 1-Page Revise
                  </button>
                  <span style="color: var(--accent-terra); font-weight: 600;">Read →</span>
                </div>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    function renderHomeTracksGrid() {
      const grid = document.getElementById('home-tracks-grid');
      if (!grid || !state.tracks.length) return;

      grid.innerHTML = state.tracks.map(t => {
        const theme = TRACK_VISUAL_THEME[t.id] || TRACK_VISUAL_THEME['system-design'];
        let clickAction = '';
        if (t.archetype === 'interactive-textbook') {
          clickAction = `openTrackTextbook('${t.id}')`;
        } else if (t.id === 'dsa') {
          clickAction = `showView('roadmap')`;
        } else if (t.id === 'frameworks') {
          clickAction = `openWorkbenchSubmode('frameworks')`;
        } else {
          clickAction = `openWorkbenchSubmode('interviews')`;
        }

        const volumePrefix = t.volume && t.volume.startsWith('Volume') ? `${t.volume.split('(')[0].trim()}: ` : '';
        const displayHeading = t.title.startsWith('Volume') ? t.title : `${volumePrefix}${t.title}`;

        return `
          <div onclick="${clickAction}" class="track-card cursor-pointer flex flex-col justify-between gap-4">
            <div>
              <span class="archetype-pill" style="background: ${theme.pillBg}; color: ${theme.pillColor};">
                ${escapeHtml(theme.pillText)}
              </span>
              <h3 style="font-size: 1.16rem; font-weight: 700; margin-top: 10px; line-height: 1.32;">
                ${escapeHtml(displayHeading)}
              </h3>
              <p style="font-size: 0.87rem; color: var(--ink-secondary); margin-top: 5px; line-height: 1.55;">
                ${escapeHtml(t.tagline)}
              </p>
            </div>
            <div class="flex items-center justify-between gap-2 pt-2 border-t border-[#EFEAE0]">
              <span class="mono" style="font-size: 0.75rem; color: var(--ink-secondary);">
                <strong>${t.completedItems}/${t.totalItems}</strong> ${escapeHtml(t.unitLabel)}
              </span>
              <button class="btn-primary" style="background: ${theme.btnBg};">
                ${escapeHtml(theme.btnLabel)}
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    function openCourseById(courseId) {
      state.expandedCourseId = courseId;
      showView('textbook');
      const course = state.kbCourses.find(c => c.courseId === courseId);
      if (course && course.firstChapterSlug) {
        openTextbookChapter(course.firstChapterSlug, false);
        return;
      }
      const fallbackCh = state.kbChapters.find(c => c.courseId === courseId) || state.kbChapters[0];
      if (fallbackCh) openTextbookChapter(fallbackCh.slug, false);
      else renderKbChaptersSpine();
    }

    function openTrackTextbook(trackId) {
      const pillarDefaultCourse = {
        'system-design': '01-zero-to-staff-sdet',
        'ai-engineering': '05-ai-engineering',
        'core-cs': '03-ui-automation-playwright'
      };
      const targetCourseId = pillarDefaultCourse[trackId];
      const courseObj = state.kbCourses.find(c => c.courseId === targetCourseId && c.publishedChapters > 0);
      if (courseObj) {
        openCourseById(courseObj.courseId);
        return;
      }
      showView('textbook');
      const firstMatch = state.kbChapters.find(c => c.track === trackId) || state.kbChapters[0];
      if (firstMatch) openTextbookChapter(firstMatch.slug, false);
    }

    function openWorkbenchSubmode(mode) {
      state.workbenchSubmode = mode;
      showView('workbench');
      switchWorkbenchMode(mode);
    }

    async function handleGlobalKbSearch(query) {
      const box = document.getElementById('global-search-dropdown');
      const trimmed = (query || '').trim();
      if (!trimmed) {
        box.classList.add('hidden');
        return;
      }
      try {
        const res = await fetch(`/api/kb/search?q=${encodeURIComponent(trimmed)}`);
        if (!res.ok) return;
        const data = await res.json();
        box.classList.remove('hidden');
        if (!data.results || !data.results.length) {
          box.innerHTML = `<div class="p-2.5 text-xs" style="color: var(--ink-secondary);">No FTS5 matches for "${escapeHtml(trimmed)}"</div>`;
          return;
        }
        box.innerHTML = `
          <div class="px-2 py-1 mono text-[10px] font-semibold border-b border-[#E6DEC8]" style="color: var(--accent-sage);">
            SQLite FTS5 BM25 · ${data.count} hits in ${data.latencyMs}ms
          </div>
          ${data.results.map(r => `
            <button onclick="openTextbookChapter('${r.slug}')" class="w-full text-left p-2.5 rounded-lg hover:bg-[#FAF7F2] transition block">
              <div class="flex items-center justify-between mono text-[10px] font-semibold" style="color: var(--accent-terra);">
                <span>${escapeHtml((r.courseId || r.track || '').toUpperCase())}</span>
                <span>BM25 ${r.rank}</span>
              </div>
              <div class="font-bold text-xs mt-0.5">${escapeHtml(r.title)}</div>
              <div class="text-[11px] mt-0.5 line-clamp-2" style="color: var(--ink-secondary);">${r.snippet || escapeHtml(r.summary)}</div>
            </button>
          `).join('')}
        `;
      } catch (_) {}
    }


    /* ========================================================================
       OPTION 4: EYE-COMFORT PALETTES, FONT SCALE, COLLAPSIBLE DRAWERS & FOCUS MODE
       ======================================================================== */
    const READER_FONT_SCALES = [1, 1.08, 1.16, 0.94];
    let activeFontScaleIdx = 0;

    function setEyeComfortTheme(themeName) {
      const valid = ['sepia', 'oat', 'ink', 'dusk'];
      const chosen = valid.includes(themeName) ? themeName : 'sepia';
      document.body.setAttribute('data-theme', chosen);
      try { localStorage.setItem('hub_eye_theme', chosen); } catch (_) {}
      valid.forEach(t => {
        const btn = document.getElementById('theme-btn-' + t);
        if (btn) btn.classList.toggle('active', t === chosen);
      });
    }

    function cycleReaderFontScale() {
      activeFontScaleIdx = (activeFontScaleIdx + 1) % READER_FONT_SCALES.length;
      const scale = READER_FONT_SCALES[activeFontScaleIdx];
      document.documentElement.style.setProperty('--reader-font-scale', String(scale));
      const btn = document.getElementById('font-scale-btn');
      if (btn) btn.textContent = scale === 1 ? 'Aa' : `Aa ${Math.round(scale * 100)}%`;
      try { localStorage.setItem('hub_font_scale_idx', String(activeFontScaleIdx)); } catch (_) {}
    }

    function toggleKbSidebar(side) {
      const cls = side === 'left' ? 'kb-hide-left' : 'kb-hide-right';
      const hidden = document.body.classList.toggle(cls);
      const btn = document.getElementById(side === 'left' ? 'kb-toggle-left-btn' : 'kb-toggle-right-btn');
      if (btn) btn.classList.toggle('active', !hidden);
      if (side === 'left' && !hidden) closePeekDrawer();
      try { localStorage.setItem('hub_' + cls, hidden ? '1' : '0'); } catch (_) {}
    }

    function setKbContentWidth(mode, isManual = true) {
      const valid = ['comfort', 'wide', 'full'];
      const chosen = valid.includes(mode) ? mode : 'comfort';
      state.kbWidth = chosen;
      if (isManual) state.kbUserWidthOverride = true;
      document.body.setAttribute('data-kb-width', chosen);
      valid.forEach(m => {
        const b1 = document.getElementById('kb-width-btn-' + m);
        const b2 = document.getElementById('zen-width-' + m);
        if (b1) b1.classList.toggle('active', m === chosen);
        if (b2) b2.classList.toggle('active', m === chosen);
      });
      if (isManual) {
        try { localStorage.setItem('hub_kb_width', chosen); } catch (_) {}
      }
    }

    function toggleCenterContentExpand(requestNative = false) {
      if (state.activeView === 'textbook' && state.kbReadingMode === 'revise' && state.kbWidth === 'comfort') {
        setKbContentWidth('wide', false);
      }
      toggleZenFullscreen(requestNative);
    }

    function openPeekDrawer() {
      const drawer = document.getElementById('kb-peek-drawer');
      if (drawer && state.activeView === 'textbook') drawer.classList.add('open');
    }

    function closePeekDrawer() {
      const drawer = document.getElementById('kb-peek-drawer');
      if (drawer) drawer.classList.remove('open');
    }

    function togglePeekDrawer() {
      const drawer = document.getElementById('kb-peek-drawer');
      if (!drawer) return;
      drawer.classList.toggle('open');
    }

    const SPLIT_PANE_CONFIGS = {
      'ws-left': {
        targetId: 'ws-left-pane', targetDefaultSpan: 'lg:col-span-6',
        siblingId: 'ws-right-pane',
        btnId: 'ws-left-expand-btn', defaultLabel: '⤢ Expand Problem', restoreLabel: '↙ Restore 50/50'
      },
      'ws-right': {
        targetId: 'ws-right-pane', targetDefaultSpan: 'lg:col-span-6',
        siblingId: 'ws-left-pane',
        btnId: 'ws-right-expand-btn', defaultLabel: '⤢ Expand Editor', restoreLabel: '↙ Restore 50/50'
      },
      'roadmap-main': {
        targetId: 'roadmap-main-pane', targetDefaultSpan: 'lg:col-span-9',
        siblingId: 'roadmap-left-aside',
        btnId: 'roadmap-expand-btn', defaultLabel: '⤢ Expand Problems', restoreLabel: '↙ Show Chapters'
      },
      'mi-left': {
        targetId: 'mi-left-pane', targetDefaultSpan: 'lg:col-span-7',
        siblingId: 'mi-right-pane',
        btnId: 'mi-left-expand-btn', defaultLabel: '⤢ Expand Reader', restoreLabel: '↙ Restore Split'
      },
      'mi-right': {
        targetId: 'mi-right-pane', targetDefaultSpan: 'lg:col-span-5',
        siblingId: 'mi-left-pane',
        btnId: 'mi-right-expand-btn', defaultLabel: '⤢ Expand Studio', restoreLabel: '↙ Restore Split'
      }
    };

    function restoreAllSplitPanes() {
      Object.keys(SPLIT_PANE_CONFIGS).forEach(k => {
        const cfg = SPLIT_PANE_CONFIGS[k];
        const target = document.getElementById(cfg.targetId);
        const sibling = document.getElementById(cfg.siblingId);
        const btn = document.getElementById(cfg.btnId);
        if (target) {
          target.classList.remove('hidden', 'lg:col-span-12');
          target.classList.add(cfg.targetDefaultSpan);
        }
        if (sibling) sibling.classList.remove('hidden');
        if (btn) {
          btn.textContent = cfg.defaultLabel;
          btn.classList.remove('active');
        }
      });
      state.maximizedSplitPane = null;
    }

    function toggleSplitPaneMaximize(paneKey) {
      const cfg = SPLIT_PANE_CONFIGS[paneKey];
      if (!cfg) return;
      if (state.maximizedSplitPane === paneKey) {
        restoreAllSplitPanes();
        return;
      }
      restoreAllSplitPanes();
      const target = document.getElementById(cfg.targetId);
      const sibling = document.getElementById(cfg.siblingId);
      const btn = document.getElementById(cfg.btnId);
      if (target) {
        target.classList.remove(cfg.targetDefaultSpan);
        target.classList.add('lg:col-span-12');
      }
      if (sibling) sibling.classList.add('hidden');
      if (btn) {
        btn.textContent = cfg.restoreLabel;
        btn.classList.add('active');
      }
      state.maximizedSplitPane = paneKey;
    }

    function toggleZenFullscreen(requestNative = false) {
      const entering = !document.body.classList.contains('zen-fullscreen');
      document.body.classList.toggle('zen-fullscreen', entering);
      if (!entering) closePeekDrawer();
      const btn = document.getElementById('zen-focus-btn');
      if (btn) btn.classList.toggle('active', entering);
      const kbExpBtn = document.getElementById('kb-expand-center-btn');
      if (kbExpBtn) kbExpBtn.classList.toggle('active', entering);
      if (entering && requestNative && document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else if (!entering && document.fullscreenElement && document.exitFullscreen) {
        document.exitFullscreen().catch(() => {});
      }
    }

    function initZenPreferences() {
      try {
        const savedTheme = localStorage.getItem('hub_eye_theme');
        if (savedTheme) setEyeComfortTheme(savedTheme);
        const savedScaleIdx = parseInt(localStorage.getItem('hub_font_scale_idx') || '0', 10);
        if (!Number.isNaN(savedScaleIdx) && savedScaleIdx > 0 && savedScaleIdx < READER_FONT_SCALES.length) {
          activeFontScaleIdx = savedScaleIdx - 1;
          cycleReaderFontScale();
        }
        const savedWidth = localStorage.getItem('hub_kb_width');
        if (savedWidth) setKbContentWidth(savedWidth, true);

        const hideLeftPref = localStorage.getItem('hub_kb-hide-left');
        const hideRightPref = localStorage.getItem('hub_kb-hide-right');
        const hideLeft = hideLeftPref === '1';
        const hideRight = hideRightPref === null ? true : (hideRightPref === '1');
        document.body.classList.toggle('kb-hide-left', hideLeft);
        document.body.classList.toggle('kb-hide-right', hideRight);

        const leftBtn = document.getElementById('kb-toggle-left-btn');
        const rightBtn = document.getElementById('kb-toggle-right-btn');
        if (leftBtn) leftBtn.classList.toggle('active', !hideLeft);
        if (rightBtn) rightBtn.classList.toggle('active', !hideRight);
      } catch (_) {}
    }

