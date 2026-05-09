# QueryQuest Project_25 - Projection Separation Philosophy

## テーマ: 「Runtime ≠ HTML」の維持

---

## Core Principle

**HTMLはprojection viewであり、state sourceではない。**

Runtimeは極小のsemantic stateのみを保持する。
Projection Layerが、そのstateを必要に応じてHTML/Markdown/SVGへ変換する。

これはPHILOSOPHY.mdの「Projection Separation」セクションに準拠する：
- Runtime と UI は分離される
- HTMLはprojection viewである

---

## Architecture

```
┌─────────────────────────────────────┐
│         Runtime (Minimal)           │
│                                     │
│  - session_id                       │
│  - recent_flow []                   │
│  - active_theme ""                  │
│  - last_action ""                   │
│  - runtime_mode ""                  │
│                                     │
│  + events[] (compressed, max:10)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Projection Layer               │
│                                     │
│  - state → HTML/MD/SVG              │
│  - ephemeral generation             │
│  - low-density output               │
│  - on-demand rendering              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         View (HTML/MD/SVG)          │
│                                     │
│  - no state source                  │
│  - read-only                        │
│  - ephemeral                        │
│  - low-attention                    │
└─────────────────────────────────────┘
```

---

## Separation Rules

### Rule 1: Runtime Never Generates HTML

RuntimeはHTMLを生成しない。
Projection Layerが生成する。

### Rule 2: Projection is Ephemeral

Projectionは必要時のみ生成される。
一度生成されたprojectionは、再生成されない限り保持されない。

### Rule 3: State Source is Always Runtime

stateの唯一のsourceはRuntimeである。
HTML/MD/SVGはstateを保持しない。

### Rule 4: Projection is Low-Density

Projectionは低密度で生成される。
大量の情報や詳細な表示は行わない。

---

## Projection Types

| Type | Trigger | Output | Persistence |
|------|---------|--------|-------------|
| minimal_state | always | JSON | runtime only |
| flow_summary | on request | Markdown | ephemeral |
| event_timeline | on request | SVG/HTML | ephemeral |
| theme_status | on request | HTML | ephemeral |

---

## Identity Preservation

**"Quiet Ambient Runtime"** のidentityを維持するため：

- Projectionは静かに生成される
- 過剰な視覚効果は禁止
- 低密度・低注意の出力のみ許可
- "空気のように存在し、必要時だけ現れる"哲学を維持

---

*Project_25 - Projection Separation Philosophy*
*"Runtime ≠ HTML"*
