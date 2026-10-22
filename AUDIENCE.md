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

## How to talk to each audience (same facts, different packaging)
- **Students / youth:** short, quick, a bit of light humour, their world (مذاكرة، سهر، جيم، قهوة ومشروبات طاقة، موبايل). Hooks: challenge, "غلطة بتعملها كل يوم".
- **Parents:** calm and reassuring, practical steps, "إمتى تقلق وإمتى تطمن". Hooks: "لو انت أم/أب…".
- **Older adults:** respectful (حضرتك when addressing directly), simple words, one clear action per slide, no slang or English, mention the family ("ابعتها لماما وبابا").
- **Upper Egypt and Delta, cities and villages:** use general Egyptian Arabic everyone understands — avoid Cairo-only slang and English words; explain any medical term in plain words. Examples should fit everyone (البيت، الغيط، الشغل، المدرسة), not only city life.
- **Every income level:** advice must be doable for free or cheap (مية، نوم، أكل بيتي، فول وعدس وخضار موسمي) — never assume a private doctor, car, AC, gym or expensive products. Mention free public options where they exist (الوحدة الصحية، مستشفى الحكومة، الإسعاف ١٢٣) after verifying them.
- **Traditions and home remedies:** correct them with respect — "ستك وجدتك كانوا بيعملوا كده من حبهم، بس العلم دلوقتي بيقول…". Never mock.
- **Never:** pity, shame, blame, class or regional stereotypes, "الناس الجاهلة", scare tactics, body shaming. Goal = include, reassure, and help everyone.
- Sensitive topics (periods, PCOS, sexual health, mental health): tactful, modest wording and visuals suitable for conservative families.

## What every spec must record (for learning)
In the spec and in topics.md / performance.md add: `audience` (youth | parents | older | general), `ig_time`, `fb_time`, `tone`. The performance loop compares score by audience × time × tone and moves future times/tones toward what wins — and tries one new time slot per week to keep testing.
