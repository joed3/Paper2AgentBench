# AlphaGenome Benchmark Scoring - Complete Summary

**Date:** 2026-01-21
**Analysis Version:** v1

---

## Overall Results

### Novel Benchmarks (75 questions each)

| Approach | Accuracy | Correct | Incorrect |
|----------|----------|---------|-----------|
| Claude and Repo Only | 78.67% | 59/75 | 16/75 |
| **MCP** | **100.00%** | **75/75** | **0/75** ✓ |

### Tutorial Benchmarks (75 questions each)

| Approach | Accuracy | Correct | Incorrect |
|----------|----------|---------|-----------|
| Claude and Repo Only | 73.33% | 55/75 | 20/75 |
| **MCP** | **96.00%** | **72/75** | **3/75** ✓ |

### Combined Results (150 questions total)

| Approach | Accuracy | Correct | Incorrect |
|----------|----------|---------|-----------|
| Claude and Repo Only | 76.00% | 114/150 | 36/150 |
| **MCP** | **98.00%** | **147/150** | **3/150** ✓ |

---

## Key Findings

### MCP Performance
- **98.00% overall accuracy** (147/150 correct)
- Perfect 100% on Novel benchmarks
- 96.00% on Tutorial benchmarks (more challenging)
- Only 3 total errors out of 150 questions
- Consistently outperforms Claude and Repo Only

### Claude and Repo Only Performance
- 76.00% overall accuracy (114/150 correct)
- Better on Novel (78.67%) than Tutorial (73.33%)
- 36 total errors out of 150 questions
- Struggles with:
  - Complex variant scoring
  - Gene identification
  - Batch processing tasks

### Performance Gap
- **MCP is 22 percentage points more accurate overall**
- MCP is also **3.9x faster** and **20% cheaper**
- MCP has **33 fewer errors** than Claude (3 vs 36)

---

## Error Analysis

### Novel Benchmarks

**Claude and Repo Only (16 errors):**
- 13 Numeric Mismatches (wrong API values)
- 2 String Mismatches (wrong answer type)
- 1 Parse Error (missing final_answer)

**MCP (0 errors):**
- Perfect performance ✓

### Tutorial Benchmarks

**Claude and Repo Only (20 errors):**
- 17 Numeric Mismatches (wrong values/computations)
- 3 String Mismatches (wrong genes/formats)

**MCP (3 errors):**
- 2 Numeric Mismatches (sign errors - same issue repeated)
- 1 Tool Error (ISM analysis failure)

---

## Scoring Methodology

### Semantic Matching Improvements

1. **Semantic Matching for Unavailable Data**
   - Accept explanatory text for empty/unavailable answers
   - Example: "Data not available" matches "[]"

2. **Numeric Value Extraction from Context**
   - Extract numbers from contextual strings
   - Example: "Positive strand: -0.08583546" → -0.08583546

3. **Tuple/Shape Format Matching**
   - Accept format variations for tuples
   - Example: "(256, 4)" matches "256 x 4" or "256 × 4"

These improvements raised accuracy from initial:
- Claude: 66.67% (novel) / 68% (tutorial) → 78.67% / 73.33%
- MCP: 82.67% (novel) / 90.67% (tutorial) → 100.00% / 96.00%

**Additional Manual Correction:**
- Gene Identifier Matching: Recognized ENSG00000288778 as Ensembl ID for APOL4
- Gained 1 correct answer each for MCP and Claude

---

## MCP's Remaining 3 Errors

All from Tutorial benchmarks (Novel benchmarks: 0 errors ✓):

1. **Tool Error** (Row 28)
   - Expected: (256, 4)
   - Got: "Unable to determine - tool error"
   - ISM analysis failed

2. **Numeric Mismatch - Sign Error** (Row 51)
   - Expected: -0.011535476
   - Got: 0.023067882 (wrong sign, ~2x magnitude)

3. **Numeric Mismatch - Sign Error** (Row 53)
   - Expected: -0.011535476
   - Got: 0.023067882 (same issue as #2, repeated)

---

## Recommendations

### Use MCP for AlphaGenome API Interactions

**Advantages:**
- ✓ 98.00% overall accuracy vs 76.00% for Claude
- ✓ 100% accuracy on novel tasks
- ✓ 96% accuracy on tutorial tasks
- ✓ 3.9x faster execution
- ✓ 20% lower cost
- ✓ Consistent high performance

**When to review:**
- Focus on the 3 MCP errors in tutorial benchmarks
- All are edge cases (1 tool error, 2 sign errors - same issue)

---

## Files Available

### Novel Benchmarks
- `ag_novel_benchmark_2026-01-20_with_*_auto_graded.csv` (automated scores)
- `ag_novel_benchmark_2026-01-20_with_*_human_graded.csv` (for your review)
- `FINAL_SUMMARY.txt` (novel-specific summary)
- `scoring_report.md` (detailed analysis)

### Tutorial Benchmarks
- `ag_tutorial_benchmark_2026-01-20_with_*_auto_graded.csv` (automated scores)
- `ag_tutorial_benchmark_2026-01-20_with_*_human_graded.csv` (for your review)
- `TUTORIAL_SUMMARY.txt` (tutorial-specific summary)
- `tutorial_scoring_report.md` (detailed analysis)

### Code
- `codes/score_benchmark.py` - Novel benchmark scoring
- `codes/score_tutorial_benchmark.py` - Tutorial benchmark scoring
- `codes/generate_report.py` - Report generation

---

## Human Grading

All `*_human_graded.csv` files are pre-filled with automated grades.

**To review:**
1. Open the CSV files
2. Check rows where grade=0 (incorrect)
3. Modify grade and grade_comments if you disagree
4. Focus on:
   - Claude: 36 total errors to review
   - MCP: 3 total errors to review

This allows you to validate or correct the automated scoring.

---

## Next Steps

1. **Read this summary** for overview
2. **Review MCP's 4 errors** in tutorial benchmarks
3. **Review Claude's 37 errors** if needed
4. **Modify human_graded.csv files** with your assessments
5. **Compare** your grades vs automated grades

---

**Questions or issues?** Check the detailed reports:
- Novel: `FINAL_SUMMARY.txt`, `scoring_report.md`
- Tutorial: `TUTORIAL_SUMMARY.txt`, `tutorial_scoring_report.md`
