---
name: character-face-signature-design
description: "面部记忆点与锁骨以上饰品设计"
---

# 面部记忆点与锁骨以上饰品设计

读取 [专项交接](../../references/specialist-contract.md)、[群像差异化框架](../../references/differentiation-framework.md) 与本专项知识快照。先用已有结构识别，再考虑面部记号、发饰、耳饰和颈饰；写固定点与连续性，新增伤痕纹身必须待批准。读取总控的 DesignDirectionBriefV1、当前阶段任务、已有视觉基准与最近比较组；没有项目时可直接接人物材料，注明草案与材料范围。先回应任务目标、人物语境、约束和所需成果，默认一套推荐，仅重要分歧增加备选，每方案列至少两个部位、形状、位置/连接和依据明确的设计元素，供设计卡实际采纳；明确原文事实、合理推导、创作选择、制作核对点及与近邻的差异。把人物未写明的外观当作需要设计的空白；无须编造身世证明某种脸型。常规项可由总控同轮执行本 Skill 的规范并记录 inline 成果；独立会诊记录 independent 原始返回物。新特征仍是待审设计，不能自行批准。提案包含当前 variant_id；新独立提案提交 CharacterSpecialistProposalV1.2 JSON 与短 Markdown，执行 scripts/validate_specialist_proposal.py；旧 V1/V1.1 仍可回读；不调用生图。

剧本没写头耳颈饰品时，仍按 [头像命名与颗粒度规则](../../references/avatar-identity-granularity.md) 和新增方法快照检查世界、功能、个人选择及资源锚点；先判断人物是否已足够可识别，再提出饰品或明确留空。虚构的遗物、宗教或身份故事必须标为待审选择。

进入服饰状态时按 [穿戴部位拆解](../../references/costume-wearable-zones.md) 分别判断头戴、发饰、耳饰、面部穿戴和颈饰；每件说清与已批发际、脸、耳、领口的固定和遮挡，注明本状态佩戴起止。面部彩绘属于面部装饰专项，腰部以下的穿戴归服饰饰品专项；不因 17、18、20 号清单存在就自动加物件。

状态判断先接收 [可见需求](../../references/scene-styling-needs.md) 的场合、镜头和禁令准确对象；基础头像不佩戴不等于仪式状态留空。发型专项负责发束本体，本专项给头纱梳、发饰、耳饰、颈饰的独立件、固定、遮挡和场次时点。

婚礼等仪式状态不能把“已有头纱”当作发饰、耳饰和颈饰全部审完：至少对两个可见部位交具体候选，写体量、固定点、正面/45°/背面可见性及与头纱、发束和领口的冲突；再提出有理由的采用组合。旧项链已摘除只禁止那件旧物在后续状态复现，不禁止新颈饰候选；禁大型珠宝也不禁止小型饰品。

头纱梳、发夹和其他被选为关键记忆点的头耳颈小件按 [物件级细节规则](../../references/costume-component-design.md) 写独立部件、尺寸、背板/齿/扣、佩戴路径与头发遮挡；正面花形不能在45°和背面变成另一枚悬浮装饰。

## Packaged references

- [knowledge/index.md](../../knowledge/index.md)
- [references/specialist-contract.md](../../references/specialist-contract.md)
- [references/differentiation-framework.md](../../references/differentiation-framework.md)
- [references/design-detail-standard.md](../../references/design-detail-standard.md)
- [references/knowledge/character-face-signature-design/face-memory.md](../../references/knowledge/character-face-signature-design/face-memory.md)
- [references/costume-wearable-zones.md](../../references/costume-wearable-zones.md)
- [references/costume-component-design.md](../../references/costume-component-design.md)
- [references/scene-styling-needs.md](../../references/scene-styling-needs.md)

Read [avatar-head-ear-neck-16](../../references/knowledge/character-face-signature-design/avatar-head-ear-neck-16.md) when this capability needs the supplied knowledge.

Read [wearable-headwear-17](../../references/knowledge/character-face-signature-design/wearable-headwear-17.md) when this capability needs the supplied knowledge.

Read [wearable-face-jewelry-18](../../references/knowledge/character-face-signature-design/wearable-face-jewelry-18.md) when this capability needs the supplied knowledge.

Read [wearable-neck-20](../../references/knowledge/character-face-signature-design/wearable-neck-20.md) when this capability needs the supplied knowledge.
