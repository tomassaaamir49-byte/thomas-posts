# Audience, timing and tone — who each post is for, when they are online, how to talk to them

Researched 2026-10-22. Re-check the account's own data every Friday and update this file.

## Who is actually following (Metricool, Instagram, Oct 2026, ~290 followers)
- 18–24: ~68% (mostly young men, then young women) → students / young adults are the core today.
- 25–34: ~18% · 13–17: ~7% · 35+: ~8%.
- Goal: keep the young core AND grow parents (25–40) and older adults, mainly through Facebook.
Refresh weekly with `getAnalyticsDataByMetrics(metrics=["IGAG01","IGAG02","IGAG03"])`.

## Who is on which network in Egypt (NapoleonCat, Sep 2026)
- Instagram (~24M): 18–24 = 36%, 25–34 = 35%, 35+ = 29%. Young.
- Facebook (~60M): 25–34 = 33%, 18–24 = 25%, 35+ = 41% (45+ = 20%). Much older and bigger.
→ Topics for older adults / parents of teens / chronic disease: Facebook is the main stage — time the Facebook post for them.
→ Topics for students / young adults: Instagram is the main stage.

## When each audience is online (Cairo time) — starting defaults, then learn from performance.md
Account activity data (Metricool best-time, both networks): strongest 10:00–12:00, second wave 16:00–19:00, drops after 21:00; Friday and Saturday are weaker in the morning.
| Audience | Instagram time | Facebook time | Notes |
|---|---|---|---|
| طلبة وشباب ١٨–٢٤ | 18:00–19:00 (after uni/work) or 21:00–22:00 (night scroll) | 19:00 | Exam seasons (Jan, May–Jun): 22:00–00:00 |
| أمهات وآباء صغيرين ٢٥–٣٩ | 10:00–11:00 (after school run) | 10:00 or 21:00 (after kids sleep) | Parent topics: children's fever, school, food |
| كبار ٤٠+ ومرضى مزمنين | 11:00 | 08:30–10:00 or 18:30–20:00 (after Maghrib) | Pressure, sugar, joints, heart, medicines |
| الكل (عام) | 10:00 or 18:00 | same | Default when audience is mixed |
- Friday: never post 11:30–13:30 (Jumuah). Friday evening (18:00–21:00) is good.
- Ramadan: after iftar (21:00–23:00) and before suhoor (01:00–02:30). Summer holidays: shift youth posts later (22:00).
- Morning slot must stay between 08:30 and 13:00, evening slot between 17:00 and 23:00, at least 5 hours apart.
- When the best time differs by network, schedule Instagram and Facebook as TWO separate Metricool posts at their own times (same media + caption). Each story goes 15 minutes after its own network's post.

## Brand voice — premium, elegant, respectful (applies to every audience)
- The account is a premium medical brand: polished, calm, confident, trustworthy — like a refined clinic, never like a street ad.
- Language: clean, elegant Egyptian Arabic (عامية راقية) — clear and warm, no slang, no vulgar or crowd-pleasing jokes, no exaggeration or panic, no English words. Medical terms explained simply and precisely.
- Examples and imagery: modern everyday life (البيت، الشغل، الجامعة، المدرسة، الجيم، السفر، المكتب). Do NOT reference regions, villages, farming, or social class at all.
- Never: pity, shame, blame, mockery, stereotypes, scare tactics, body shaming, or "cheap" framing.
- Sensitive topics (periods, PCOS, sexual or mental health): tactful, dignified wording and visuals.

## How to talk to each audience (same premium voice, different focus)
- **Students / youth:** sharp and smart, a touch of wit, their world (مذاكرة، سهر، جيم، قهوة، موبايل، مشروبات طاقة). Hooks: challenge, "غلطة بتعملها كل يوم".
- **Parents:** calm, reassuring, practical: "إمتى تقلق وإمتى تطمن". Hooks: "لو انت أم/أب…".
- **Older adults:** respectful (حضرتك when addressing directly), simple and clear, one action per slide, and mention the family ("ابعتها لماما وبابا").
- **Traditions and old habits:** correct them gracefully — "عادة قديمة كلنا اتربينا عليها، بس العلم دلوقتي بيقول…". Never mock.

## What every spec must record (for learning)
In the spec and in topics.md / performance.md add: `audience` (youth | parents | older | general), `ig_time`, `fb_time`, `tone`. The performance loop compares score by audience × time × tone and moves future times/tones toward what wins — and tries one new time slot per week to keep testing.
