# SoFi Pockets — Google Stitch prompts

How to use: paste **Prompt 0** first and let Stitch establish the theme. Then paste
each screen prompt one at a time, in order, into the same project so the design
system carries. Screens marked *optional* can be skipped.

---

## Prompt 0 — Theme and design system (paste this first)

> Design a mobile banking app for iOS called **SoFi Pockets**, aimed at college
> students. It lets a student divide their checking balance into labeled "pockets"
> (Food, Rent, Books, Travel), each with its own virtual debit card in Apple Wallet
> that can only spend from that pocket. Pockets can be shared with roommates.
>
> **Brand colors.** Primary: SoFi Blue `#00A2C7`, Ink `#201747`, Karl the Gray
> `#E5E1E6`. Accents, used sparingly: Buttercup `#FED880`, Cantaloupe `#DD7975`,
> Poppy `#E03E52`, Berry `#A60261`, Eggplant `#330072`. Neutrals: Gunmetal
> `#53565A`, Taupe `#AB989D`.
>
> **Application of color.** Screen headers are a solid SoFi Blue block with white
> knockout text. Page body is a warm off-white (`#F7F5F2`). Content sits in white
> cards, 20px corner radius, very soft shadow. Primary buttons are SoFi Blue with
> white text, fully rounded pill shape. Ink is used for large numerals, headlines,
> and dark feature panels. Each pocket is assigned one accent color used for its
> icon chip, progress bar, and card art.
>
> **Typography.** Use **Larsseit** if available, otherwise **Figtree**. Headlines
> Bold or ExtraBold, tight leading, sentence case. Body copy Regular on light
> backgrounds, Medium when knocked out on dark. Labels and legal in **TT Norms**,
> otherwise **Inter**, Medium. All numerals in tables and transaction rows use a
> monospaced face — **Interstate Mono** if available, otherwise **Roboto Mono** — so
> figures align in columns.
>
> **Signature details.** Large balances render with superscript cents, like
> `$1,284.⁴⁰`. Section headings are preceded by a small all-caps eyebrow label in
> letterspaced Medium at half the headline's size. Dark Ink panels may carry a
> corner motif of thin cyan sine-wave lines. Positive amounts in green, warnings in
> Buttercup amber, never red unless it is an error.
>
> **Bottom tab bar**, 5 items: Home, Banking, Credit card, Invest, Loans. Pockets
> lives under **Banking**, which is the selected tab on every screen.
>
> **Tone.** Confident, plain, a little playful. Never condescending about money.
> No emoji in body copy, but pocket icons may be emoji.

---

## Screen 1 — Pockets home

> Screen: **Pockets home**, inside the Banking tab.
>
> SoFi Blue header: back chevron, title "Pockets", a settings gear. Beneath the
> title, in white knockout: eyebrow "CHECKING", then `$1,284.⁴⁰` large, then a
> smaller line "$212.60 unallocated" with a pill button "Allocate".
>
> Directly below the header, overlapping it slightly, a white **suggested card**
> panel: a small map-pin icon, text "You're near Trader Joe's — pay with
> **Groceries**", a mini card thumbnail in the pocket's green, and a pill button
> "Open in Wallet". A small × to dismiss.
>
> Then a horizontally scrolling **Pocket Perks** strip: eyebrow "POCKET PERKS · NEW
> THIS WEEK", three small cards — "Free fries with any $10+ order, Five Guys",
> "$5 back on Spotify Premium", "20% off Amtrak, book by Sunday". Each has a
> partner logo placeholder and an "Activate" pill.
>
> Then eyebrow "YOUR POCKETS" and a 2-column grid of pocket tiles. Each tile: an
> emoji in a colored circular chip, pocket name, balance in large mono numerals, a
> thin progress bar in the pocket's accent color showing how much of this month's
> budget is left, and a caption like "$88 left of $200". Tiles:
> - 🍜 Food — `$128.⁴⁰` — cyan — "$128 left of $300"
> - 🛒 Groceries — `$74.¹²` — green — "$74 left of $150"
> - 🏠 Rent — `$1,650.⁰⁰` — Eggplant — **joint**, shows a stack of 3 small circular
>   avatars in the corner and a "Shared" tag
> - 📚 Books — `$210.⁰⁰` — Buttercup — "$210 left of $400"
> - 🚌 Transit — `$18.⁵⁰` — Taupe — low, so its progress bar is amber and it shows a
>   small warning triangle
> - ✈️ Spring Break — `$340.⁰⁰` — Berry — **joint**, 4 avatars, "Shared"
>
> Last cell of the grid is a dashed-outline "+ New pocket" tile.
>
> Bottom tab bar with Banking selected.

---

## Screen 2 — Pocket detail (solo)

