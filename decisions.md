# SoFi Pockets — Decisions & Open Issues

Last updated: 2026-07-28

## Concept

Spendable sub-accounts inside SoFi Checking. A student divides their balance into
**Pockets** (Food, Rent, Books, Travel…). Each pocket gets its own **virtual debit
card** provisioned to Apple Wallet; paying with that card draws only from that
pocket's balance. Pockets can be **joint** — the creator invites friends/roommates,
each member commits a dollar amount or percentage, and the group shares a card for
rent, groceries, or a break trip. Targeted at college students. Paying with a
pocket card earns **rewards** (T-Mobile-Tuesdays-style).

Distinct from SoFi **Vaults**, which are savings-side buckets with no card and no
spend capability. Naming collision needs resolving — see Open Questions.

---

## Locked decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Pocket cards are **virtual**, not disposable/burner | Recurring charges (rent, subscriptions) need a persistent PAN. Burner cards are a separate feature if we want them at all. |
| D2 | Overspending a pocket = **hard decline** | Preserves the envelope model. No auto-spillover, no cross-pocket borrowing. |
| D3 | Hard-decline UX is **out of scope for the UI mockup** | Mockup shows the happy path. Decline handling must be designed before build — see F1. |
| D4 | Joint pockets are backed by a **true joint account** | Clean co-ownership; avoids one member "gifting" money to a host. |
| D5 | **All joint pocket members must have a SoFi account** | Required for joint-account KYC. Accepted cost to the viral loop — see F2. |
| D6 | Right card surfaced by **location / spend-pattern signals** | Solves card-selection friction without collapsing to one card. Mockup can show this as a suggestion; see T1 for what's actually buildable. |
| D7 | Pocket-card spend earns **rewards** | Engagement + differentiation. |
| D8 | Pockets live in **Checking** | Simple mental model; pockets are for spending, not saving. Tiles show balance only — **no APY, no interest earned** anywhere in the UI. Vaults remain the savings-side product. |
| D9 | Rewards = **merchant/partner offers**, T-Mobile-Tuesdays style | Free fries, a discount at a partner, % back at a specific merchant. Vendor-funded, so it survives Durbin-capped interchange. Working name: **Pocket Perks**. |
| D10 | Card suggestion surfaces as **push + in-app hero**, not Wallet reordering | Wallet cannot be steered programmatically — see T1. |

---

## Deferred — must resolve before build (F)

### F1. Hard-decline experience
Student has $3 in Food, taps for $40 at a register. Declining in front of people is
a churn event. Needs: pre-decline warning (push at 80% / 95% of pocket balance),
low-balance badge in Wallet-adjacent surfaces, one-tap top-up from the decline
notification, and a decision on whether Reg E overdraft opt-in is offered at all.
Nothing here appears in the v1 mockup, but the low-balance *warning* state probably
should.

### F2. Viral loop is gated by the SoFi-account requirement
D5 means every invite is a signup wall. Needs an invite flow that pre-fills the
pocket context through account opening, and a decision on what a pending
(un-onboarded) member looks like in the UI — placeholder avatar, greyed row, or
hidden until they join.

### F3. Roommate turnover
Joint accounts generally cannot have owners removed — the account is closed and
re-papered. A 12-month lease cycle means annual churn on every rent pocket. Needs
a supported "someone moves out" path, and a UI answer for settling a departing
member's balance.

### F4. ~~Where do pockets live?~~ → RESOLVED (D8)
Checking. No APY surface anywhere. Remaining sub-question: does idle pocket money
ever get swept to Savings, or is "money sitting still earns nothing" an accepted
tradeoff? Probably fine for v1 — students hold small balances.

### F5. Rewards — partner supply and attribution
Mechanic is settled (D9: merchant offers). What isn't:
- **Partner supply.** Merchant-funded offers need actual signed vendors. Who are the
  launch partners, and are they national (Chipotle, Spotify, Amtrak) or
  campus-local (the pizza place off-campus)? Campus-local is far more compelling
  and far harder to source at scale. Realistic path is an aggregator
  (Cardlytics/Fidel-style card-linked offer network) plus a handful of marquee
  direct deals.
