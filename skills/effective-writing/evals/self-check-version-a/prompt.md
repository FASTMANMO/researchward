---
tags: [effective-writing, self-check]
max_turns: 10
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

Can you check this paragraph from my draft? It's written for LES modelers who use eddy-viscosity closures. They think the subgrid model's job is to drain energy from the resolved scales; what they'd value is knowing where their closure will fail, and after reading it I want them to test their closure in the regions where it is weakest.

This section discusses subgrid-scale modeling in large-eddy simulation (LES) of turbulent flows. Subgrid-scale models represent the effect of the unresolved scales on the resolved field. The Smagorinsky model, which relates the subgrid stress to the resolved strain rate through an eddy viscosity, is widely used. In this work, the energy transfer between resolved and subgrid scales is analyzed using filtered DNS data.
