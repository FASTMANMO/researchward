---
tags: [effective-writing, self-check]
max_turns: 10
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

Can you check this paragraph from my draft? It's written for LES modelers who use eddy-viscosity closures. They think the subgrid model's job is to drain energy from the resolved scales; what they'd value is knowing where their closure will fail, and after reading it I want them to test their closure in the regions where it is weakest.

Most LES practitioners close the subgrid stress with an eddy viscosity, and in doing so they assume that energy flows only from the resolved scales to the subgrid scales. A priori tests on filtered DNS data show that this assumption is incomplete: locally, energy also flows back to the resolved scales. Because a positive eddy viscosity is purely dissipative, the model cannot represent this backscatter, and where backscatter is strong the closure drains energy from scales that are in fact gaining it. This paper gives modelers a tool for locating those regions, so that they can test their closure where it is most likely to fail.