- **Pocket targeting.** Is an offer tied to a pocket category (a food offer only
  redeems on the Food card) or to any pocket card? Category-tying is the
  differentiator — it's the reason pockets exist — but it means a student who put
  Chipotle in "Going Out" instead of "Food" silently loses the perk.
- **Joint attribution.** Who earns the reward on a shared card — the member who
  swiped, or the group? Splitting a $5 credit five ways is absurd; giving it to the
  swiper creates a race to be the one who pays.
- **Cadence.** A weekly "drop" is the T-Mobile Tuesdays hook. If any part of it is
  chance-based rather than a flat published offer, see L6.

### F6. Deposit allocation
Financial aid and refunds arrive as single lump ACH credits; they cannot be split at
the source. Payroll direct deposit *can* be split. Needs auto-allocation rules that
fire on deposit ("when money lands, fill Rent first, then 20% to Food…") and a UI
for unallocated balance.

### F7. White text on SoFi Blue fails contrast
The mockups put white knockout text on SoFi Blue `#00A2C7`, which is roughly 2.6:1 —
below the 4.5:1 WCAG AA threshold for body text and below even the 3:1 large-text
threshold. This matches how the live SoFi app renders its cyan header, so the mockups
are brand-faithful rather than wrong, but it is a real accessibility defect that will
surface in review. Options: darken the header fill for text-bearing areas, use Ink
`#201747` for text on cyan, or accept and document it. Not resolved.

### F8. Pocket lifecycle
Closing a pocket with a balance, closing with pending authorizations, per-user
pocket cap (Wallet clutter and performance), virtual card expiry rotation for
subscription pockets.

---

## Legal & compliance edge cases (L)

### L1. In a joint account, contribution percentages are not legally enforceable
Every joint owner has full withdrawal rights over the entire balance. If Alex
commits 30% and Sam commits 70%, Sam can still withdraw 100%. The contribution
split is a UI convention and an accounting ledger, **not** a legal restriction.
Anything in the interface implying otherwise is a UDAAP problem — do not use copy
like "your share is protected" or "locked." Consider explicit disclosure at invite
acceptance.

### L2. Number of joint owners
Multi-owner joint accounts are commonly capped (often 2–4). A 5-roommate rent
pocket may exceed what the core banking platform or the account agreement supports.
Confirm the ceiling; it caps the group-pocket use case.

### L3. Joint liability
All owners are liable for overdrafts and negative balances on a joint account, and
adverse activity can follow all of them. One roommate's behavior becomes everyone's
problem.

### L4. Disputes and friendly fraud
Any joint owner can dispute a transaction made by another joint owner. A roommate
claiming an unauthorized charge on a shared card is both a real fraud vector and an
operational nightmare — who receives the provisional credit?

### L5. KYC and age
Every member needs full KYC. Under-18 students (some freshmen) cannot open a joint
account independently, which cuts off part of the target market.

### L6. Rewards may be a sweepstakes
A T-Mobile-Tuesdays-style prize drop is regulated promotional activity — official
rules, no-purchase-necessary considerations, state registration/bonding above
certain prize values, and exclusions in some states. If the mechanic involves
chance rather than a flat earn rate, this becomes a legal workstream, not a feature.

### L7. Rewarding spend inside a budgeting product
Rewards incentivize spending; pockets exist to constrain it. The tension is a brand
and regulatory exposure, sharpened by marketing to college students. Prefer rewards
that fire on *behavior* (funding a pocket, staying under budget, on-time rent) over
rewards that fire on *volume*.

### L8. Location data
Geofenced card suggestions require "Always" location permission, plus GLBA and
state privacy (CCPA/CPRA) treatment of location data. Needs a clear value exchange
at the permission prompt and a fully functional non-location fallback.

### L9. FDIC
Joint accounts are insured $250k per co-owner; not a practical constraint here, but
disclosure copy must be correct.

---

## Technical constraints (T)

