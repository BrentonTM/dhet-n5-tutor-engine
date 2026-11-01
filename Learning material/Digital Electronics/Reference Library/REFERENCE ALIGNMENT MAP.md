# Digital Electronics reference alignment map

**Status:** supporting study reference only; not an official DHET syllabus, module order, weighting, or exam blueprint. The N5 module headings below were transcribed from the learner's photos of the school textbook contents pages.

**Book reviewed:** Anil K. Maini, *Digital Electronics: Principles, Devices and Applications* (2007), user-supplied copy. The full book stays in the local project and is not included in the public app repository. This map uses original summaries and short topic labels, not textbook passages.

## N4 learner-confirmed working scope

| Working group | Maini chapters | Alignment |
|---|---:|---|
| Number systems and codes | 1-3 | Number bases, codes, and digital arithmetic. |
| Logic gates, Boolean algebra, and K-maps | 4, 6 | K-maps are included in N4, as confirmed by the learner. |
| Logic-device characteristics | 4-5 | Gate and logic-family reference; detailed family comparisons are not established in current N4 notes. |
| Combinational circuits | 7-8 | Adders, multiplexers/demultiplexers, encoders, and decoders. |
| Flip-flops and latches | 10 | Direct reference match. |
| Counters and shift registers | 11 | Direct reference match. |
| A/D and D/A conversion | 12 | Paper-evidenced DAC calculations and ramp ADC/digital-voltmeter block diagrams; other types/specifications are broader reference. |

**N4 boundary:** Memory Systems (RAM/ROM and memory organization) are outside the learner-confirmed N4 scope, even though the reference book covers memory elsewhere. Do not use those chapters to add N4 lessons or quizzes.

## N5 school-textbook topic map

The standalone Digital Electronics N5 detailed DHET syllabus has not been authenticated. These are the modules visible in the learner's school textbook contents photos. Maini chapter references are comparison pointers based on chapter headings; they do not establish official alignment or expand the photographed course scope.

| Module | Visible textbook topics | Maini reference chapters |
|---|---|---:|
| 1. Digital-to-analog and analog-to-digital converters | Binary-weighted, BCD, and ladder DACs; ADCs including staircase-ramp, dual-slope, and successive-approximation types; voltage-to-frequency conversion; sample-and-hold; recovery time, hysteresis, offset voltage, response time; practical ADC activity. | 12 |
| 2. Counter design | Design rules; Mod-6 and 3-bit Gray counters; binary counter. The photographed contents show only selected subsection numbers. | 10-11 |
| 3. Encoder-decoder realisation | Decoders; BCD-to-7-segment decoder/driver in common-anode configuration; alphanumeric-code decoding. | 2, 8 |
| 4. Parity-error-ASCII-code | ASCII and serial transmission; CRT and ASCII characters; data transmission and error detection. | 2, 13 |
| 5. K-maps and code converters | Plotting minterm/SOP and maxterm/POS expressions; grouping methods. | 2, 6 |
| 6. Code converters | Binary-to-Gray and Gray-to-binary conversion; common-anode BCD-to-7-segment decoder/driver realisation. | 2, 8 |
| 7. Number systems | Number systems. | 1 |
| 8. Addition and multiplication | Binary addition (the visible subsection); module heading also names multiplication. | 3, 7 |
| 9. Division and 2's complement | Division and two's-complement representation/operations. | 3 |
| 10. Party-line circuits | TTL logic family, open-collector and Schottky TTL, unused TTL inputs, current sinking/sourcing and current sources, tri-state devices, MOS technology and MOS integrated circuits. | 5, 8 |
| 11. Computer architecture | Memory systems, PROM, EPROM, and RAM. | 13, 15 |
| 12. Boolean algebra | Exclusive-OR and exclusive-NOR functions. | 4, 6 |
| 13. Contact bounce elimination | Contact bounce; non-impact printers; magnetic tape and data organisation; drum and disc memories; card-punch station; UART, USART, and RS-232 receiver. | 10, 13, 15 |
| 14. Input/output devices | CMOS 8-bit ADC; serial and parallel transmission; microcomputer address decoding and tri-state interfaces; peripherals; microcomputer/memory/I/O; floppy disks, hard disks, magnetic-core memory, non-volatile RAM, PROM/ROM/RAM, static RAM, CMOS and equivalent symbols. | 12-15 |

**Memory boundary:** Module 11 explicitly includes memory systems in this school-textbook N5 list. This does not change the confirmed N4 boundary: Memory Systems stay excluded from N4 and included only in the N5 study map.

## Transcription notes

- The Module 1 contents photo appears to print “R/2 ladder”; verify the textbook wording before normalising this to the commonly written R-2R ladder.
- The Module 2 photo shows selected entries (including 2.1, 2.2, 2.3 and 2.10), not a complete subsection list. Do not infer the missing entries.
- Preserve the older topics listed under Modules 13 and 14 as part of the learner's supplied course reference; do not silently omit them because the technologies are dated.

## Basis

- N4 scope and boundaries: `curriculum/digital_electronics/topic_map.json` and `app/docs/DIGITAL_ELECTRONICS_N4_PAPER_SCOPE.md`.
- N5 module titles and topic labels: learner-supplied school textbook contents photos.
- Maini matches: chapter headings in the supplied book's contents pages; no textbook passages are reproduced.
- The app's N5 selector follows this school-textbook list. Official DHET sequence and weighting remain unverified.
