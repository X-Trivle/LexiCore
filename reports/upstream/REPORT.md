# LexiCore — Validation & Oxford Comparison Report

Generated: 2026-09-14T17:50:40.615611Z

## Word volume actually analyzed and verified

| Source | Words | Docs | Files |
|---|---:|---:|---:|
| fineweb | 7,545,397,544 | 14,853,888 | 115 |
| fwedu | 1,509,381,045 | 2,020,431 | 18 |
| wiki | 2,172,583,977 | 5,428,305 | 110 |
| subs | 1,103,261,872 | 198,800,294 | 1 |
| cc2026 | 1,301,987,532 | 1,549,435 | 128 |

**TOTAL: 13,632,611,970 words** (floor 8,000,000,000)

## Validation

- Exactly 5000 unique headwords: True
- Every headword in a validity dictionary: True
- Level counts: {'A1': 1000, 'A2': 1000, 'B1': 1000, 'B2': 1000, 'C1': 1000}
- Direct-profile vs model labels: {'cefrj-v1.5': 3898, 'model': 437, 'octanove-c1c2-v1.0': 665}
- Mean CEFR confidence: 0.9205
- Present in all 5 sources: 99.06%; in >=4: 99.98%
- Mean 2022+ recency share: nan; 2025-2026 share: nan

## Held-out coverage (independent documents)

| Source | Coverage |
|---|---:|
| fineweb | 0.7560 |
| fwedu | 0.7388 |
| wiki | 0.6587 |
| subs | 0.8290 |
| cc2026 | 0.5469 |
| overall | 0.7251 |

## External comparison vs Oxford 5000 (reference only)

- Overlap: 3526 words (70.52% of LexiCore); Jaccard 0.5508
- LexiCore-only: 1474; Oxford-only: 1402
- Exact CEFR agreement on overlap: 0.466; within +/-1: 0.8659; quadratic-weighted kappa: 0.7124
- Mean 2025-26 share — LexiCore-only: None vs Oxford-only: None
- Mean wordfreq(2021) Zipf — LexiCore-only: 3.734 vs Oxford-only: 4.072

### Notable modern additions (LexiCore, ranked by 2025-26 evidence)
abandoned, abdominal, aboard, abound, abruptly, absorption, abstraction, acceleration, accidental, accord, accustomed, acidic, acoustic, acoustics, acutely, adaptive, addict, addicted, adjoining, adjustable, admiration, adopted, adrenaline, advantageous, adventurous, adversary, advertiser, advisor, advisory, aerosol, aesthetically, affirm, aggregate, agreeable, airplane, aisle, algorithm, alleviate, altar, alternate, altitude, am, amino, amongst, ample, amplification, amplitude, amusement, an, analytic

### Oxford-only examples
accounting, angrily, cleaning, feeding, actress, blog, cannot, career, email, euro, fifth, fourth, geography, goodbye, grandparent, guess, hey, kilometre, laugh, menu, metre, nobody, oh, policeman, somebody, sweater, thirsty, waiter, yeah, advertise, advertisement, affect, ah, anyway, app, architect, army, asleep, awful, based, behave, bin, businessman, carpet, chat, cigarette, classical, climate, comedy, comment, connect, connected, cooker, crazy, cupboard, curly, definitely, detective, digital, disease