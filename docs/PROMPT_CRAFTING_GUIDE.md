# Suno Prompt Crafting Guide

**How to write prompts that generate accurate results while maintaining semantic consistency for song matching**

---

## Quick Start: Ready-to-Use Templates

**Need prompts fast?** See **[PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md)** for complete 13-prompt track sets:
- **Template 1:** Neon Night / Rain / Coding Focus
- **Template 2:** Pre-Dawn / Sunrise / Calm Focus
- **Template 3:** Retro Tech / Analog Neutral

All templates are pre-validated and ready to paste into Notion. Read below to understand the rules and customize your own.

---

## The Problem

Prompts that are too technical (e.g., "sustained pad in mid-low register, slow attack and long release") work for Suno but create library fragmentation:
- Songs won't match across tracks with similar themes
- Semantic similarity drops below 60%
- Reduced song reuse efficiency

**Solution:** Use evocative, consistent vocabulary that's descriptive enough for Suno but standardized enough for semantic matching.

---

## Prompt Structure Template

**Use this exact format for every prompt:**

```
[texture/timbre], [mood/imagery], [harmonic element], [motion quality] — vaporwave synthwave lofi
```

**Example:**
```
soft ambient pads, distant city hush, analog warmth, minimal motion — vaporwave synthwave lofi
```

**Components:**
1. **Texture/Timbre** - What the sound feels like
2. **Mood/Imagery** - Evocative description
3. **Harmonic Element** - How chords/tones move
4. **Motion Quality** - Energy level/pace
5. **Anchor Phrase** - Always the same genre tags

---

## Approved Vocabulary

### Texture/Timbre (Choose 1-2)

**✅ Use These:**
- soft ambient pads
- warm analog pads
- airy vaporwave pads
- layered analog warmth
- gentle synth tones
- vintage synth atmosphere
- soft complex chords

**❌ Never Use:**
- "sustained pad in mid-low register"
- "slow attack and long release"
- "mid-frequency range"
- Any technical production terms

---

### Mood/Imagery (Choose 1-2)

**✅ Use These:**

**Morning/Sunrise:**
- morning light emerging
- gentle sunrise warmth
- pre-dawn stillness
- soft morning calm
- early light awakening

**Night/Midnight:**
- deep night calm
- gentle nocturnal energy
- quiet midnight drift
- night dissolving
- distant city hush

**Rain:**
- soft rain texture
- gentle rain ambience
- rain-washed calm

**CRT/Desk:**
- CRT-like drone tones
- analog desk warmth
- retro terminal hum
- vintage equipment glow

**General:**
- gentle drift
- quiet stillness
- calm atmosphere
- spacious resonance

**❌ Never Use:**
- "faint static noise bed" (too clinical)
- "no rhythmic elements" (negative phrasing)
- "beatless structure" (negative phrasing)
- Functional descriptions without imagery

---

### Harmonic Element (Choose 1)

**✅ Use These:**
- slow chord progression
- subtle tonal shifts
- gentle harmonic movement
- warm resonance
- slow harmonic drift
- smooth harmonic flow
- subtle harmonic evolution

**❌ Never Use:**
- "chord cycling every 8 bars"
- "extended complex chords"
- "minimal harmonic change"
- Specific musical theory terms

---

### Motion Quality (Always Include)

**✅ Use These:**
- minimal motion
- gentle drift
- slow evolution
- calm stillness
- quiet energy
- soft flow
- relaxed motion
- gentle pulse

**❌ Never Use:**
- "zero rhythmic drive"
- "no percussion"
- "extremely low event density"
- "beatless"
- Any negative phrasing

---

## Percussion Guidance

**Default approach:** Don't mention percussion at all. Suno will add appropriate amounts.

**For less percussion:**
```
✅ minimal rhythmic elements, gentle pulse
✅ soft ambient focus, calm stillness
❌ no drums, zero percussion, beatless
```

**For more percussion:**
```
✅ soft steady beat, muted drums, gentle rhythm
✅ gentle lofi pulse, warm analog bass
❌ drum machine, crisp percussion (too specific)
```

**Rule:** Use positive descriptors (gentle, soft, muted) instead of negative ones (no, zero, without).

---

## BPM Ranges

Include BPM in **phase headers only**, not in individual prompts.

