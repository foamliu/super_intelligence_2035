# 外部评审意见：DAC 2027 submission — ZhuLong

> 来源：用户朋友（EDA/AI 会议评审视角）提供，2026-10-24 转交。
> 用途：作为 zhulong agent 的改稿依据；本文件只读存档，**不要修改评审原文**。

---

## Overall assessment

My assessment is that ZhuLong has a potentially compelling DAC paper, but the current draft has several substantial technical and experimental vulnerabilities that could prevent acceptance. The strongest contribution is the execution-grounded agent for custom EDA scripting; the biggest risk is that the paper's theoretical claims are stronger than what its experiments and formalization currently establish.

I'm evaluating the submitted seven-page draft from the perspective of an EDA/AI conference reviewer, focusing on technical novelty, evidence, reproducibility, and likely reviewer objections. This is a critical review, not a prediction of the actual DAC committee decision.

### Preliminary reviewer verdict

- **Verdict**: Borderline / major revision
- **Technical potential**: High
- **Evidence strength**: Moderate
- **Main strength**: Execution-grounded EDA automation across multiple runtimes
- **Main weakness**: Theory, benchmark validity, and reproducibility gaps

**Central recommendation**: Make the paper primarily an empirical EDA automation paper, with a carefully bounded grounding framework, rather than presenting the grounding-gap bound as an established theoretical result.

The paper's headline result is strong: ZhuLong achieves 75.7% pooled Pass@1 across 449 tasks, compared with 18.3% for the pure-LLM baseline and 62.5% for retrieval-only RAG. It also reports execution and retrieval ablations, multiple LLM backbones, and four commercial EDA runtimes. These are meaningful ingredients for a systems paper.

However, the draft also makes a broad claim that observation fidelity, rather than model scale, sets the accuracy ceiling. That claim is not yet established as strongly as the abstract and introduction suggest.

---

## 2. The five most serious issues to fix

### 1. The grounding-gap theory overclaims what is proved — **Critical**

Section 4 defines a grounding gap using Bayesian inference and then posits `D_grounding ≤ g(ε)`, where `g(ε) → 0` as observation error goes to zero. But the draft explicitly calls this a prediction, not a theorem derived in the paper.

The central difficulty is that the paper does not specify the assumptions needed to derive a meaningful bound, the divergence conditions under which the bound holds, or the form of `g`. The experimental trend cannot establish the proposed inequality by itself.

**Likely reviewer objection**: "The theoretical contribution is an intuitive hypothesis expressed in Bayesian notation rather than a demonstrated result."

**Recommended fix**: Either provide a formal proposition and proof under explicit assumptions, or call this a grounding-gap framework and treat it as a conceptual hypothesis evaluated empirically. Avoid presenting it as a proven theoretical bound.

### 2. The headline 57.4-point gain is attributed to the wrong comparison — **Critical**

The abstract and introduction say the observation ladder improves Pass@1 by 57.4 percentage points with the LLM fixed. However, Table 3 reports these read-back configurations:

| Configuration | Pass@1 |
|---|---|
| No read-back | 62.2% |
| Binary pass/fail | 65.5% |
| Full observation | 75.7% |
| Pure LLM baseline | 18.3% |

The full-observation versus no-read-back comparison is **13.5 percentage points**, not 57.4. The 57.4-point figure is the difference between the full system and the pure-LLM baseline, which changes more than observation alone.

This is a concrete attribution error, not merely a wording issue. It directly affects the paper's main theoretical argument.

**Recommended fix**: Correct the abstract, contribution bullets, Section 4.2, and Section 6.2.1. Report the controlled read-back effect as 13.5 points, the binary-feedback effect as 3.3 points over no read-back, and the pure-LLM-to-full-system improvement as 57.4 points. Explain these as separate comparisons.

### 3. The benchmark is difficult to independently verify — **Critical**

EDA-Scripting-Bench contains 449 tasks derived from non-redistributable vendor documentation. The draft explains the task schema and assertion-based scoring, but readers cannot readily inspect the full task set, reproduce all commercial runtime behaviors, or verify that the assertions adequately capture the intended design changes.

**Likely reviewer objection**: "The evaluation is performed on a proprietary benchmark with insufficiently demonstrated reproducibility and external validity."

**Recommended fix**: Provide as much of the benchmark as licensing permits:

- Public task descriptions, signatures, and assertion specifications.
- A documented procedure for obtaining authorized runtime access.
- A small, fully reproducible public subset.
- An evaluation harness, configuration files, and anonymized execution traces.
- Evidence that assertions distinguish the intended operation from plausible but incorrect implementations.

If the full benchmark cannot be released, explain exactly what independent researchers can reproduce.

### 4. The comparison against existing methods is too narrow — **Major**

The main experiments compare ZhuLong against a pure LLM and several component ablations, including retrieval-only RAG. This establishes that the complete harness is better than those configurations under the selected protocol, but it does not clearly establish superiority over the most relevant existing EDA agents or alternative execution-grounded coding systems.

