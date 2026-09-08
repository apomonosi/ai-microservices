# Full catalog

The [service catalog](services/index.md) is what's built, generated straight
from `services/*.yaml`. This page is the wider list it's drawn from: the
original 145-entry brainstorm, organized by category, with a status per
entry and — where one exists — a link to the actual built service. As
[Roadmap](roadmap.md#growing-the-service-library) says, it's a backlog, not
a deliverable: there's no fixed target count, and growing it is opportunistic.

Reading it as a whole is also the argument for building this way at all.
The dominant verb is *check* — structure, methodology, statistics,
citations, terminology, numbers that should agree but don't — not
*generate*. Checking is where a small model is strongest and a wrong
answer is cheapest to catch, which is why the catalog fills in from there
rather than from the handful of entries (a novelty reviewer, a full thesis
examiner) that need real judgement. See [Design principles](philosophy.md)
for what that implies about which model backs which service.

| # | Category | AI Service | Short description | Status | Built as |
|--:|---|---|---|:--:|---|
| 1 | Academic Writing | Academic Proofreader | Grammar, spelling, clarity, academic style | ✅ Done | [`proofread`](services/proofread.md) |
| 2 | Academic Writing | Academic Style Converter | Convert informal/technical/plain/academic styles | ✅ Done | [`academic-style-convert`](services/academic-style-convert.md) |
| 3 | Academic Writing | Journal Style Adapter | Adapt manuscript to journal guidelines | ⬜ Not started |  |
| 4 | Academic Writing | Abstract Generator | Generate structured and conventional abstracts | ✅ Done | [`summarize`](services/summarize.md) |
| 5 | Academic Writing | Title Generator | Generate and evaluate academic titles | ✅ Done | [`generate-titles`](services/generate-titles.md) |
| 6 | Academic Writing | Introduction Reviewer | Evaluate problem, gap, question and contribution | ✅ Done | [`introduction-review`](services/introduction-review.md) |
| 7 | Academic Writing | Argument Mapper | Map claims, arguments and supporting evidence | ⬜ Not started |  |
| 8 | Academic Writing | Academic Structure Checker | Check logical organization of a manuscript | ⬜ Not started |  |
| 9 | Academic Writing | Terminology Consistency Checker | Detect inconsistent terminology and abbreviations | ✅ Done | [`terminology-check`](services/terminology-check.md) |
| 10 | Academic Writing | Academic Conciseness Checker | Identify unnecessary verbosity and repetition | ✅ Done | [`make-concise`](services/make-concise.md) |
| 11 | References | Reference Checker | Verify bibliographic references and metadata | ✅ Done | [`reference-check`](services/reference-check.md) |
| 12 | References | Citation Verifier | Verify DOI, authors, title, journal and year | ⬜ Not started |  |
| 13 | References | Citation–Claim Checker | Determine whether citations support claims | ⬜ Not started |  |
| 14 | References | Citation Completeness Checker | Identify claims that probably need citations | ✅ Done | [`citation-completeness`](services/citation-completeness.md) |
| 15 | References | Citation Overuse Checker | Identify unnecessary or excessive citations | ✅ Done | [`citation-overuse`](services/citation-overuse.md) |
| 16 | References | Citation Recency Checker | Identify outdated supporting literature | ⬜ Not started |  |
| 17 | References | Reference Formatter | Convert references between citation styles | ⬜ Not started |  |
| 18 | References | Bibliography Deduplicator | Detect duplicate references | ✅ Done | [`biblio-dedupe`](services/biblio-dedupe.md) |
| 19 | References | Suspicious Reference Detector | Identify references that cannot be verified | ✅ Done | [`suspicious-reference-detect`](services/suspicious-reference-detect.md) |
| 20 | References | DOI Resolver | Find and validate DOI metadata | ✅ Done | [`doi-resolve`](services/doi-resolve.md) |
| 21 | Literature | Literature Review Assistant | Assist with planning and conducting reviews | ✅ Done | [`literature-review-assist`](services/literature-review-assist.md) |
| 22 | Literature | Search Query Generator | Generate database-specific search strategies | ✅ Done | [`search-query-generate`](services/search-query-generate.md) |
| 23 | Literature | Search Strategy Critic | Evaluate literature search strategies | ✅ Done | [`search-strategy-critic`](services/search-strategy-critic.md) |
| 24 | Literature | Paper Screening Assistant | Classify papers as include/exclude/maybe | ⬜ Not started |  |
| 25 | Literature | Full-Text Screening Assistant | Screen full papers against criteria | ⬜ Not started |  |
| 26 | Literature | Literature Clustering | Group papers into thematic areas | ⬜ Not started |  |
| 27 | Literature | Literature Gap Finder | Identify potentially underexplored areas | ⬜ Not started |  |
| 28 | Literature | Literature Contradiction Finder | Find conflicting research findings | ⬜ Not started |  |
| 29 | Literature | Literature Consensus Mapper | Identify areas of broad agreement | ⬜ Not started |  |
| 30 | Literature | Literature Timeline | Map development of a research field | ⬜ Not started |  |
| 31 | Literature | Research Landscape Mapper | Map topics, authors, institutions and methods | ⬜ Not started |  |
| 32 | Literature | Paper Comparison Tool | Compare multiple papers systematically | ⬜ Not started |  |
| 33 | Paper Review | AI Paper Pre-Reviewer | Pre-review manuscript before submission | ⬜ Not started |  |
| 34 | Paper Review | Structure Reviewer | Check consistency between paper sections | ✅ Done | [`structure-review`](services/structure-review.md) |
| 35 | Paper Review | Methodology Reviewer | Evaluate research design and methods | ✅ Done | [`methodology-review`](services/methodology-review.md) |
| 36 | Paper Review | Statistical Reviewer | Identify statistical-method concerns | ✅ Done | [`statistical-review`](services/statistical-review.md) |
| 37 | Paper Review | Reproducibility Reviewer | Check whether research can be reproduced | ✅ Done | [`reproducibility-review`](services/reproducibility-review.md) |
| 38 | Paper Review | Claims Reviewer | Audit strength and support of major claims | ✅ Done | [`claims-review`](services/claims-review.md) |
| 39 | Paper Review | Novelty Reviewer | Compare contribution against supplied literature | ⬜ Not started |  |
| 40 | Paper Review | Reviewer #2 Simulator | Generate skeptical reviewer questions | ✅ Done | [`reviewer2-simulate`](services/reviewer2-simulate.md) |
| 41 | Paper Review | Journal Rejection Risk Analyzer | Identify likely desk-review/rejection risks | ⬜ Not started |  |
| 42 | Paper Review | Reviewer Response Checker | Check whether author addressed reviewer comments | ⬜ Not started |  |
| 43 | Thesis | Thesis Structure Auditor | Audit overall thesis structure | ✅ Done | [`thesis-structure-audit`](services/thesis-structure-audit.md) |
| 44 | Thesis | Thesis Consistency Checker | Find contradictions across chapters | ✅ Done | [`thesis-consistency-check`](services/thesis-consistency-check.md) |
| 45 | Thesis | Thesis Terminology Checker | Ensure terminology is consistent | ⬜ Not started |  |
| 46 | Thesis | Thesis Examiner | Simulate examiner assessment | ✅ Done | [`thesis-examine`](services/thesis-examine.md) |
| 47 | Thesis | Viva Simulator | Simulate oral thesis defense | ⬜ Not started |  |
| 48 | Thesis | Thesis-to-Presentation | Convert thesis into defense presentation | ⬜ Not started |  |
| 49 | Thesis | Thesis-to-Public-Summary | Produce accessible thesis summary | ⬜ Not started |  |
| 50 | Thesis | Thesis Chapter Reviewer | Review individual thesis chapters | ⬜ Not started |  |
| 51 | Research Design | Research Question Critic | Evaluate research-question quality | ✅ Done | [`research-question-critic`](services/research-question-critic.md) |
| 52 | Research Design | Hypothesis Reviewer | Evaluate hypotheses | ✅ Done | [`hypothesis-review`](services/hypothesis-review.md) |
| 53 | Research Design | Study Design Assistant | Suggest appropriate study designs | ✅ Done | [`study-design-assist`](services/study-design-assist.md) |
| 54 | Research Design | Survey Question Reviewer | Detect poor/biased/ambiguous questions | ✅ Done | [`survey-question-review`](services/survey-question-review.md) |
| 55 | Research Design | Interview Guide Reviewer | Evaluate interview questions | ⬜ Not started |  |
| 56 | Research Design | Qualitative Coding Assistant | Suggest codes and themes | ✅ Done | [`qualitative-coding-assist`](services/qualitative-coding-assist.md) |
| 57 | Research Design | Codebook Generator | Generate candidate qualitative codebooks | ✅ Done | [`codebook-generate`](services/codebook-generate.md) |
| 58 | Data & Statistics | Statistical Method Selector | Match research questions to methods | ✅ Done | [`statistical-method-select`](services/statistical-method-select.md) |
| 59 | Coding | Code Assistant | Generate/explain research code | ✅ Done | [`code-assist`](services/code-assist.md) |
| 60 | Coding | Code Reviewer | Review Python/R/other research code | ✅ Done | [`review-code`](services/review-code.md) |
| 61 | Coding | Jupyter Notebook Auditor | Check reproducibility and notebook quality | ✅ Done | [`notebook-audit`](services/notebook-audit.md) |
| 62 | Data & Statistics | Statistical Interpretation Checker | Compare statistical output with interpretation | ✅ Done | [`statistical-interpretation-check`](services/statistical-interpretation-check.md) |
| 63 | Data & Statistics | Table Checker | Check tables against manuscript text | ✅ Done | [`table-check`](services/table-check.md) |
| 64 | Data & Statistics | Figure Caption Generator | Generate scientific figure captions | ⬜ Not started |  |
| 65 | Data & Statistics | Numerical Consistency Checker | Find inconsistent numbers across documents | ✅ Done | [`numerical-consistency-check`](services/numerical-consistency-check.md) |
| 66 | Research Integrity | Research Integrity Preflight | Comprehensive integrity audit | ⬜ Not started |  |
| 67 | Research Integrity | Claim–Evidence Auditor | Trace major claims to evidence | ✅ Done | [`claims-review`](services/claims-review.md) |
| 68 | Research Integrity | Data Provenance Checker | Check where reported data came from | ✅ Done | [`data-provenance-check`](services/data-provenance-check.md) |
| 69 | Research Integrity | AI Disclosure Assistant | Generate appropriate AI-use disclosure | ✅ Done | [`ai-disclosure-assist`](services/ai-disclosure-assist.md) |
| 70 | Research Integrity | AI Policy Compliance Checker | Check AI use against institutional policy | ⬜ Not started |  |
| 71 | Research Integrity | Research Reporting Checker | Check completeness of research reporting | ⬜ Not started |  |
| 72 | Research Integrity | Statistical Integrity Checker | Flag questionable statistical claims | ⬜ Not started |  |
| 73 | Teaching | Assignment Generator | Generate assignments from learning objectives | ✅ Done | [`assignment-generate`](services/assignment-generate.md) |
| 74 | Teaching | Assignment Quality Reviewer | Evaluate assignment quality | ✅ Done | [`assignment-quality-review`](services/assignment-quality-review.md) |
| 75 | Teaching | Rubric Generator | Generate assessment rubrics | ⬜ Not started |  |
| 76 | Teaching | Rubric Consistency Checker | Check rubric against assignment/objectives | ⬜ Not started |  |
| 77 | Teaching | Exam Question Generator | Generate questions by difficulty/cognitive level | ✅ Done | [`exam-question-generate`](services/exam-question-generate.md) |
| 78 | Teaching | Exam Question Quality Checker | Detect ambiguity and quality problems | ✅ Done | [`exam-question-quality-review`](services/exam-question-quality-review.md) |
| 79 | Teaching | Student Feedback Generator | Generate formative feedback | ✅ Done | [`student-feedback-generate`](services/student-feedback-generate.md) |
| 80 | Teaching | Socratic Tutor | Guide students through questions | ⬜ Not started |  |
| 81 | Teaching | Misconception Detector | Identify conceptual misunderstandings | ✅ Done | [`misconception-detect`](services/misconception-detect.md) |
| 82 | Course Material | Lecture-to-Study-Guide | Convert lectures/slides to study guides | ✅ Done | [`lecture-to-studyguide`](services/lecture-to-studyguide.md) |
| 83 | Course Material | Lecture-to-Quiz | Generate quizzes from course material | ⬜ Not started |  |
| 84 | Course Material | Lecture-to-Flashcards | Generate study flashcards | ⬜ Not started |  |
| 85 | Course Material | Course Q&A | Answer strictly from course material | ✅ Done | [`course-qa`](services/course-qa.md) |
| 86 | Course Material | Course Knowledge Graph | Map concepts and prerequisites | ⬜ Not started |  |
| 87 | Administration | Policy Q&A | Answer questions from university policies | ✅ Done | [`policy-qa`](services/policy-qa.md) |
| 88 | Administration | Regulation Explainer | Explain bureaucratic regulations simply | ✅ Done | [`regulation-explain`](services/regulation-explain.md) |
| 89 | Administration | Policy Comparison | Compare old/new policies | ⬜ Not started |  |
| 90 | Administration | Form Assistant | Assist with institutional forms | ⬜ Not started |  |
| 91 | Research Admin | Ethics Application Assistant | Help prepare ethics applications | ⬜ Not started |  |
| 92 | Grants | Grant Proposal Reviewer | Review proposals against criteria | ⬜ Not started |  |
| 93 | Grants | Call-to-Requirements Extractor | Extract requirements from funding calls | ✅ Done | [`grant-call-extract`](services/grant-call-extract.md) |
| 94 | Grants | Proposal Compliance Checker | Check proposal against call requirements | ⬜ Not started |  |
| 95 | Grants | Grant Abstract Optimizer | Improve grant abstracts | ⬜ Not started |  |
| 96 | Grants | Budget Narrative Checker | Compare budget and narrative | ⬜ Not started |  |
| 97 | Grants | Funding Opportunity Matcher | Match researchers to funding calls | ⬜ Not started |  |
| 98 | Research Management | Research Meeting Summarizer | Summarize scientific meetings | ✅ Done | [`meeting-summarize`](services/meeting-summarize.md) |
| 99 | Research Management | Meeting-to-Action-Items | Extract decisions, owners and deadlines | ✅ Done | [`meeting-action-items`](services/meeting-action-items.md) |
| 100 | Research Management | Research Risk Register | Identify project risks | ✅ Done | [`research-risk-register`](services/research-risk-register.md) |
| 101 | Research Management | Milestone Health Checker | Identify project delays/issues | ⬜ Not started |  |
| 102 | Knowledge | Department Knowledge Assistant | Q&A over department documents | ✅ Done | [`department-knowledge-assistant`](services/department-knowledge-assistant.md) |
| 103 | Knowledge | Lab Knowledge Assistant | Q&A over lab knowledge | ⬜ Not started |  |
| 104 | Knowledge | Research Group Assistant | Search internal research knowledge | ⬜ Not started |  |
| 105 | Knowledge | Research Project Memory | Search decisions, notes and documents | ⬜ Not started |  |
| 106 | Equipment | Equipment Assistant | Answer questions from equipment manuals | ⬜ Not started |  |
| 107 | Language | Academic Translator | Academic translation | ✅ Done | [`translate-da`](services/translate-da.md) |
| 108 | Language | Academic Terminology Translator | Preserve specialist terminology | ⬜ Not started |  |
| 109 | Language | Abstract Translator | Translate abstracts accurately | ⬜ Not started |  |
| 110 | Language | Plain-Language Translator | Academic → public language | ✅ Done | [`plain-language`](services/plain-language.md) |
| 111 | Accessibility | Accessibility Checker | Identify accessibility problems | ✅ Done | [`accessibility-check`](services/accessibility-check.md) |
| 112 | Accessibility | Academic Alt-Text Generator | Generate figure/image descriptions | ⬜ Not started |  |
| 113 | Accessibility | Chart Explainer | Convert charts into textual explanations | ⬜ Not started |  |
| 114 | Accessibility | Lecture Accessibility Assistant | Create accessible lecture materials | ⬜ Not started |  |
| 115 | Library | Library Research Assistant | Guide researchers through library resources | ⬜ Not started |  |
| 116 | Library | Database Selection Assistant | Recommend appropriate databases | ⬜ Not started |  |
| 117 | Library | Search Strategy Critic | Audit systematic-review searches | ✅ Done | [`search-strategy-critic`](services/search-strategy-critic.md) |
| 118 | Library | Subject Heading Assistant | Map concepts to controlled vocabularies | ⬜ Not started |  |
| 119 | Publishing | Review Quality Checker | Assess quality of peer reviews | ⬜ Not started |  |
| 120 | Publishing | Reviewer Tone Checker | Make reviews more constructive | ✅ Done | [`reviewer-tone-fix`](services/reviewer-tone-fix.md) |
| 121 | Publishing | Reviewer Conflict Checker | Identify potential conflicts | ⬜ Not started |  |
| 122 | Publishing | Reviewer Expertise Assistant | Identify required expertise areas | ⬜ Not started |  |
| 123 | Communication | Paper-to-Press-Release | Convert research to press release | ✅ Done | [`paper-to-press-release`](services/paper-to-press-release.md) |
| 124 | Communication | Paper-to-Policy-Brief | Convert research to policy brief | ⬜ Not started |  |
| 125 | Communication | Paper-to-Website | Convert research to web copy | ⬜ Not started |  |
| 126 | Communication | Paper-to-Poster | Generate conference-poster content | ⬜ Not started |  |
| 127 | Communication | Paper-to-3MT | Generate Three Minute Thesis script | ⬜ Not started |  |
| 128 | Communication | Paper-to-Social | Generate social-media research summaries | ✅ Done | [`paper-to-social`](services/paper-to-social.md) |
| 129 | Secure AI | Confidential Document Summarizer | Process sensitive documents locally | ⬜ Not started |  |
| 130 | Secure AI | Confidential Meeting Summarizer | Process sensitive meetings locally | ⬜ Not started |  |
| 131 | Secure AI | Private Grant Reviewer | Review confidential proposals locally | ⬜ Not started |  |
| 132 | Secure AI | Private Thesis Assistant | Analyze unpublished thesis material | ⬜ Not started |  |
| 133 | Secure AI | Research Notes Assistant | Search private research notes | ⬜ Not started |  |
| 134 | Academic Linting | Academic Linter | Automated manuscript quality checks | ⬜ Not started |  |
| 135 | Academic Linting | Manuscript Preflight | Run comprehensive manuscript checks | ⬜ Not started |  |
| 136 | Academic Linting | Journal Submission Preflight | Check manuscript before submission | ⬜ Not started |  |
| 137 | Academic Linting | Thesis Preflight | Comprehensive thesis checks | ⬜ Not started |  |
| 138 | Academic Linting | Grant Preflight | Comprehensive grant checks | ⬜ Not started |  |
| 139 | Academic Linting | Assignment Preflight | Check assignment before release | ⬜ Not started |  |
| 140 | AI Infrastructure | AI Service Gateway | Unified API for university AI services | ⬜ Not started |  |
| 141 | AI Infrastructure | Model Router | Select local/cloud model per task | ⬜ Not started |  |
| 142 | AI Infrastructure | University RAG Service | Shared retrieval layer for institutional data | ⬜ Not started |  |
| 143 | AI Infrastructure | AI Evaluation Service | Benchmark service quality systematically | ⬜ Not started |  |
| 144 | AI Infrastructure | Prompt/Model Registry | Version prompts and specialized models | ⬜ Not started |  |
| 145 | AI Infrastructure | AI Audit Log | Record AI operations and provenance | ⬜ Not started |  |

## What the still-open entries share

The 145 aren't 145 separate projects — most of what's left shares
infrastructure that hasn't been built yet, roughly in this order:

| Layer | What it takes | Unlocks |
|---|---|---|
| Document layer | PDF/DOCX parsing, OCR, chunking | Multi-file inputs — theses, whole papers |
| Retrieval layer *(partially built — [`corpus: <id>`](guide/service-manifest.md#corpus-id), BM25 lexical search)* | Embeddings/vector search, PDF/DOCX ingestion still open | Rows 85, 87, 102 now use it (`course-qa`, `policy-qa`, `department-knowledge-assistant`). Rows 103–106, 115, 116, 118 stay open — same mechanism, just not built yet |
| Verification layer *(partially built — [`verify: crossref`](guide/service-manifest.md#verify-crossref))* | Crossref lookups done; OpenAlex/PubMed, retries, caching still open | Rows 11, 19, 20 now use it (`reference-check`, `suspicious-reference-detect`, `doi-resolve`). Rows 12, 16 stay open as close-duplicates for now; row 17 (Reference Formatter) doesn't actually need this layer — it's a deterministic format conversion, not verification |
| Model router | Route by task, not by default | The minority that outgrows a small local model — e.g. a real Novelty Reviewer (row 39), comparing a manuscript against a whole supplied corpus |
| Audit log | Record what ran, on what, with which model | Anything used for actual grading or institutional decisions |

That's rows 140–145 (*AI Infrastructure*) in the table above, and it's
deliberately last: the current engine covers the single-pasted-text case
well, and each of these layers is its own project, worth building only
once a specific entry needs it — see
[Roadmap](roadmap.md#growing-the-service-library) for what's explicitly
out of scope for now and why.