**Standard Ranges:**
- **Phase 1 (Ambient Entry):** 50-58 BPM
- **Phase 2 (Light Rhythmic Lift):** 56-64 BPM
- **Phase 3 (Sustained Focus):** 64-72 BPM
- **Phase 4 (Wind Down):** 56-64 BPM

**Example Phase Header:**
```
### Phase 1 — Quiet Night Fade (BPM 50-58)
```

---

## Anchor Phrase (Sacred Rule)

**Every prompt must end with:**
```
— vaporwave synthwave lofi
```

**Never change this to:**
- `— sunrise calm focus`
- `— neon rain focus flow`
- `— lofi study beats`
- Any other variation

**Why:** Consistent anchor phrases ensure semantic matching across all tracks. A different anchor phrase can drop similarity scores by 10-15%.

---

## Forbidden Phrases

**Never use these technical terms:**

❌ "slow attack and long release"
❌ "mid-low register"
❌ "chord cycling every 8 bars"
❌ "wide stereo field"
❌ "zero rhythmic drive"
❌ "extremely low event density"
❌ "no percussion"
❌ "beatless structure"
❌ "faint static noise bed"
❌ "vocal pads in upper register"

**Why these fail:**
1. They're production/mixing terms, not musical descriptions
2. They confuse semantic matching (create low similarity scores)
3. They sound clinical rather than evocative
4. They fragment your song library

---

## Pattern Library

Use these tested, high-similarity combinations:

### Ambient/Pad-Focused Patterns

```
soft ambient pads, [imagery], gentle harmonic movement, minimal motion — vaporwave synthwave lofi

warm analog pads, [imagery], slow tonal shifts, quiet stillness — vaporwave synthwave lofi

airy vaporwave pads, [imagery], subtle resonance, calm drift — vaporwave synthwave lofi

layered analog warmth, [imagery], slow harmonic evolution, gentle drift — vaporwave synthwave lofi
```

### Light Rhythm Patterns

```
gentle lofi pulse, [imagery], warm analog bass, soft steady flow — vaporwave synthwave lofi

muted rhythmic elements, [imagery], calm progression, gentle energy — vaporwave synthwave lofi

soft steady beat, [imagery], smooth harmonic drift, relaxed motion — vaporwave synthwave lofi
```

### Textural/Atmospheric Patterns

```
vintage synth atmosphere, [imagery], gentle modulation, quiet depth — vaporwave synthwave lofi

soft complex chords, [imagery], spacious resonance, minimal motion — vaporwave synthwave lofi

layered analog tones, [imagery], subtle tape saturation, slow evolution — vaporwave synthwave lofi
```

**[imagery]** = Replace with your theme-specific mood descriptor:
- morning light emerging
- deep night calm
- distant city hush
- soft rain texture
- etc.

---

## Good vs. Bad Examples

### ✅ Good Prompt Set (High Semantic Similarity ~75%)

```
1. soft ambient pads, distant city hush, analog warmth, minimal motion — vaporwave synthwave lofi

2. gentle vaporwave wash, morning light emerging, slow harmonic drift, calm stillness — vaporwave synthwave lofi

3. warm analog layers, quiet dawn energy, subtle resonance, gentle evolution — vaporwave synthwave lofi
```

**Why it works:**
- Consistent vocabulary from approved library
- Similar structure across all three
- Variation comes from imagery only
- All use same anchor phrase

---

### ❌ Bad Prompt Set (Low Semantic Similarity ~45%)

```
1. soft ambient pads, distant city hush, analog warmth, minimal motion — vaporwave synthwave lofi

2. sustained pad in mid-low register, slow attack and long release, no percussion, minimal harmonic change — sunrise calm focus

3. airy vaporwave pad stack with slow chord cycling every 8 bars, faint static noise bed, no rhythmic elements — sunrise calm focus
```

**Why it fails:**
- Technical production terms (attack, release, register)
- Different anchor phrases (breaks consistency)
- Negative phrasing (no percussion, no rhythmic elements)
- Clinical descriptions instead of evocative imagery

---

## Theme-Specific Imagery

### Morning/Sunrise Tracks

**✅ Good:**
```
warm analog pads, morning light emerging, slow harmonic drift, minimal motion — vaporwave synthwave lofi

gentle vaporwave wash, pre-dawn stillness, subtle tonal shifts, calm awakening — vaporwave synthwave lofi

soft ambient layers, sunrise warmth, gentle resonance, quiet optimism — vaporwave synthwave lofi
```