### T1. Apple Wallet cannot be steered programmatically
A third-party issuer **cannot** change which card Wallet presents when the user
double-clicks, and cannot reorder Wallet. So "location detects you're at Trader
Joe's and Wallet shows your Groceries card" is not buildable as described.

What *is* buildable, and what the mockup should show:
- A geofenced/pattern-triggered **push notification**: "At Trader Joe's — pay with
  your Groceries card," tapping through to the card.
- An in-app **suggested card** hero on the home screen.
- Guidance to set the most-used pocket as the Wallet default.
- Post-transaction **re-routing** as a fallback for the wrong-card case.

### T2. One PAN per pocket
Each pocket card is a separate provisioned credential. Multiplies tokenization
calls, BIN capacity, expiry rotation, and fraud-model surface per user.

### T3. MCC routing is unreliable where students spend
Merchant category codes cannot split a mixed basket. Target, Walmart, Amazon, and
campus bookstores all resolve to a single MCC, which is why post-transaction
re-routing (T1) matters.

---

## Still open (not blocking the mockup)

1. **Naming** — "Pockets" vs existing SoFi "Vaults." Also note One/OnePay ships a
   feature named Pockets and Monzo's Pots cover similar ground; worth a competitive
   check before committing.
2. **College framing** — the semester-runway model ("$2,400 must last until Dec 15,
   you're burning $31/day") is the strongest student-specific angle and no
   competitor has it. In or out of v1? It changes the pocket detail screen from a
   balance to a burn-down. Mocked as an **optional screen** in the Stitch prompt so
   it can be dropped.
3. **Parent-funded pockets** — not yet decided. Strong acquisition wedge, real
   surveillance concern.
4. **Physical card** — every pocket card is virtual (D1). Does the student still
   carry one physical SoFi debit card, and which pocket does it draw from?

---

## Brand spec (extracted from `Brand Guidelines.pdf`, "Design and Art Direction 2025")

### Color

| Tier | Name | Hex |
|---|---|---|
| Primary | SoFi Blue | `#00A2C7` |
| Primary | Ink | `#201747` |
| Primary | Karl the Gray | `#E5E1E6` |
| Secondary | Buttercup | `#FED880` |
| Secondary | Cantaloupe | `#DD7975` |
| Secondary | Poppy | `#E03E52` |
| Secondary | Berry | `#A60261` |
| Secondary | Eggplant | `#330072` |
| Tertiary | Gunmetal | `#53565A` |
| Tertiary | Taupe | `#AB989D` |

Guidance from the deck: colors are "bold, vibrant, elevated." SoFi Blue and Ink
carry most surfaces; secondaries are accents. The live app pairs the cyan header
with a warm off-white body — Karl the Gray is the on-brand equivalent.

### Type

- **Larsseit** — headlines in Bold / ExtraBold. Body copy also Larsseit: Regular for
  dark text on light backgrounds, Medium for knockout (light on dark).
- **TT Norms** (usually Medium) — legal, callouts, and web.
- **Interstate Mono** — strictly for tabulated numerals.

### Graphic elements

- **Box eyebrow** — short Buttercup bar above a knockout headline inside an Ink box.
  Bar is 1/3 the height of a cap letter, as wide as the first 3 letters, sitting
  3 bar-heights above the cap line.
- **Text eyebrow** — all-caps label in Larsseit Medium, tracking 25, at half the
  height of the headline beneath it.
- **Highlight** — short Berry rule used to emphasize a fragment of a headline.
- **Pattern** — cyan sine-wave lines on Ink, used as a corner motif.
- **Brandscape** — 3D collage illustration: chrome, gold, marble, sneakers,
  oversized objects. Reference `Sofi DAM_ Collection Preview.pdf`.

### Existing app conventions (from the three screenshots in this directory)

Cyan header block with greeting and pill CTAs → white rounded cards (~16–20px
radius) on warm off-white → bottom tab bar (Home / Banking / Credit card / Invest /
Loans). Large balances use superscript cents (`$27,282.¹²`). Green for gains, amber
for "pacing high" warnings. Pockets should read as a section inside **Banking**.
