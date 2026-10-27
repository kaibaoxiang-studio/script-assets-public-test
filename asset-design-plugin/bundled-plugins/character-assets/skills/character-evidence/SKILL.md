---
name: character-evidence
description: "核对剧本事实、资产表与场记来源并列冲突"
---

# 角色证据核对

先读 [知识索引](../../knowledge/index.md)，按情景只加载本轮需要的 reference。

读取 [证据规则](../../references/evidence.md) 和项目来源文件。以标准剧本原文为事实基准，资产表只供 ID/层级/状态索引，场记作可选镜头与情绪核对。逐条分类原文事实、保守推导、未批准提案、已批准选择；每条事实附 source_refs。若三份输入冲突，给出双方位置和受影响角色/字段，返回待裁决，不替用户改写。如受上游改版影响，列影响角色与全剧视觉基准是否需重审，再用 CLI 记录影响决议。

## Packaged references

- [knowledge/index.md](../../knowledge/index.md)
- [references/evidence.md](../../references/evidence.md)
- [references/interfaces.md](../../references/interfaces.md)
