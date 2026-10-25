# Evaluation results

Run locally against the bundled PDFs with `python evals/run_evals.py`.

- Retrieval hit rate at top-4: **15/15 (100%)**
- Evidence keyword check: **15/15 (100%)**

The answer check is offline: it verifies that all expected answer keywords appear in the retrieved evidence. It is a groundedness proxy, not an LLM judge.

| Question | Expected page in top-4 | Evidence keywords found |
| --- | --- | --- |
| What are the core collaboration hours? | yes | yes |
| Where should delivery-date decisions be recorded? | yes | yes |
| When is weekly planning held? | yes | yes |
| What must exist before scheduling a meeting? | yes | yes |
| How quickly should non-urgent chat receive a response? | yes | yes |
| How should an urgent production issue be marked? | yes | yes |
| How much home-office equipment can be reimbursed? | yes | yes |
| When should time off be requested? | yes | yes |
| How long do employees have to submit equipment receipts? | yes | yes |
| What is the laptop replacement cycle? | yes | yes |
| Where is the community garden located? | yes | yes |
| When are garden volunteer sessions? | yes | yes |
| How much rainwater can the garden store? | yes | yes |
| When are tomatoes planted? | yes | yes |
| Where does excess garden produce go? | yes | yes |

This is the baseline for the current 700-character chunks with 120-character overlap. Future changes should be compared against these two figures.
