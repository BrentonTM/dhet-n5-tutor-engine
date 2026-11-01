# Digital Electronics reference alignment map

**Status:** supporting reference only. This map does not define an official DHET syllabus, module order, weighting, or exam scope.

**Book reviewed:** Anil K. Maini, *Digital Electronics: Principles, Devices and Applications* (2007), 741-page user-supplied copy. The full PDF stays in the local project; it is not included in the public app repository. This map contains short, original alignment notes only.

## N4 learner-confirmed working scope

| Working group | Maini chapters | Alignment |
|---|---:|---|
| Number systems and codes | 1-3 | Direct: number bases, codes, and digital arithmetic. |
| Logic gates, Boolean algebra, and K-maps | 4, 6 | Direct. K-maps are included in N4, as confirmed by the learner. |
| Logic-device characteristics | 4-5 | Supporting: logic gates and families. Detailed family comparisons are not established in the current N4 notes. |
| Combinational circuits | 7-8 | Direct: adders, multiplexers/demultiplexers, encoders, and decoders. |
| Flip-flops and latches | 10 | Direct. |
| Counters and shift registers | 11 | Direct. |
| A/D and D/A conversion | 12 | Direct for the paper-evidenced DAC calculations and ramp ADC/digital-voltmeter block diagrams; other converter types/specifications are broader reference. |

**N4 boundary:** Memory Systems (RAM/ROM and memory organization) are outside the learner-confirmed N4 scope, even though the book discusses memory in its broader computer and troubleshooting chapters. Do not use those chapters to add N4 lessons or quizzes.

## Digital Electronics N5 provisional outline

| Current app outline topic | Maini chapters | Alignment status |
|---|---:|---|
| Counters and shift registers | 10-11 | Reference match; N5 placement remains provisional. |
| DAC and ADC converters | 12 | Reference match; N5 placement remains provisional. |
| Memory organization | 15-16 | Possible reference match for the provisional N5 outline only; never import into N4. |
| Microprocessor fundamentals and architecture | 13 | Reference match to the provisional N5 outline. |
| ALUs and bus systems | 13, 15 | Reference match to the provisional N5 outline. |

The standalone Digital Electronics N5 detailed DHET syllabus has not been authenticated. These matches do not verify N5 scope. Chapters on PLDs (9), microcontrollers (14), computer fundamentals (15), and troubleshooting/test equipment (16) remain reference-only unless course notes or an official syllabus confirm them.

## Basis

- N4 groups and boundaries: `curriculum/digital_electronics/topic_map.json` and `app/docs/DIGITAL_ELECTRONICS_N4_PAPER_SCOPE.md`.
- N5 outline: the provisional `DIGI-N5` topics in `app.py`.
- Subject identity and syllabus limitations: `data/dhet_curriculum/source_register/digital_electronics_n4_n5_sources.json`.
- Textbook match: chapter titles in the book's contents pages. No textbook passages are reproduced here.

