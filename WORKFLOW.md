# Daily Instagram workflow — @thomassamir_medical_student

Account owner: توماس سمير فوزي, طالب طب بشري (medical student — NOT a doctor).
Goal: grow followers, reach and engagement with Egyptian-Arabic medical awareness for the general public.
Metricool brand (blogId): 7301767. Networks: instagram AND facebook (page "توماس سمير طالب طب بشري"). Timezone: Africa/Cairo.
TWO posts per day: morning slot `am` = CAROUSEL at 10:00, evening slot `pm` = REEL at 18:00.
Folders/specs are named `<date>-am` and `<date>-pm` (e.g. posts/2026-10-21-am, specs/2026-10-21-pm.json).

Reels get original synthesized music automatically (tools/make_music.py); never add copyrighted songs.

## Sources (mandatory)
Every fact must come from an approved reference — standard medical textbooks (Davidson's, Harrison's, Oxford Handbook of Clinical Medicine, Kumar & Clark, Nelson, Williams Obstetrics) or official bodies (WHO, NHS, NICE, CDC, ECDC, Mayo Clinic, Egyptian Ministry of Health).
- Before writing a spec, use WebSearch/WebFetch to open the official page for the topic and check EVERY sentence against it. Drop any claim you cannot match to the source; do not mark "warning" items as "emergency" unless the source says so.
- Put the source name in Arabic in the spec as `"source": "..."` (it is printed on the last slide / last scene) and add `📚 المصدر: <name> — <url>` as the line before the disclaimer in the caption.
- If no approved source covers the topic, choose another topic.

## Each run
1. Find the next Cairo date (tomorrow or later) that does not yet have BOTH `posts/<date>-am` and `posts/<date>-pm`.
   Prepare whichever of the two slots is missing for that date (normally both). Never prepare a date in the past or redo an existing folder.
2. Slot `am` is always a carousel; slot `pm` is always a reel. The two topics of the same day must be different.
3. For each slot pick a NEW topic (and its approved source) not listed in `topics.md`. Rotate content angles that get reach:
   - خرافات طبية مصدقها (myth vs. fact)
   - علامات خطر لازم تروح فيها للطوارئ (red flags)
   - غلطات يومية بتأذي صحتك (everyday mistakes)
   - "إيه اللي بيحصل في جسمك لما…" (body explainer)
   - إسعافات أولية صح وغلط (first aid)
   Pick topics that are common, relatable and shareable in Egypt (صداع، ضغط، سكر، معدة، نوم، أطفال، صيام، حر، إسعافات…).
4. Write the spec in `specs/<date>-<slot>.json` (Egyptian Arabic, short punchy lines).
   - Carousel: 7–9 slides. Slide 1 = hook (question/shock) using type `cover`; points use type `point` with `num`; last slide type `cta`.
   - Reel: 7–9 scenes, ~30 s total (secs 3–4.5 each). Scene 1 hook in the first 3 seconds; last scene asks to send it to someone + follow.
   - On-screen text has no emojis (font can't draw them). Emojis are fine in the caption.
   - Spec also holds `"caption"`: first line = hook with the topic keyword; then save/send/comment CTA; "تابعني عشان معلومة طبية جديدة كل يوم."; the line "⚠️ المحتوى للتوعية فقط ومش بديل عن استشارة الطبيب."; 3–5 Arabic hashtags.
5. Medical safety: only well-established facts. No drug doses, no prescriptions, no brand names, no diagnosis promises, nothing that discourages seeing a doctor. When in doubt, pick another topic.
6. Render:
   - carousel: `python3 tools/make_carousel.py specs/<date>-am.json posts/<date>-am`
   - reel: `python3 tools/make_reel.py specs/<date>-pm.json posts/<date>-pm`
   Look at the output (open slide images / extract a few frames with ffmpeg) and fix any overflow or broken text before publishing.
7. Append `- <date>-<slot> | carousel/reel | <topic>` to `topics.md`, commit, push to `main`.
8. Confirm the raw URLs return 200: `https://raw.githubusercontent.com/tomassaaamir49-byte/thomas-posts/main/posts/<date>-<slot>/...`
9. Schedule with Metricool `createScheduledPost` for `<date>T10:00:00+03:00` (am) or `<date>T18:00:00+03:00` (pm), autoPublish true, providers [instagram, facebook]:
   - carousel: media = all slide JPG raw URLs in order, instagramData type POST, facebookData type POST.
   - reel: media = reel.mp4 raw URL, videoThumbnailUrl = cover.jpg raw URL, instagramData type REEL + showReelOnFeed true, facebookData type REEL.
   - Reels only — try Instagram's licensed music library first: add instagramData.audioConfiguration
     {"audioId": "<search term for a calm/emotional or trending instrumental>", "audioVolume": 80, "videoVolume": 0}.
     If it is rejected with a list of candidates, retry once with the numeric id of a fitting instrumental candidate.
     If it is rejected with a 403/catalog-unavailable error, schedule without audioConfiguration (the video already carries our own original music).
   - If a provider fails (e.g. facebook disconnected), still schedule for the networks that work and report which one failed.
10. Check it appears in `getScheduledPosts`. If anything fails, say exactly what failed.