**❌ Avoid:**
- Changing anchor to "sunrise calm focus"
- Overly bright imagery ("brilliant sunshine")
- Daytime references ("midday energy")

---

### Night/Rain Tracks

**✅ Good:**
```
soft ambient pads, deep night calm, analog warmth, minimal motion — vaporwave synthwave lofi

gentle vaporwave wash, soft rain texture, slow harmonic drift, quiet stillness — vaporwave synthwave lofi

warm analog layers, gentle nocturnal energy, subtle resonance, calm drift — vaporwave synthwave lofi
```

**❌ Avoid:**
- Changing anchor to "neon rain focus flow"
- Heavy rain imagery ("torrential downpour")
- Late-night party vibes

---

### CRT Desk Tracks

**✅ Good:**
```
soft ambient pads, CRT-like drone tones, analog warmth, minimal motion — vaporwave synthwave lofi

gentle vaporwave wash, retro terminal hum, slow harmonic drift, quiet focus — vaporwave synthwave lofi

warm analog layers, vintage equipment glow, subtle resonance, calm productivity — vaporwave synthwave lofi
```

**❌ Avoid:**
- Technical computer terms ("CPU fan hum")
- Modern tech references ("LED backlight")
- Office/work imagery ("keyboard clicking")

---

## Complexity Without Divergence

### How to Be Descriptive Without Being Technical

**❌ Too Technical (Low Similarity):**
```
sustained warm analog pad in mid–low register, slow attack and long release,
no percussion, minimal harmonic change — sunrise calm focus
```

**✅ Evocative & Consistent (High Similarity):**
```
warm analog pads, gentle morning calm, slow harmonic movement, minimal motion — vaporwave synthwave lofi
```

**Both describe similar music, but the second:**
- Uses approved vocabulary
- Maintains anchor phrase consistency
- Is evocative rather than technical
- Will match better with other tracks

---

## Variation Within a Track

You need variety within a single track, but not so much that it breaks semantic consistency.

### ✅ Good Variation (Within Same Track)

```
Phase 1:
- soft ambient pads, pre-dawn stillness, gentle warmth, minimal motion — vaporwave synthwave lofi
- airy vaporwave wash, night dissolving, slow harmonic drift, calm stillness — vaporwave synthwave lofi
- warm analog layers, quiet nocturnal energy, subtle resonance, gentle evolution — vaporwave synthwave lofi

Phase 2:
- gentle lofi pulse, morning light emerging, warm analog bass, soft flow — vaporwave synthwave lofi
- muted rhythmic elements, sunrise calm, smooth progression, gentle energy — vaporwave synthwave lofi
- soft steady beat, distant city awakening, harmonic drift, relaxed motion — vaporwave synthwave lofi
```

**Why this works:**
- All use approved vocabulary
- Variation comes from imagery (pre-dawn → sunrise)
- Structure remains consistent
- Progression feels natural (ambient → light rhythm)

---

### ✅ Consistency Across Different Tracks

**Track A (Morning Theme):**
```
warm analog pads, morning light emerging, slow harmonic drift, minimal motion — vaporwave synthwave lofi
```

**Track B (Night Theme):**
```
warm analog pads, deep night calm, slow harmonic drift, minimal motion — vaporwave synthwave lofi
```

**Semantic Similarity:** ~75-80% (excellent for song reuse)

**What changed:** Only the imagery (morning vs night)
**What stayed the same:** Texture, harmonic element, motion, anchor phrase

This means songs generated for Track A could potentially work for Track B and vice versa.

---

## Testing Your Prompts

### Before Finalizing a Track

Run through this checklist:

- [ ] All prompts end with `— vaporwave synthwave lofi`
- [ ] No production terms (attack, release, register, stereo, etc.)
- [ ] Vocabulary matches approved pattern library
- [ ] Structure follows 4-part format [texture], [imagery], [harmonic], [motion]
- [ ] Theme-specific imagery is evocative, not clinical
- [ ] BPM ranges in phase headers only
- [ ] Percussion guidance is positive (soft/muted) not negative (no/zero)
- [ ] Prompts would semantically match similar themes from other tracks

### Quick Similarity Test

Pick any two prompts from your track and ask:
- Do they use similar vocabulary?
- Is the structure the same?
- Is only the imagery changing?
- Do they both end with the same anchor phrase?

**If yes to all four:** Good consistency ✅
**If no to any:** Rewrite for consistency ❌

---

## Real-World Example: Track 24 vs Track 1000

