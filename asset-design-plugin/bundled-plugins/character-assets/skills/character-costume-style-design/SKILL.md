---
name: character-costume-style-design
description: "服饰款式设计：主衣、外套、内层、下装、袜鞋品类与穿搭层次"
---

# 服饰款式设计：衣装品类、长度和层次

读取 [专项交接](../../references/specialist-contract.md)、[群像差异化框架](../../references/differentiation-framework.md) 与本专项知识快照。从世界、场合、职业与行动决定衣装品类和整体轮廓；不侵占剪裁、配色、材质与饰品职责。读取总控的 DesignDirectionBriefV1、当前阶段任务、已有视觉基准与最近比较组；没有项目时可直接接人物材料，注明草案与材料范围。先回应任务目标、人物语境、约束和所需成果，默认一套推荐，仅重要分歧增加备选，每方案列至少两个部位、形状、位置/连接和依据明确的设计元素，供设计卡实际采纳；明确原文事实、合理推导、创作选择、制作核对点及与近邻的差异。把人物未写明的外观当作需要设计的空白；无须编造身世证明某种脸型。常规项可由总控同轮执行本 Skill 的规范并记录 inline 成果；独立会诊记录 independent 原始返回物。新特征仍是待审设计，不能自行批准。提案包含当前 variant_id；新独立提案提交 CharacterSpecialistProposalV1.2 JSON 与短 Markdown，执行 scripts/validate_specialist_proposal.py；旧 V1/V1.1 仍可回读；不调用生图。

服饰状态任务按 [穿戴部位拆解](../../references/costume-wearable-zones.md) 先列主衣，再逐件确定主体上装/连体上身、外套、可见中层与贴身层、主体下装/连体裙身、可见袜品和鞋履品类。给每件衣物写覆盖范围、相邻衣层、长度端点与穿法；连衣裙上下身使用同一物件，不能重复生成两套服装。未选外套、袜或内搭可明确留空；鞋履不能只报“低跟鞋”，须交鞋头、开口、跟底和与脚/裙袜的关系供剪裁深化。配色面料沿已批准方案。

重点服装按 [物件级细节规则](../../references/costume-component-design.md) 先定远景能识别的主体与外层关系，再定一处中近景可见的部件做法；写清外层起止、叠压方向、前背覆盖和穿法，不把更多花纹当成廓形创新。

## Packaged references

- [knowledge/index.md](../../knowledge/index.md)
- [references/specialist-contract.md](../../references/specialist-contract.md)
- [references/differentiation-framework.md](../../references/differentiation-framework.md)
- [references/design-detail-standard.md](../../references/design-detail-standard.md)
- [references/knowledge/character-costume-style-design/costume-style.md](../../references/knowledge/character-costume-style-design/costume-style.md)
- [references/knowledge/character-costume-designer/costume-deep.md](../../references/knowledge/character-costume-designer/costume-deep.md)
- [references/costume-wearable-zones.md](../../references/costume-wearable-zones.md)
- [references/costume-component-design.md](../../references/costume-component-design.md)

Read [wearable-upper-21](../../references/knowledge/character-costume-style-design/wearable-upper-21.md) when this capability needs the supplied knowledge.

Read [wearable-close-chest-26](../../references/knowledge/character-costume-style-design/wearable-close-chest-26.md) when this capability needs the supplied knowledge.

Read [wearable-lower-main-27](../../references/knowledge/character-costume-style-design/wearable-lower-main-27.md) when this capability needs the supplied knowledge.

Read [wearable-knee-sock-29](../../references/knowledge/character-costume-style-design/wearable-knee-sock-29.md) when this capability needs the supplied knowledge.

Read [wearable-footwear-30](../../references/knowledge/character-costume-style-design/wearable-footwear-30.md) when this capability needs the supplied knowledge.
