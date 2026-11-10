---
tags: [effective-writing, dissect]
max_turns: 10
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

I came across this paragraph in a published LES paper and it reads really well. Can you break down why, using the effective-writing criteria? Its readers are LES modelers who use eddy-viscosity closures.

Most LES practitioners close the subgrid stress with an eddy viscosity, and in doing so they assume that energy flows only from the resolved scales to the subgrid scales. A priori tests on filtered DNS data show that this assumption is incomplete: locally, energy also flows back to the resolved scales. Because a positive eddy viscosity is purely dissipative, the model cannot represent this backscatter, and where backscatter is strong the closure drains energy from scales that are in fact gaining it. This paper gives modelers a tool for locating those regions, so that they can test their closure where it is most likely to fail.
