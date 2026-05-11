# Failure Case Autopsy Report

## Executive Summary

Our updated 15-query evaluation revealed a **66% retrieval precision@5** and **73% answer accuracy**. 

---

## Top-K Saturation (CV Domination)

**Affected Queries:** Q5, Q6, Q13
**Category:** retrieval_imbalance
**Severity:** High (blocks job matching)

### Symptom

When asked questions specifically about job requirements (Q5: "What programming languages are required for the job?"), the system retrieves **only CV chunks**. The top 5 results are saturated with the candidate's technical skills, leaving no room for the job description's requirements. As a result, the LLM correctly reports that it cannot find the information, even though the JD is present in the database.

### Failure Chain

```
Query: "What programming languages are required for the job?"
   |
   v
Embedding: Maps to "programming languages", "required", "job"
   |
   v
Qdrant: Scoring matches:
        #1 Ahmed.pdf (Skills list)       (score: 0.896)
        #2 Ahmed.pdf (Certifications)    (score: 0.866)
        #3 Ahmed.pdf (Languages)         (score: 0.866)
        #4 Ahmed.pdf (Summary)           (score: 0.864)
        #5 Ahmed.pdf (Work History)      (score: 0.855)
   |
   v
LLM: Receives only CV chunks -> "I could not find this information"
```

### Root Cause

The candidate's CV is much denser in "technical keywords" than the job description. The word "languages" in the query triggers a high score for the CV's "Technical Skills > Languages" section. Because all chunks compete in a flat index, the dense skills list from the CV scores consistently higher than the relatively sparse requirements in the JD.

### Proposed Fix

1. **Category-Aware Retrieval**: Increase `top_k` to 10 or 15 to ensure chunks from multiple documents can "break through" the top tier.
2. **Diversity Re-ranking (MMR)**: Implement Maximum Marginal Relevance to penalize redundancy (retrieving 5 chunks from the same file) and force document diversity in the prompt.

---

## Context Neglect (Position Bias)

**Affected Queries:** Q4, Q14
**Category:** llm_extraction_failure
**Severity:** Medium

### Symptom

Even when the relevant Job Description chunk is retrieved and placed in the prompt (e.g., Q14 at Document No. 5), the LLM claims it "could not find a job description." The information is physically present in the prompt, but the LLM ignores it or fails to synthesize it with the CV content.

### Failure Chain

```
Query: "Summarise the strongest match between any CV and the job description."
   |
   v
Retrieval: 
        Docs 1-4: Ahmed.pdf (Skills/Projects)
        Doc 5: intern-description.txt (About Us)
   |
   v
Prompt: Long list of CV skills followed by a short "About Dubizzle" chunk
   |
   v
LLM: Focuses on the first 4 documents -> "Could not find job description"
```

### Root Cause

**Position Bias / Lost-in-the-Middle**: LLMs often struggle with information placed at the end of a long context. Since Document 5 was the only JD chunk and it appeared after four dense CV chunks, the LLM's attention mechanism prioritized the candidate's profile. Furthermore, the retrieved JD chunk was the "About Us" section rather than the "Requirements" section, making it less recognizable as a "Job Description" to the LLM.

### Proposed Fix

1. **Hybrid Retrieval**: Combine vector search with keyword search (BM25) to ensure "Requirements" headers in the JD are prioritized.
2. **Prompt Structuring**: Group retrieved chunks by document source in the prompt (e.g., "DOCUMENTS FROM CV:" and "DOCUMENTS FROM JD:") to help the LLM navigate the context.


## Summary Table (Updated)

| # | Failure Type | Queries | Root Cause | Fix Complexity |
|---|-------------|---------|------------|----------------|
| 1 | Top-K Saturation | Q5, Q6, Q13 | Flat index, dense CV keywords | Medium |
| 2 | Context Neglect | Q4, Q14 | Position bias, sub-optimal chunking | Easy |

## Architecture Improvement Roadmap

1. **Short Term**: Increase `top_k` to 10. Group chunks by filename in the LLM prompt.
2. **Medium Term**: Implement MMR (Max Marginal Relevance) for chunk diversity.
3. **Long Term**: Multi-vector indexing (separate collections for CVs and JDs).