> Screen: **Food pocket detail**.
>
> Header block in the pocket's cyan: back chevron, "🍜 Food", overflow menu.
> Centered: `$128.⁴⁰` very large in white, caption "of $300 this month". A slim
> white progress bar beneath.
>
> Two pill buttons side by side, white on cyan: "Add money" and "Move money".
>
> White card: a realistic **virtual debit card** rendered in cyan with the SoFi
> wordmark, "FOOD" in small caps, `•••• 4417`, and "VIRTUAL" in a corner tag. Below
> it a black "Add to Apple Wallet" button and two text actions with icons: "Card
> details" and "Freeze card".
>
> White card: eyebrow "AUTO-FUND", one row — "Every deposit, fill this pocket with
> **$300**" with a toggle set on, and a subtext "Next: Aug 15 financial aid".
>
> White card: eyebrow "THIS MONTH", a transaction list with monospaced amounts.
> Rows: "Chipotle — Jul 27 — −$14.²⁰" with a small Pocket Perks tag reading
> "$2 back earned"; "Sweetgreen — Jul 26 — −$16.⁸⁵"; "Dining Hall Add-On — Jul 24 —
> −$45.⁰⁰"; "Panda Express — Jul 22 — −$11.⁷⁵". Each row has a merchant logo
> placeholder circle. A "See all" text link.

---

## Screen 3 — Low balance warning state

> Same as the Food pocket detail screen, but for **🚌 Transit** and in a low-balance
> state. Header block uses Taupe. Balance reads `$18.⁵⁰` of $80.
>
> Directly under the balance, a Buttercup-amber banner with a warning triangle:
> "Running low. Cards decline when a pocket is empty — pockets never borrow from
> each other." A pill button "Add money".
>
> Everything else matches Screen 2.

---

## Screen 4 — Create a pocket

> Screen: **New pocket**, a full-page sheet with a close ×.
>
> Headline "What's this pocket for?"
>
> Eyebrow "START FROM A TEMPLATE", then a wrapping grid of selectable chips, each
> with an emoji: 🍜 Food, 🛒 Groceries, 🏠 Rent & Utilities, 📚 Books & Supplies,
> 🚌 Transit, 🎬 Subscriptions, 🎉 Going Out, 🧺 Laundry, ✈️ Travel, 💊 Health,
> 🐣 Emergency, ✨ Custom. "🍜 Food" is selected, filled cyan.
>
> Eyebrow "NAME", a text field pre-filled "Food".
>
> Eyebrow "COLOR", a row of 8 circular color swatches using the brand accents, the
> cyan one selected with a ring.
>
> Eyebrow "MONTHLY AMOUNT", a large centered input showing `$300` with a numeric
> stepper, and beneath it "You have $212.60 unallocated" in Gunmetal.
>
> Eyebrow "AUTO-FUND", a card with a toggle on: "Refill from every deposit", subtext
> "Rent and Books fill first, then this pocket."
>
> A row of two options presented as large selectable cards: "Just me" (selected,
> cyan border) and "Share with friends" (with a small avatar-stack icon).
>
> Sticky bottom primary button: "Create pocket".

---

## Screen 5 — Joint pocket detail

> Screen: **Rent pocket detail — shared**.
>
> Header block in Eggplant `#330072`. Back chevron, "🏠 Rent", overflow menu. A
> "SHARED" tag. Centered `$1,650.⁰⁰` in white, caption "of $1,800 due Aug 1". Slim
> progress bar showing 92%. A stack of 3 circular avatars with a "+ Invite" circle.
>
> Two white pill buttons: "Add my share" and "Pay rent".
>
> White card: eyebrow "MEMBERS". Four rows, each with avatar, name, a contribution
> chip, and a status:
> - Sammy (You) — "33% · $600" — ✅ "Paid Jul 25"
> - Maya R. — "33% · $600" — ✅ "Paid Jul 24"
> - Dev P. — "34% · $600" — 🕐 "Due in 4 days", with a "Remind" text button
> - Jordan L. — "—" — grey row, italic "Invite pending", with "Resend"
>
> White card: the shared virtual card in Eggplant, "RENT · SHARED", `•••• 8802`,
> "Add to Apple Wallet" button, and a line "All 4 members hold this card."
>
> White card: eyebrow "ACTIVITY", showing who spent what — "Maya paid Greystone
> Property Mgmt — Jul 1 — −$1,800.⁰⁰" with Maya's avatar on the row; "Dev added
> money — Jun 28 — +$600.⁰⁰"; "Sammy added money — Jun 27 — +$600.⁰⁰". Amounts
> monospaced, deposits green.
>
> Small Gunmetal footnote at the bottom: "A shared pocket is a joint account. Every
> member can access the full balance."

---

## Screen 6 — Invite friends to a pocket

