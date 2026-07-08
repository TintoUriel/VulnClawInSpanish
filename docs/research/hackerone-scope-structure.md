# Research: HackerOne scope-page structure & program rules

> Linked asset for [#44](https://github.com/JMAN730/VulnClaw/issues/44), part of the
> [/hackerone bug-bounty skill map (#43)](https://github.com/JMAN730/VulnClaw/issues/43).
> Feeds the parse-and-enforce logic of the skill body (#46).

This document answers: **when the agent's `fetch` tool hits a HackerOne program
link, what does it get back, and what structure must the skill parse?**

---

## TL;DR for the skill author

1. **Plain `fetch` of a HackerOne program/scope URL returns almost nothing
   usable.** The site is a JavaScript single-page app; the HTML shell contains
   only the word "HackerOne" and no rendered scope rows. Verified live against
   `https://hackerone.com/security/policy_scopes` — the fetch returned a JS app
   shell with zero scope data. **The fetch-first / paste-fallback decision on
   the map (#43) is correct and, in practice, the paste path is the common
   case, not the exception.**
2. The real scope data is loaded client-side from the **`hackerone.com/graphql`**
   endpoint (needs a CSRF token + cookie) or the authenticated
   **`api.hackerone.com`** REST API. Neither is reachable by a naive
   unauthenticated `fetch`. (API integration is explicitly **Fog** on #43 —
   this research reinforces that fetch-of-HTML alone is insufficient and an API
   path would be the robust alternative if we ever revisit it.)
3. Therefore the fallback parser should target **what a human copies out of the
   rendered scope tab** (tab/space/newline-separated rows), not raw HTML and not
   JSON. A structured example is in [§5](#5-concrete-example-for-the-fallback-parser).

---

## 1. HackerOne URL shapes — public vs login-walled / JS-rendered

`<handle>` is the program's URL slug (e.g. `security`, `slack`, `hackerone`).

| URL shape | What it is | What a plain `fetch` gets |
|---|---|---|
| `hackerone.com/<handle>` | Program profile / policy landing page | JS app shell — no scope rows rendered server-side |
| `hackerone.com/<handle>/policy_scopes` | The scope tab (asset table) | **JS app shell — verified empty** |
| `hackerone.com/<handle>/policy_and_scope` | Program-team edit view of policy + scope | Login-walled (team members only) |
| `hackerone.com/<handle>/scope_versions` | History of scope changes | Login-walled / JS-rendered |
| `hackerone.com/graphql` | Internal GraphQL API the SPA calls | Usable JSON **but** needs CSRF token + session cookie (POST) |
| `api.hackerone.com/v1/...` | Official REST API | Usable JSON **but** needs API-token auth |

**Public vs walled:**

- **Public programs** render their scope + policy to anyone *in a browser*, but
  the data arrives via a client-side GraphQL call — so a server-side HTML fetch
  still sees nothing. Public ≠ fetchable-as-HTML.
- **Private programs** are login-walled entirely; even the browser needs an
  invited, authenticated session. (Private-program auth is **Fog** on #43.)

**Practical rule for the skill:** treat `fetch` of any `hackerone.com/*` URL as
**likely to return no scope data**, detect the empty/shell response, and fall
back to asking the user to paste the scope table. Do not try to parse HackerOne
HTML.

## 2. Asset types in a scope table

A scope entry is a **StructuredScope**. The two representations to know:

**(a) Human-facing labels** (what shows in the rendered table and the asset-type
picker — this is what a *pasted* table will contain):

| Human label | Identifier example |
|---|---|
| Domain | `www.example.com`, `myprogram.com` |
| URL | `www.example.com/app1` |
| Wildcard | `*.example.com`, `*.vpn.hackerone.net` |
| CIDR | `172.200.0.0/16`, `2001:db8::/48` |
| iOS: App Store | App Store hyperlink |
| iOS: Testflight | `com.domainname.myapp` |
| iOS: .ipa | `com.domainname.myapp` |
| Android: Play Store | Play Store application ID |
| Android: .apk | `com.domainname.myapp` |
| Windows: Microsoft Store | `9WZDNCRFHVJL` or `Microsoft.SDKSamples...` |
| Source code | Repo link (e.g. a GitHub URL) |
| Executable | Packaged Linux/Windows/Mac binary |
| Hardware/IoT | Model/make, e.g. `100-440-0.750-3434-A` |
| AI Model | e.g. `LLM-06-12-2023` |
| Smart Contract | Blockchain-explorer URL |
| Other | Free-form; ASNs live here, e.g. `ASN: 13335` |

**(b) API/GraphQL enum strings** (`asset_type` field — what an API/JSON path
would return; useful if #46 ever hardens toward the API). Distinct known values:

```
URL, WILDCARD, CIDR, SOURCE_CODE, DOWNLOADABLE_EXECUTABLES, HARDWARE,
APPLE_STORE_APP_ID, TESTFLIGHT, OTHER_IPA,
GOOGLE_PLAY_APP_ID, OTHER_APK, WINDOWS_APP_STORE_APP_ID,
AI_MODEL, SMART_CONTRACT, OTHER
```

Note the community bug-bounty tooling (`bounty-targets`) filters scopes down to
`%w[URL WILDCARD]` when it wants web targets. For VulnClaw, the direct web-target
set is slightly wider: **`Domain`, `URL`, and `WILDCARD` can all be handed to
`pentest-flow` directly** — a bare `Domain` like `myprogram.com` is a first-class
pentest target (VulnClaw already accepts bare domains; see
`tests/test_agent.py::test_target_detection_domain`). `Domain` is in fact
HackerOne's *default* asset type for a whole domain, with `URL` reserved for a
specific application/path on it — so treating `Domain` as needing special
handling would make #46 silently skip most in-scope web roots. The remaining
types (mobile, source, hardware, and `CIDR`/IP ranges) are either non-web or need
special handling (those non-web assets are **Fog** on #43).

**How in-scope vs out-of-scope is marked:** the scope has two lists —
**In scope** and **Out of scope**. Out-of-scope assets are shown to hackers with
a **red warning** and cannot be selected for submission. In the API this is the
boolean `eligible_for_submission` (`false` ⇒ out of scope / not submittable).

**Guard rule for the skill:** an out-of-scope asset must **never be touched**.
Parse both lists; the out-of-scope list is a deny-list to enforce, not just
metadata.

## 3. Eligibility — in-scope but not bounty-eligible

Two independent booleans per asset:

| Field | Meaning | Effect |
|---|---|---|
| `eligible_for_submission` | Is this asset in scope at all? | `false` ⇒ **out of scope**, do not test, cannot submit |
| `eligible_for_bounty` | Will the program pay for findings here? | `false` ⇒ **still in scope and testable**, but no payout — hacker sees "not a paid asset" warning |

So the tri-state the skill should model per asset:

- **submission=true, bounty=true** → in scope, paid. Prime target.
- **submission=true, bounty=false** → in scope, testable, **unpaid** (VDP-style).
  Test it, but tell the user it won't pay.
- **submission=false** → out of scope. **Never test.**

## 4. Program-rules / policy constraints worth enforcing

These come from HackerOne's platform-wide Code of Conduct plus each program's own
policy text. The skill should surface and enforce them before handing an asset to
`pentest-flow`:

- **No DoS / DDoS / availability impact.** Excessive traffic or request
  generation and anything affecting system availability is prohibited unless a
  program *explicitly* authorizes it. This is the single most important guard for
  an autonomous scanner.
- **Respect rate limits / automation limits.** Programs frequently cap request
  volume and restrict automated scanning; AI-assisted testing must comply with a
  program's automation and rate-limit restrictions. (Concrete throttle mechanics
  are **Fog** on #43.)
- **No social engineering / phishing** of employees, users, or staff.
- **No PII exfiltration / minimal impact.** Don't exploit beyond what's needed to
  demonstrate impact — no dumping databases or hoarding customer data.
- **Automated-scanning restrictions.** Some programs forbid automated scanners
  outright; honor a program's stated "no automated scanning" clause by disabling
  aggressive tool use for that program.

**Enforcement stance for the skill:** these are per-program *policy text* (free
prose in the `instruction` / policy body), so the skill should (a) always apply
the platform-wide guards (no DoS, minimal impact) as hard defaults, and (b) show
the pasted/fetched policy prose to the user and require confirmation before
proceeding on each asset. VulnClaw already has `BLOCKED_PATTERNS` /
`RESERVED_IP_RANGES` guards in `builtin_tools.py` — the scope guard should layer
on top of those, not replace them.

## 5. Concrete example for the fallback parser

When `fetch` fails, the user pastes what they copied from the program's **Scope**
tab. The rendered table has these columns:

> **Identifier · Types · Eligibility for Submission · Eligibility for Bounty ·
> Environmental Score (Max severity) · Instruction**

A copy-paste from that tab typically flattens to whitespace/newline-separated
rows. A representative shape the fallback parser should target:

```
In scope
Asset                         Type       Eligible for Bounty   Max Severity
*.example.com                 Wildcard    Eligible             Critical
www.example.com               URL         Eligible             Critical
api.example.com               URL         Eligible             High
store.example.com             URL         Not eligible         Medium      (in scope, unpaid)
172.16.0.0/16                 CIDR        Eligible             High
203.0.113.10                  IP Address  Eligible             High        (standalone IP, no slash)
myprogram.com                 Domain      Eligible             Critical
com.example.mobile            Android: .apk  Eligible          High
https://github.com/example/core   Source code   Eligible      Medium

Out of scope
Asset                         Type
*.corp.example.com            Wildcard    (internal — do not test)
blog.example.com              URL
support.example.com           URL         (third-party helpdesk)
```

Realistic parser expectations:

- Rows are **not** cleanly delimited — the user may paste tab-separated,
  multi-space, or one-field-per-line depending on their browser/OS. Parse
  leniently: pull the **identifier** (first token that looks like a
  domain/URL/CIDR/wildcard/package-id) and classify its **type** by pattern
  rather than trusting a "Type" column to survive the copy.
- Detect the **"Out of scope"** section header to split the deny-list from the
  allow-list. If the header is missing, treat everything as in-scope but warn
  the user and ask them to confirm the out-of-scope set explicitly.
- Classify identifiers by regex when the type column is lost, **in this order**
  (earlier rules win, so IPs are caught before the generic bare-host rule):
  `*.` prefix → Wildcard;
  value with a `/NN` suffix over a dotted/colon-hex address → CIDR;
  **bare IPv4 (`N.N.N.N`) or IPv6 (`::`/hex-colon) with no slash → IP address**
  (HackerOne lists `IP Address` as its own asset type; a single IP is
  effectively a `/32` and #44 explicitly asked for CIDR/**IP** coverage — don't
  let it fall through to the bare-host/Domain rule and get misclassified);
  `scheme://…/path` or bare `host/path` → URL; bare `host` → Domain;
  reverse-DNS `com.x.y` → mobile package; `github.com/…`/`gitlab.com/…` →
  Source code.
- Map **"Not eligible" / "Not eligible for bounty"** text to the unpaid tri-state
  from §3; do **not** confuse it with out-of-scope.

## Sources

- [Defining Scope | HackerOne Help Center](https://docs.hackerone.com/en/articles/8494552-defining-scope)
- [Asset Types | HackerOne Help Center](https://docs.hackerone.com/en/articles/8486276-asset-types)
- [Asset Details and Scoping | HackerOne Help Center](https://docs.hackerone.com/en/articles/8593105-asset-details-and-scoping)
- [Scope Best Practices | HackerOne Help Center](https://docs.hackerone.com/en/articles/8495670-scope-best-practices)
- [Core Ineligible Findings | HackerOne Help Center](https://docs.hackerone.com/en/articles/8494488-core-ineligible-findings)
- [Code of Conduct | HackerOne](https://www.hackerone.com/policies/code-of-conduct)
- [HackerOne API — hacker reference (StructuredScope)](https://api.hackerone.com/hacker-reference/)
- [bounty-targets — hackerone.rb (GraphQL scope fetch, URL/WILDCARD filter)](https://github.com/arkadiyt/bounty-targets/blob/main/lib/bounty-targets/hackerone.rb)
- Live check: `WebFetch` of `https://hackerone.com/security/policy_scopes` returned a JS app shell with no scope data (2026-07-08).