**Recommended fix**: Add at least one strong, reproducible alternative that uses the same underlying LLM, API access, task budget, and execution environment. Consider:

- Retrieval plus execution without the full refinement strategy.
- A general-purpose coding agent with equivalent tool access.
- A simple retrieve–execute–repair loop.
- A stronger iterative baseline with the same execution-call budget.

Compare success rate, runtime, number of tool calls, and cost. If a baseline cannot access the commercial runtimes, explicitly distinguish that limitation from algorithmic superiority.

### 5. The component contributions are not uniformly demonstrated — **Major**

The full system does not win every slice. On SKILL, ZhuLong scores 60.3%, below the 61.5% reported without offline self-exploration. On PyAether, removing retrieval barely hurts in the reported ablation and even gives a higher score, 81.0% versus 77.3% for the system without self-exploration and 81.4% for the full system. The paper itself notes that toolchain-specific effects vary substantially.

**Recommended fix**: Reframe the contribution as a generally effective architecture with toolchain-dependent component value, rather than implying that every component is individually necessary in every setting. Add per-slice error analysis and uncertainty estimates, and investigate why offline self-exploration hurts SKILL.


---

## 3. Technical and experimental review

| Area | Assessment | What would strengthen it |
|---|---|---|
| Problem significance | Strong | Quantify real engineering pain points |
| System architecture | Promising | Explain implementation and runtime isolation more precisely |
| Technical novelty | Unclear to moderate | Distinguish the contribution from existing tool-using coding agents |
| Theoretical grounding | Weak in current form | Prove a meaningful result or narrow the claims |
| Benchmark design | Promising but difficult to verify | Release a reproducible subset and strengthen assertion validation |
| Experimental methodology | Reasonable foundation | Add controlled baselines, confidence intervals, and cost analysis |
| Cross-runtime generality | Encouraging | Report host-specific results and investigate failure modes |
| Practical impact | Potentially strong | Quantify engineering productivity and real workflow success |

### A. Is the novelty strong enough?

The paper's central system combines four MCP tools, API retrieval, documentation lookup, sandbox execution, and iterative refinement. Its offline API self-exploration process adds a useful engineering component.

The likely novelty challenge is that execution-based feedback and retrieval-augmented coding agents are already established approaches. The paper acknowledges related work such as ChatEDA, AutoEDA, MCP4EDA, LayoutCopilot, ChaTCL, and RAG-EDA, but the key distinction needs to be sharper.

Recommended: state three precise differences:
1. **Target environment**: custom/analog EDA scripting, where correctness depends on live layout, schematic, or waveform state.
2. **Execution interface**: one unified interface covers three scripting languages and four commercial runtimes.
3. **Empirical contribution**: a cross-runtime benchmark and controlled experiments measure the contribution of retrieval, execution feedback, and refinement.

The strongest novelty claim may be the combination of the multi-runtime infrastructure and its empirical study, rather than the general idea of an agent that executes code and repairs errors.

### B. Is the experimental design convincing?

Good features: 449 tasks, four runtime slices, five independent runs, assertion-based evaluation, a fixed primary backbone, ablations that remove individual capabilities.

Remaining questions:
- **Statistical evidence is limited.** Five runs and reported standard deviations are a useful start, but they do not establish the significance of every component-level difference. Add confidence intervals and paired comparisons where appropriate. In particular, the 3.1-point pooled gain from self-exploration deserves cautious interpretation.
- **The budget comparison needs better characterization.** Each task has a 2,500-second timeout, but the paper should report actual latency distributions, execution-call counts, token usage, and failure rates. The claimed 27% reduction in net-active solve time from self-exploration is interesting, but it appears to rely on supplementary material rather than evidence shown in the main seven-page paper.
- **The benchmark's scoring scope must be explicit.** A task passes when code executes without errors and the assertions hold. That is reasonable, but the paper acknowledges that this does not certify full functional equivalence. Explain how assertions are designed, whether they are independently reviewed, and how false positives are prevented.

### C. Is the cross-toolchain result convincing?

Reported pooled results:
- **PyAether**: full system 81.4%; execution alone performs nearly as well in the reported ablation.
- **SKILL**: full system 60.3%, while retrieval plus execution without self-exploration reaches 61.5%.
- **Tcl**: pooled 87.2%, although this combines two distinct workloads (WaveView and Innovus).

These differences are scientifically interesting — they suggest the value of API retrieval, offline exploration, and live feedback depends on the scripting interface and the information recoverable from the runtime.

Recommendation: expand the error analysis and report WaveView and Innovus separately in the main results if space permits. A strong explanation of why the architecture behaves differently across interfaces could be more convincing than simply asserting generality.

---

## 4. Specific problems in the current seven-page draft

### Must fix