> Screen: **Invite to Rent**, a full sheet.
>
> Headline "Who's splitting this?" Subhead "Everyone needs a SoFi account to join a
> shared pocket."
>
> A search field "Search contacts", then a horizontal row of selected people as
> chips with avatars and small ×: Maya R., Dev P.
>
> A contact list below with avatars, names, and a right-side state: "Has SoFi" in
> cyan with a checkmark, or "Will be invited" in Gunmetal. Include 5 rows.
>
> Eyebrow "HOW TO SPLIT", a segmented control with three options: "Evenly"
> (selected), "By percent", "Custom amounts".
>
> A card showing the resulting split as editable rows: "Sammy (You) — 33% — $600",
> "Maya R. — 33% — $600", "Dev P. — 34% — $600", with a total row "Total — 100% —
> $1,800" in bold.
>
> An Ink panel with a Buttercup box-eyebrow bar above knockout text: "Money lands in
> the pocket before rent is due. No chasing anyone on Venmo."
>
> Sticky primary button "Send invites".

---

## Screen 7 — Invite received

> Screen: **You've been invited**, a centered full-page state.
>
> Top: a large circular avatar of Maya with a small 🏠 emoji badge. Headline
> "Maya invited you to a shared pocket." Beneath, a large Ink card: "🏠 Rent",
> "$1,800 / month", and a row of avatars of the other members.
>
> White card: eyebrow "YOUR SHARE", `$600.⁰⁰` large and monospaced, caption "33%,
> due the 1st of each month". A row "Auto-pay my share each month" with a toggle on.
>
> White card: eyebrow "WHAT YOU GET", three rows with icons: "A shared debit card
> for rent", "See every payment the group makes", "Reminders before rent is due".
>
> Small Gunmetal legal text: "Shared pockets are joint accounts. All members can
> view and access the full balance. Contribution splits are a group agreement, not a
> spending limit."
>
> Two stacked buttons: primary "Join and add $600", secondary text "Decline".

---

## Screen 8 — Card details and Apple Wallet

> Screen: **Card details** for the Food pocket.
>
> Ink background, cyan sine-wave line motif in the top-right corner.
>
> Centered: the virtual card rendered large in cyan, with the full number revealed
> as `4417 8802 3391 0264`, "EXP 09/29", "CVV 481", cardholder "SAMMY CHEN", and a
> "VIRTUAL" tag. A small copy icon next to the number.
>
> Below, a black "Add to Apple Wallet" button, full width.
>
> A white card containing a list with icons and right chevrons: "Set as Wallet
> default" with a toggle off and subtext "Double-click the side button to pay from
> Food"; "Freeze card" with a toggle; "Get a new number"; "Spending limits";
> "Transaction notifications" with a toggle on.
>
> Footnote in Taupe: "This card only spends from your Food pocket. It declines if
> the pocket is empty."

---

## Screen 9 — Location-triggered notification

> Screen: **iPhone lock screen** showing a push notification, rendered over a
> blurred abstract wallpaper in Ink and cyan.
>
> The notification is a rounded card with the SoFi app icon, title "SoFi Pockets",
> timestamp "now", body: "**At Trader Joe's?** Pay with your Groceries card —
> $74.12 available." Two inline action buttons on the notification: "Open in Wallet"
> and "Use a different pocket".
>
> Below it, a second, dimmer stacked notification, partially visible: "Chipotle
> $14.20 paid from Food. $2.00 back from Pocket Perks."

---

## Screen 10 — Transaction detail with re-routing

> Screen: **Transaction detail**.
>
> Header: back chevron, "Transaction".
>
> Centered: a merchant logo placeholder circle, merchant name "Target", `−$62.⁴⁰`
> very large in Ink monospaced, "Jul 27 at 4:12 PM", and a green "Completed" chip.
>
> White card: eyebrow "PAID FROM", a row showing a cyan 🍜 chip, "Food",
> `•••• 4417`, and a text button "Change".
>
> An amber Buttercup banner: "Mixed basket? Move part of this to another pocket."
> With a pill button "Split this charge".
>
> White card: eyebrow "MOVE TO A DIFFERENT POCKET", a horizontal row of selectable
> pocket chips with emoji and balances — 🛒 Groceries $74.12, 🧺 Laundry $30.00,
> 📚 Books $210.00, 🎉 Going Out $55.00.
>
> White card: eyebrow "DETAILS", rows for "Category — Groceries", "Merchant
> category code — 5411", "Card — Food virtual card".
>
> Sticky secondary button: "Report a problem".

---

## Screen 11 — Pocket Perks

