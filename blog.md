# Replacing Ourselves at the Job

Hi. We're QuietLab.

We're Ishan and Niranjan, and on most Mondays we put on our IBM badges and go work on mainframe modernization at IBM. Specifically: on the tooling that helps engineers move COBOL code off the mainframe, with an AI assistant that suggests the modernized version.

So when this hackathon was announced, picking the topic took about thirty seconds.

## A two-paragraph mainframe primer

Mainframes are big computers from an earlier era of computing. IBM mostly. They're physically huge, eye-wateringly expensive, and absurdly reliable. They don't go down, they don't really break, and they process transactions at a scale the cloud still finds embarrassing. About 95% of US ATM transactions touch one. Roughly $3 trillion in daily commerce flows across them. By IBM's count, ~70% of global business transactions still pass through a mainframe somewhere in the pipeline.

These machines mostly run code written in COBOL, a language designed in 1959. Despite "COBOL is dying" being declared once a decade for the last fifty years, there are around **220 billion lines of it in active production today**. Banks, insurance companies, governments, airlines, payroll, tax systems. The plumbing of the world.

## The not-so-fun part

The engineers who wrote this stuff are retiring. The average COBOL developer is now 55. About 10% of that workforce hits retirement every year. Universities stopped teaching the language somewhere around 1995. The result is a quiet but compounding crisis: the code that runs the world is being maintained by a shrinking group of people who are increasingly tired and would frankly like to be golfing.

So companies are paying enormous amounts of money to migrate off it. The mainframe modernization market is roughly **$8.4B in 2025**, projected to hit **$13.3B by 2030**, and that's the narrow slice. The broader application modernization market is on track for **$100B+ by 2035**. Replacing a single working COBOL system routinely costs upward of $50 million. AWS, IBM, Capgemini, Accenture, TCS: every major consulting firm has a dedicated practice for it. Most of the migrations target Java or Python.

There's a temptation to think AI just solves this. In February 2026, Anthropic published a blog suggesting Claude could "rapidly refactor" COBOL codebases. IBM's stock dropped 13% in a single day, its worst crash since 2000, and Wall Street briefly believed the mainframe business was dead.

Then everyone calmed down, because IBM SVP Rob Thomas pointed out the obvious: **translation isn't modernization.** Real legacy code lives inside fixed-width records, copybooks, implied decimals, level-88 condition names, branch precedence, weird date semantics, and small formatting details that have to be preserved exactly or your entire payroll system silently breaks at midnight. A model that one-shots COBOL into Python is a toy. A model that actually does the *work* of a modernization engineer is the unsolved problem.

## The pitch

We don't love the job.

So, like any reasonable software engineers, we tried to build a thing that might one day replace us at it.

## What we built

**Legacy COBOL Migration Workbench**: an OpenEnv environment where a small LLM is trained, via reinforcement learning, to behave less like a translator and more like a careful modernization engineer.

Each episode is one migration ticket. The agent receives a high-level request and a list of available files, and that's it. From there it has tools:

- `read_cobol_file`: read a COBOL source file
- `read_copybook`: read a referenced copybook
- `parse_copybook_layout`: extract field offsets, lengths, scales, condition names
- `inspect_business_rules`: surface hints about branch precedence and edge cases
- `write_python_solution`: draft a Python implementation
- `run_visible_tests`: try the draft against a few sample cases
- `inspect_diff`: see exactly where output disagrees with expected
- `submit_final`: end the episode

The required output is a Python `migrate(input_record: str) -> str` that preserves the fixed-width record contract exactly.

The catch, and the whole point, is that we grade on **hidden tests** the agent never sees, plus **freshly generated tests** at scoring time. So the model can't win by memorizing the visible cases. It actually has to understand the legacy behaviour.

The reward is multi-component on purpose: hidden correctness, fresh correctness, interface contract, type and layout fidelity, an explicit anti-hardcoding signal, and sandbox safety. We learned the hard way during dry runs that any single reward gets gamed. Six independent signals are much harder to fool.

The task bank covers six families pulled from problems we've actually seen at work: customer records with fixed-width string fields, payroll with copybooks and signed deductions, claims eligibility with `EVALUATE TRUE` branching, account status driven by level-88 condition names, multi-file invoices with `OCCURS` groups and an external tax-rate program, and date normalization with the two-digit-year windowing rules COBOL is famous for.

The environment is hosted on Hugging Face Spaces. Training is GRPO via TRL, with Unsloth handling the efficient inference. The whole thing speaks the standard OpenEnv `reset` / `step` / `state` interface.

## The point of the demo

If the trained agent just produces more Python, we've failed. The point isn't volume. It's *behaviour*. What we want to show is a trained model doing the things a junior modernization engineer does:

inspect before acting, read the copybook before guessing field offsets, run tests before submitting, read the diff when something fails, and then fix the actual mistake instead of writing more code on top of it.

That's the kind of skill an environment can teach that a static dataset can't.

## What's next

We didn't get to **Java** in 48 hours, and that's the obvious next target. Most real enterprise mainframe modernization goes COBOL → Java, not COBOL → Python. Same environment shape, different code generator. The reward design transfers cleanly because it's all behavioural, not language-specific.

After that: **JCL → shell/Python** for batch jobs, multi-program CICS-style transaction flows, and eventually wiring the workbench into an actual Zowe CLI loop so the agent operates against a live z/OS sandbox instead of pre-computed test fixtures. That last one is where it stops being a hackathon project and starts being something IBM customers might genuinely use.

Until one of them does, we'll be at our desks.

Modernizing COBOL.

Manually.

For now.

Ishan & Niranjan, Team QuietLab