1. **Correct the 57.4-point attribution.** Align the abstract, contribution list, theoretical section, and experimental discussion with Table 3.
2. **Resolve the theoretical overclaim.** Section 4.2 explicitly presents the observation-fidelity bound as a prediction rather than a theorem. The title and abstract can remain ambitious, but the wording must accurately reflect the evidence.
3. **Clarify the role of the benchmark.** Explain availability, licensing constraints, reproducibility, assertion construction, and the limitations of execution-based scoring.
4. **Strengthen related-work comparisons.** Make the differences from the closest EDA and coding-agent systems explicit and substantiate any superiority claims.
5. **Fix the reference-format placeholder.** The ACM reference-format text contains "In Proceedings of . ACM," which is incomplete. Ensure the final bibliography and conference metadata conform to the actual submission requirements.

### Strongly recommended

1. Report latency, tool calls, token usage, and cost alongside Pass@1.
2. Explain the SKILL self-exploration regression and the large variance in some ablations.
3. Report WaveView and Innovus independently instead of relying exclusively on pooled Tcl results.
4. Clarify the distinction between the retrieval observation channel and actual observations of live design state. These are not interchangeable sources of evidence.
5. Substantiate the production deployment claim with measurable evidence, such as adoption, task completion, or engineering time saved, where disclosure is permitted.


---

## 5. Suggested revision of the paper's main claims

Distinguish what is demonstrated from what is hypothesized.

**Current framing to reconsider**
> The grounding gap is bounded by observation fidelity, not model scale.

**Safer framing**
> We investigate how observation fidelity and model choice affect execution-based correctness in EDA scripting. Across our benchmark, controlled changes to execution feedback produce substantial accuracy differences, while the tested backbone choices also have a material effect. These findings motivate an observation-centric framework for understanding EDA agent reliability.

The revised wording preserves the central idea without asserting a general mathematical bound established by experiments.

Also make the abstract's empirical contribution more concrete:
- State the 449-task benchmark and four runtime slices.
- Report the full-system result and the pure-LLM and retrieval-only baselines.
- Separate the controlled read-back comparison from the overall system-versus-baseline comparison.
- Describe offline self-exploration as a complementary component whose benefits vary by toolchain.
- Present the theoretical framework as a hypothesis unless a formal result is added.

---

## 6. A plausible reviewer report (Reviewer #2 — EDA automation and AI agents)

**Recommendation**: Borderline

**Summary**: This paper presents ZhuLong, an execution-grounded LLM agent for EDA scripting across PyAether, SKILL, and Tcl. The system integrates API retrieval, documentation lookup, offline API exploration, and sandbox execution in an iterative generation-and-refinement loop. The authors evaluate on 449 tasks across four commercial runtimes and report a pooled Pass@1 of 75.7%, substantially exceeding the pure-LLM and retrieval-only baselines.

**Strengths**
- The problem is practically important: EDA scripting requires tool-specific API knowledge and correctness in stateful design environments.
- The system architecture is coherent and integrates knowledge retrieval with execution feedback.
- The multi-runtime evaluation is broader than a single-tool demonstration.
- The ablation study provides useful evidence about the contributions of retrieval and execution.
- The production-use claim suggests practical relevance beyond a benchmark.

**Weaknesses**
- The theoretical grounding-gap bound is stated as a prediction without a derivation, and the empirical evidence does not establish the claimed general relationship.
- The reported 57.4-percentage-point gain is incorrectly associated with the controlled observation ladder; Table 3 indicates a 13.5-point difference between no read-back and full observation.
- The benchmark is based on non-redistributable vendor documentation, limiting independent verification.
- The baseline set does not sufficiently establish superiority over alternative execution-grounded coding agents.
- The contribution of offline self-exploration is modest overall and negative on the SKILL slice.
- Runtime cost, statistical uncertainty, and practical productivity benefits are insufficiently characterized.

**Questions for the authors**
1. Can the authors formally derive the proposed observation-fidelity bound, or should it be presented as a hypothesis?
2. What portion of EDA-Scripting-Bench can be released for independent reproduction?
3. How does ZhuLong compare with a strong general-purpose coding agent given equivalent tool access and execution budgets?
4. Why does self-exploration reduce performance on SKILL?
5. What is the cost in latency, model usage, and engineer time per successfully completed task?

---

## 7. Revision priorities if time is limited

### Revision checklist (0 of 6)

1. **Correct the headline numerical inconsistency** — fix the 57.4-point observation claim everywhere.
2. **Reframe or formalize the grounding-gap claim** — avoid a theorem-like claim without a proof.
3. **Strengthen the baseline and reproducibility story** — add the strongest feasible control and release a reproducible subset.
4. **Add cost and statistical evidence** — report uncertainty, runtime, tool calls, and model usage.
5. **Explain cross-runtime regressions** — investigate SKILL and split the Tcl results.
6. **Tighten the paper's contribution statement** — emphasize the EDA-specific system and benchmark.

### Final verdict
> I would not submit this exact draft without revision. The paper has a credible systems contribution and encouraging results, but the numerical attribution error is easy for reviewers to detect, and the theory, benchmark reproducibility, and comparative evaluation leave avoidable openings for rejection.
>
> The most effective strategy is to make the empirical system contribution unmistakable, make every numerical claim match the controlled experiment that supports it, and either strengthen the theory substantially or reduce its role in the paper.

