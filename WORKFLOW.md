# Daily Instagram workflow — @thomassamir_medical_student

Account owner: توماس سمير فوزي, طالب طب بشري (medical student — NOT a doctor).
Goal: grow followers, reach and engagement with Egyptian-Arabic medical awareness for the general public.
Metricool brand (blogId): 7301767. Networks: instagram AND facebook (page "توماس سمير طالب طب بشري"). Timezone: Africa/Cairo.
TWO CAROUSELS per day (user's choice, no reels): morning slot `am` at 10:00 and evening slot `pm` at 18:00 — both are carousels.
Folders/specs are named `<date>-am` and `<date>-pm` (e.g. posts/2026-10-21-am, specs/2026-10-21-pm.json).


## Freshness — every post must feel different from the one before it
- THEME: render each post with a different colour theme than the previous post: `POST_THEME=<ocean|emerald|violet|sunset|rose|teal> python3 tools/...`. Record the theme in topics.md and never reuse the previous post's theme.
- ANGLE: never use the same content angle (myth/red-flags/mistakes/body-explainer/first-aid/quiz "صح ولا غلط"/numbers & facts) twice in a row; vary the hook style (question, shocking fact, "غلطة بيعملها ٩٠٪", challenge).
- TOPIC BANK: start from `topics_bank.md` (researched list of what Egyptians search for + seasonal topics + hook formulas). Prefer the 'Seasonal NOW' section while in season, mix with evergreen/Egypt-specific ones, and pick topics that speak to a specific person (أم، طالب، مريض سكر…) because those get shared. Once a week (Fridays) refresh the bank with a quick search and commit it.
- WHAT THE AUDIENCE NEEDS NOW: before choosing topics, (1) WebSearch what health topics are in the news / trending in Egypt this week and what season it is (heat, flu season, exams, Ramadan, school start, outbreaks, viral myths) and pick topics people are searching for right now; (2) check Metricool analytics for the account's recent posts (getAnalyticsDataByMetrics — reach, saves, shares, plays) and lean toward the formats/topics that performed best.
- MUSIC: Instagram's publishing API only allows music on reels, not carousels (Metricool returns AUDIO_NOT_APPLICABLE). Do NOT send audioConfiguration on carousels. In the final message, suggest one fitting, currently popular song name per post that the user can add by hand in the Instagram app if they want.

## Stories — a teaser story for EVERY carousel (cover only, not the whole post)
- After rendering a carousel, make its story: `POST_THEME=<same theme> python3 tools/make_story.py posts/<date>-<slot>/slide_01.jpg posts/<date>-<slot>/story.jpg "<teaser>"`.
  The teaser is ONE short Egyptian-Arabic curiosity line that makes people open the profile without giving the answer, different every time (e.g. "الخرافة رقم ٤ أغلبنا مصدقها", "٦ علامات لازم كل أم وأب يعرفوها", "الغلطة رقم ٢ بنعملها كل يوم"). The image already says "بوست جديد", points at the name ("اضغط على اسمي") and says "البوست كامل على البروفايل".
- Commit/push story.jpg with the post, then schedule it 15 minutes after the post (10:15 / 18:15) with `createScheduledPost`, providers [instagram, facebook], instagramData type STORY, facebookData type STORY, NO text, autoPublish true, media = story.jpg raw URL.
- If Facebook refuses the story, still schedule the Instagram one and report it.

## Sources (mandatory)
Every fact must come from an approved reference — standard medical textbooks (Davidson's, Harrison's, Oxford Handbook of Clinical Medicine, Kumar & Clark, Nelson, Williams Obstetrics) or official bodies (WHO, NHS, NICE, CDC, ECDC, Mayo Clinic, Egyptian Ministry of Health).
- Before writing a spec, use WebSearch/WebFetch to open the official page for the topic and check EVERY sentence against it. Drop any claim you cannot match to the source; do not mark "warning" items as "emergency" unless the source says so.
- Put the source name in Arabic in the spec as `"source": "..."` (it is printed on the last slide / last scene) and add `📚 المصدر: <name> — <url>` as the line before the disclaimer in the caption.
- If no approved source covers the topic, choose another topic.

## Each run
1. Find the next Cairo date (tomorrow or later) that does not yet have BOTH `posts/<date>-am` and `posts/<date>-pm`.
   Prepare whichever of the two slots is missing for that date (normally both). Never prepare a date in the past or redo an existing folder.
2. Both slots are carousels. The two topics and the two colour themes of the same day must be different, and the evening one must use a different angle than the morning one.
3. For each slot pick a NEW topic (and its approved source) not listed in `topics.md`. Rotate content angles that get reach:
   - خرافات طبية مصدقها (myth vs. fact)
   - علامات خطر لازم تروح فيها للطوارئ (red flags)
   - غلطات يومية بتأذي صحتك (everyday mistakes)
   - "إيه اللي بيحصل في جسمك لما…" (body explainer)
   - إسعافات أولية صح وغلط (first aid)
   Pick topics that are common, relatable and shareable in Egypt (صداع، ضغط، سكر، معدة، نوم، أطفال، صيام، حر، إسعافات…).
4. Write the spec in `specs/<date>-<slot>.json` (Egyptian Arabic, short punchy lines).
   - Carousel: 7–9 slides. Slide 1 = hook (question/shock) using type `cover`; points use type `point` with `num`; last slide type `cta`.
   - Reel (motion graphics): 7–9 scenes, ~30 s total (secs 3–4.5 each). Give EVERY scene an `"icon"` that matches its meaning, chosen from the file names in assets/icons (e.g. flame, droplet, pill, heart, brain, ambulance, thermometer, salad, moon, ban, circle-check). Optional `"kind"`: hook | do | dont | alert | info | cta (colours: do=green, dont/alert=red). Scene 1 hook in the first 3 seconds; last scene asks to send it to someone + follow.
   - On-screen text has no emojis (font can't draw them). Emojis are fine in the caption.
   - Spec also holds `"caption"`: first line = hook with the topic keyword; then save/send/comment CTA; "تابعني عشان معلومة طبية جديدة كل يوم."; the line "⚠️ المحتوى للتوعية فقط ومش بديل عن استشارة الطبيب."; 3–5 Arabic hashtags.
5. Medical safety: only well-established facts. No drug doses, no prescriptions, no brand names, no diagnosis promises, nothing that discourages seeing a doctor. When in doubt, pick another topic.
6. Render:
   - `POST_THEME=<theme> python3 tools/make_carousel.py specs/<date>-<slot>.json posts/<date>-<slot>` (once per slot)
   Look at the output (open slide images / extract a few frames with ffmpeg) and fix any overflow or broken text before publishing.
7. Append `- <date>-<slot> | carousel/reel | <topic>` to `topics.md`, commit, push to `main`.
8. Confirm the raw URLs return 200: `https://raw.githubusercontent.com/tomassaaamir49-byte/thomas-posts/main/posts/<date>-<slot>/...`
9. Schedule with Metricool `createScheduledPost` for `<date>T10:00:00+03:00` (am) or `<date>T18:00:00+03:00` (pm), autoPublish true, providers [instagram, facebook]:
   - carousel: media = all slide JPG raw URLs in order, instagramData type POST, facebookData type POST.
   - If a provider fails (e.g. facebook disconnected), still schedule for the networks that work and report which one failed.
10. Schedule each post's teaser story (see Stories). Check the 2 posts and 2 stories appear in `getScheduledPosts`. If anything fails, say exactly what failed.