> Screen: **Pocket Perks**, a rewards hub.
>
> Header: an Ink block with a Buttercup box-eyebrow bar above knockout headline
> "Perks for paying from a pocket." Beneath it, monospaced `$38.⁵⁰ earned this
> semester`. Cyan sine-wave motif in the corner.
>
> A countdown strip in cyan: "NEW DROP IN 2 DAYS · WEDNESDAYS".
>
> Eyebrow "THIS WEEK", a vertical list of large offer cards. Each card has a partner
> logo placeholder, bold offer text, a qualifying-pocket tag, an expiry, and an
> "Activate" pill that becomes a green "Activated ✓" state on some cards:
> - "Free large fries with any $10+ order" — Five Guys — tag "🍜 Food" — "Ends Sunday"
>   — Activated
> - "$5 back on your next month" — Spotify — tag "🎬 Subscriptions" — "3 days left"
> - "20% off any Northeast route" — Amtrak — tag "✈️ Travel" — "Ends Aug 3"
> - "$3 back on a $25 shop" — Trader Joe's — tag "🛒 Groceries" — "Ends Friday"
> - "Free medium coffee" — campus cafe — tag "🍜 Food" — "Today only"
>
> Eyebrow "EARNED", a compact list with dates and green monospaced amounts:
> "Five Guys — Jul 21 — +$4.²⁹", "Chipotle — Jul 27 — +$2.⁰⁰", "Spotify — Jul 3 —
> +$5.⁰⁰".
>
> A small Gunmetal footnote: "Offers are funded by our partners. Perks apply when
> you pay with the matching pocket's card."

---

## Screen 12 — Move money between pockets

> Screen: **Move money**, a half-height bottom sheet over a dimmed Pockets home.
>
> Handle bar, headline "Move money".
>
> A "From" row: a card with a cyan 🍜 chip, "Food", "$128.40 available". A circular
> swap button with vertical arrows overlapping between the two rows. A "To" row: a
> card with an amber 🚌 chip, "Transit", "$18.50".
>
> A large centered amount in Ink monospaced: `$40.⁰⁰`, with a caption "Food will
> have $88.40 left".
>
> A row of quick-amount pills: "$10", "$20", "$40", "All".
>
> A numeric keypad occupying the lower half.
>
> Sticky primary button "Move $40".

---

## Screen 13 *(optional)* — Semester runway

> Screen: **Semester runway**, the college-specific budgeting view. Reached from the
> Pockets home.
>
> Ink header panel with cyan sine-wave corner motif. Eyebrow "FALL SEMESTER", large
> knockout headline `$2,412.⁰⁰`, caption "has to last until December 15 — 140 days".
>
> A large **burn-down chart**: a descending line from today to Dec 15, with a
> dotted "on pace" reference line and the actual line above it in Buttercup,
> labeled "You're 6 days ahead of pace". X-axis labeled by month, Aug through Dec.
>
> A prominent white card: eyebrow "SAFE TO SPEND", `$27.⁵⁰ / day` in very large Ink
> monospaced, and beneath, in amber, "You've averaged $31.20 a day this week."
>
> White card: eyebrow "WHAT'S DRIVING IT", a horizontal stacked bar broken into
> pocket accent colors, with a legend listing 🍜 Food 34%, 🏠 Rent 28%,
> 🛒 Groceries 16%, 🎉 Going Out 12%, other 10%.
>
> White card: eyebrow "MONEY COMING IN", two rows — "Aug 15 — Financial aid
> disbursement — +$2,100.⁰⁰" and "Every other Friday — Campus job — +$310.⁰⁰".
>
> A cyan pill button "Adjust my pockets".

---

## Screen 14 — Empty state / onboarding

> Screen: **Pockets onboarding**, first run.
>
> Top two-thirds is a SoFi Blue panel with a 3D-collage-style illustration: an
> oversized chrome debit card splitting into several smaller colored cards, on a
> cyan gradient with a floating Buttercup circle and an Eggplant sphere. Playful,
> glossy, slightly surreal.
>
> Knockout headline "One checking account. As many pockets as you need."
> Subhead "Give every dollar a job, and a card that only spends it there."
>
> White sheet below with three rows, each an icon and one line: "A virtual card per
> pocket, right in Apple Wallet", "Share a pocket with roommates for rent and
> groceries", "Earn partner perks when you pay from a pocket".
>
> Primary button "Set up my pockets", secondary text link "Maybe later".

---

## Notes for whoever runs these

- **Screen 3, 9, and 10 are the credibility screens.** Anyone reviewing this will
  immediately ask "what happens when a pocket is empty" and "what about Target."
  Those three answer it.
- Stitch will not have Larsseit or Interstate Mono. The fallbacks are specified in
  Prompt 0; expect to swap the real faces in Figma afterward.
- Do not let Stitch add APY, interest, or savings-goal language anywhere — pockets
  are Checking (D8).
- Do not let it write "your share is locked" or "protected" on any joint screen.
  See L1 in `decisions.md`; the wording in Screens 5 and 7 is deliberate.