### Track 24 (Good Consistency)

```
1. soft ambient pads, distant city hush, analog warmth, minimal motion — vaporwave synthwave lofi
2. slow vaporwave chord wash, subtle tape flutter, deep space between notes, night dissolving — vaporwave synthwave lofi
3. CRT-like drone tones, gentle modulation, calm nocturnal energy — vaporwave synthwave lofi
```

**Similarity within track:** ~70-75%

---

### Track 1000 Original (Poor Consistency)

```
1. sustained warm analog pad in mid–low register, slow attack and long release, no percussion, minimal harmonic change — sunrise calm focus
2. airy vaporwave pad stack with slow chord cycling every 8 bars, faint static noise bed, no rhythmic elements — sunrise calm focus
3. extended complex chords voiced softly, slow harmonic transitions, wide stereo field, zero rhythmic drive — sunrise calm focus
```

**Similarity with Track 24:** ~45% (too low for song reuse)

---

### Track 1000 Rewritten (Good Consistency)

```
1. warm analog pads, gentle morning calm, slow harmonic movement, minimal motion — vaporwave synthwave lofi
2. airy vaporwave pads, subtle static texture, slow chord progression, ambient stillness — vaporwave synthwave lofi
3. soft complex chords, slow harmonic shifts, spacious atmosphere, gentle drift — vaporwave synthwave lofi
```

**Similarity with Track 24:** ~70-75% (excellent for song reuse)

**What changed:**
- Removed technical terms
- Standardized anchor phrase
- Used approved vocabulary
- Maintained evocative descriptions

**Result:** Track 1000 can now share songs with Track 24!

---

## Summary Rules

### The 7 Sacred Rules

1. **Always use the 4-part structure:** [texture], [imagery], [harmonic], [motion]
2. **Always end with:** `— vaporwave synthwave lofi`
3. **Stick to approved vocabulary** from the pattern library
4. **Avoid production/mixing terms** completely
5. **Use evocative imagery** specific to your theme
6. **Test prompt sets** for consistency before finalizing
7. **When in doubt:** Choose evocative over technical

---

### Quick Decision Tree

**When writing a prompt, ask:**

1. Does it follow the 4-part structure? → If no, restructure
2. Does it end with `— vaporwave synthwave lofi`? → If no, fix anchor
3. Does it use approved vocabulary? → If no, replace technical terms
4. Is imagery evocative, not clinical? → If no, rewrite imagery
5. Would it match similar prompts from other tracks? → If no, simplify

---

## Benefits of Consistent Prompts

**With this system:**
- ✅ Semantic similarity stays above 70%
- ✅ Songs can be reused across tracks with similar themes
- ✅ Library grows cohesively instead of fragmenting
- ✅ Suno still gets enough detail to generate accurate results
- ✅ Query command finds better matches
- ✅ Reduced need to generate new songs (60-70% reuse rate)

**Without this system:**
- ❌ Similarity drops to 40-50%
- ❌ Each track needs all new songs
- ❌ Library fragments into incompatible clusters
- ❌ Production time increases
- ❌ Query command finds poor matches

---

## Appendix: Full Pattern Templates

### Template 1: Ambient Focus
```
soft ambient pads, [theme imagery], gentle harmonic movement, minimal motion — vaporwave synthwave lofi
```

### Template 2: Light Rhythm
```
gentle lofi pulse, [theme imagery], warm analog bass, soft steady flow — vaporwave synthwave lofi
```

### Template 3: Atmospheric
```
layered analog warmth, [theme imagery], subtle resonance, calm drift — vaporwave synthwave lofi
```

### Template 4: Textural
```
vintage synth atmosphere, [theme imagery], gentle modulation, quiet depth — vaporwave synthwave lofi
```

### Template 5: Complex Harmony
```
soft complex chords, [theme imagery], spacious resonance, minimal motion — vaporwave synthwave lofi
```

**Replace [theme imagery] with:**
- **Morning:** morning light emerging, pre-dawn stillness, gentle sunrise warmth
- **Night:** deep night calm, quiet nocturnal energy, distant city hush
- **Rain:** soft rain texture, gentle rain ambience, rain-washed calm
- **CRT:** retro terminal hum, CRT-like drone tones, analog desk warmth

---

**End of Guide**

For questions or examples, reference the full analysis in `AGENT_CONTEXT.md` under "Workflows & Use Cases" → "Duration Examples"
