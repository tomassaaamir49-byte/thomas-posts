# Daily Instagram workflow — @thomassamir_medical_student

Account owner: توماس سمير فوزي, طالب طب بشري (medical student — NOT a doctor).
Goal: grow followers, reach and engagement with Egyptian-Arabic medical awareness for the general public.
Metricool brand (blogId): 7301767. Networks: instagram AND facebook (page "توماس سمير طالب طب بشري"). Timezone: Africa/Cairo.
ONE CAROUSEL + ONE STORY per day (user's decision 2026-10-24, to stay inside the Metricool plan limit; no reels).
- The carousel is ONE Metricool post with providers [instagram, facebook] at ONE time — it goes to Instagram and is shared to Facebook at the same moment. Never split Instagram and Facebook into separate posts.
- The story is ONE Metricool post with providers [instagram, facebook] (type STORY on both), 15 minutes after the carousel.
- The single daily time (08:30–23:00) is chosen from the post's target audience in AUDIENCE.md and what performance.md shows works best on Instagram (the main stage).
## MANUAL MODE (user's decision 2026-10-25) — overrides the Metricool scheduling steps below
The Metricool plan limit was reached, so the user publishes by hand. Each run: prepare the post exactly as below (performance loop, research, quality bar, render, commit, push), but do NOT call createScheduledPost. Instead deliver to the user with SendUserFile: slide_01..slide_NN.jpg in order, story.jpg, and caption.txt (the spec's caption), then a short Egyptian-Arabic message with the recommended publish time for Instagram + Facebook together, the story 15 minutes later, and the suggested song. Metricool is still used read-only for analytics (performance loop). Mark the row in topics.md / performance.md as "manual".

Folders/specs are named `<date>` (e.g. posts/2026-10-25, specs/2026-10-25.json). Older days used `<date>-am` / `<date>-pm`.


## Audience first (read AUDIENCE.md every run)
- Decide each post's `audience` (youth | parents | older | general) BEFORE writing it, and write the whole post in that audience's tone (AUDIENCE.md → "How to talk to each audience"). Premium, elegant brand voice (AUDIENCE.md → "Brand voice"): refined Egyptian Arabic, calm and confident, no slang, no references to regions, villages or social class; no pity, shame, mockery or stereotypes.
- Pick ONE `time` for that audience from AUDIENCE.md, adjusted by what performance.md shows works. Instagram and Facebook always publish together as one post.
- Across the week, cover all audiences (youth, parents, older adults) — don't serve only one group.
- Every Friday: refresh AUDIENCE.md with the account's demographics (IGAG01–03) and what performance.md says about times/tones, and try one new time slot that week.

## Freshness — every post must feel different from the one before it
- THEME: render each post with a different colour theme than the previous post: `POST_THEME=<ocean|emerald|violet|sunset|rose|teal> python3 tools/...`. Record the theme in topics.md and never reuse the previous post's theme.
- ANGLE: never use the same content angle (myth/red-flags/mistakes/body-explainer/first-aid/quiz "صح ولا غلط"/numbers & facts) twice in a row; vary the hook style (question, shocking fact, "غلطة بيعملها ٩٠٪", challenge).
- TOPIC BANK: start from `topics_bank.md` (researched list of what Egyptians search for + seasonal topics + hook formulas). Prefer the 'Seasonal NOW' section while in season, mix with evergreen/Egypt-specific ones, and pick topics that speak to a specific person (أم، طالب، مريض سكر…) because those get shared. Once a week (Fridays) refresh the bank with a quick search and commit it.
- WHAT THE AUDIENCE NEEDS NOW: before choosing topics, (1) WebSearch what health topics are in the news / trending in Egypt this week and what season it is (heat, flu season, exams, Ramadan, school start, outbreaks, viral myths) and pick topics people are searching for right now; (2) check Metricool analytics for the account's recent posts (getAnalyticsDataByMetrics — reach, saves, shares, plays) and lean toward the formats/topics that performed best.
- MUSIC: Instagram's publishing API only allows music on reels, not carousels (Metricool returns AUDIO_NOT_APPLICABLE). Do NOT send audioConfiguration on carousels. In the final message, suggest one fitting, currently popular song name per post that the user can add by hand in the Instagram app if they want.

## Stories — a teaser story for EVERY carousel (cover only, not the whole post)
- After rendering a carousel, make its story: `POST_THEME=<same theme> python3 tools/make_story.py posts/<date>/slide_01.jpg posts/<date>/story.jpg "<teaser>"`.
  The teaser is ONE short Egyptian-Arabic curiosity line that makes people open the profile without giving the answer, different every time (e.g. "الخرافة رقم ٤ أغلبنا مصدقها", "٦ علامات لازم كل أم وأب يعرفوها", "الغلطة رقم ٢ بنعملها كل يوم"). The image already says "بوست جديد", points at the name ("اضغط على اسمي") and says "البوست كامل على البروفايل".
- Commit/push story.jpg with the post, then schedule it 15 minutes after the post with `createScheduledPost`, providers [instagram, facebook], instagramData type STORY, facebookData type STORY, NO text, autoPublish true, media = story.jpg raw URL.
- If Facebook refuses the story, still schedule the Instagram one and report it.
- Plan limit: if any provider shows "You have reached your Metricool account limit", nothing can be published until the plan limit resets or is upgraded — say so first in the final message (do not keep creating posts that will fail).
- Failure check (start of every run): `getScheduledPosts` for today and yesterday; any provider with status ERROR (Instagram stories sometimes fail with "media cannot be found") → if its time slot hasn't passed by more than a few hours, reschedule it once from the GitHub raw URL, and always list every failure in the final message.

## Performance loop — learn from every post (do this FIRST each run)
1. Pull Instagram post stats for the last 14 days: `getAnalyticsDataByMetrics(brandId=7301767, metrics=["IGPO02","IGPO06","IGPO07","IGPO14","IGPO28","IGPO13","IGPO08","IGPO15","IGPO27","IGPO29"])` (date, url, type, reach, views, likes, comments, saves, shares, follows).
2. Add/refresh each post's row in `performance.md` (match by date/time to topics.md) and compute its score. Record audience, time and tone for each post too, so the loop learns which time and tone work for which audience.
3. Before choosing tomorrow's topics, read performance.md: repeat what is in the top third (topic family, angle, hook style, audience, slide count), avoid what is in the bottom third, and try ONE new experiment per day (new hook style or format) so the account keeps improving. Write one line under "## Lessons" in performance.md each run (what worked / what to try).

## Quality bar — every carousel must pass ALL of these before it is scheduled
1. Cover = scroll-stopper: ≤ 9 words, contains a number OR a direct question OR a bold claim, and names a specific person/problem ("لو انت أم…", "لو بتذاكر…"). A curiosity gap: it promises something the reader must swipe to get.
2. Slide 2 delivers value immediately — no intro, no "في البوست ده هنعرف".
3. One idea per slide, title ≤ 7 words, body ≤ 25 words, plain Egyptian Arabic a 15-year-old understands.
4. 7–9 slides total (more dwell time; Instagram re-shows carousels from slide 2 to people who skipped).
5. At least one surprising/counter-intuitive fact that makes people say "مكنتش أعرف".
6. A save trigger: second-to-last slide is a `checklist` slide ("الخلاصة في صورة واحدة" / "احفظها") summarising the whole post in 3–5 ticks.
7. A share trigger aimed at a specific person in the CTA + caption ("ابعتها لماما"، "منشن صاحبك اللي…").
8. A comment prompt with an easy answer (a number, a word, an emoji): "قولّي رقم الغلطة اللي بتعملها".
9. Caption: first line = keyword + hook (< 125 characters), then value, CTA, source, disclaimer, 3–5 relevant Arabic hashtags.
10. Visually checked: no overflow, readable at phone size, colour theme different from the previous post.
If any item fails, fix it before scheduling. Rewrite the hook up to 3 times and keep the strongest.

## Carousel formats to rotate (never the same format twice in a row)
numbered list (٥ علامات / ٣ أكلات) · myth vs fact · quiz "صح ولا غلط" (question slide → answer slide) · mistakes ("غلطات بنعملها") · "إيه اللي بيحصل لجسمك لو…" step by step · comparison ("الفرق بين البرد والإنفلونزا") · first aid do/don't · "اسأل نفسك" self-check checklist.
Slide types available: `cover`, `point` (with `num`), `checklist` (title + `items`), `cta`.
Every slide uses Thomas's photo (assets/thomas.jpg) as the background automatically: on the cover he is clearly visible in the lower half with the text on top; on the other slides the photo sits behind a light veil so the text stays crisp. Keep cover text short so it never covers his face.

## Sources (mandatory)
Every fact must come from an approved reference — standard medical textbooks (Davidson's, Harrison's, Oxford Handbook of Clinical Medicine, Kumar & Clark, Nelson, Williams Obstetrics) or official bodies (WHO, NHS, NICE, CDC, ECDC, Mayo Clinic, Egyptian Ministry of Health).
- Before writing a spec, use WebSearch/WebFetch to open the official page for the topic and check EVERY sentence against it. Drop any claim you cannot match to the source; do not mark "warning" items as "emergency" unless the source says so.
- Put the source name in Arabic in the spec as `"source": "..."` (it is printed on the last slide / last scene) and add `📚 المصدر: <name> — <url>` as the line before the disclaimer in the caption.
- If no approved source covers the topic, choose another topic.

## Each run
1. Find the next Cairo date (tomorrow or later) that does not yet have `posts/<date>` (or the old `<date>-am`/`<date>-pm`). Never prepare a date in the past or redo an existing folder.
2. One carousel per day. Its theme and angle must differ from the previous day's post.
3. Pick a NEW topic (and its approved source) not listed in `topics.md`. Rotate content angles that get reach:
   - خرافات طبية مصدقها (myth vs. fact)
   - علامات خطر لازم تروح فيها للطوارئ (red flags)
   - غلطات يومية بتأذي صحتك (everyday mistakes)
   - "إيه اللي بيحصل في جسمك لما…" (body explainer)
   - إسعافات أولية صح وغلط (first aid)
   Pick topics that are common, relatable and shareable in Egypt (صداع، ضغط، سكر، معدة، نوم، أطفال، صيام، حر، إسعافات…).
4. Write the spec in `specs/<date>.json` (Egyptian Arabic, short punchy lines).
   - Carousel: 7–9 slides. Slide 1 = hook (question/shock) using type `cover`; points use type `point` with `num`; last slide type `cta`.
   - Reel (motion graphics): 7–9 scenes, ~30 s total (secs 3–4.5 each). Give EVERY scene an `"icon"` that matches its meaning, chosen from the file names in assets/icons (e.g. flame, droplet, pill, heart, brain, ambulance, thermometer, salad, moon, ban, circle-check). Optional `"kind"`: hook | do | dont | alert | info | cta (colours: do=green, dont/alert=red). Scene 1 hook in the first 3 seconds; last scene asks to send it to someone + follow.
   - On-screen text has no emojis (font can't draw them). Emojis are fine in the caption.
   - Spec also holds `"caption"`: first line = hook with the topic keyword; then save/send/comment CTA; "تابعني عشان معلومة طبية جديدة كل يوم."; the line "⚠️ المحتوى للتوعية فقط ومش بديل عن استشارة الطبيب."; 3–5 Arabic hashtags.
5. Medical safety: only well-established facts. No drug doses, no prescriptions, no brand names, no diagnosis promises, nothing that discourages seeing a doctor. When in doubt, pick another topic.
6. Render:
   - `POST_THEME=<theme> python3 tools/make_carousel.py specs/<date>.json posts/<date>`
   Look at the output (open slide images / extract a few frames with ffmpeg) and fix any overflow or broken text before publishing.
7. Append `- <date> | carousel | <topic>` to `topics.md`, commit, push to `main`.
8. Confirm the raw URLs return 200: `https://raw.githubusercontent.com/tomassaaamir49-byte/thomas-posts/main/posts/<date>/...`
9. Schedule with Metricool `createScheduledPost` at the audience-based time chosen above as ONE post, autoPublish true, providers [instagram, facebook]:
   - carousel: media = all slide JPG raw URLs in order, instagramData type POST, facebookData type POST.
   - If a provider fails (e.g. facebook disconnected), still schedule for the networks that work and report which one failed.
10. Schedule the teaser story (see Stories) as ONE post on both networks. Check the post and the story appear in `getScheduledPosts`. If anything fails, say exactly what failed.
