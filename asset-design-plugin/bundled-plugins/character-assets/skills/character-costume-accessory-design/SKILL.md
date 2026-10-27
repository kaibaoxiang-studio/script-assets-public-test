---
name: character-costume-accessory-design
description: "服饰附加物设计：肩胸背、臂手腕腰腿的装饰与挂载"
---

# 服饰饰品设计：衣身、腰、手与随身穿戴物

读取 [专项交接](../../references/specialist-contract.md)、[群像差异化框架](../../references/differentiation-framework.md) 与本专项知识快照。处理锁骨以下饰品的功能、固定、重量与道具 ID；跨锁骨物件与面部饰品专项只指定一个主责。读取总控的 DesignDirectionBriefV1、当前阶段任务、已有视觉基准与最近比较组；没有项目时可直接接人物材料，注明草案与材料范围。先回应任务目标、人物语境、约束和所需成果，默认一套推荐，仅重要分歧增加备选，每方案列至少两个部位、形状、位置/连接和依据明确的设计元素，供设计卡实际采纳；明确原文事实、合理推导、创作选择、制作核对点及与近邻的差异。把人物未写明的外观当作需要设计的空白；无须编造身世证明某种脸型。常规项可由总控同轮执行本 Skill 的规范并记录 inline 成果；独立会诊记录 independent 原始返回物。新特征仍是待审设计，不能自行批准。提案包含当前 variant_id；新独立提案提交 CharacterSpecialistProposalV1.2 JSON 与短 Markdown，执行 scripts/validate_specialist_proposal.py；旧 V1/V1.1 仍可回读；不调用生图。

按 [穿戴部位拆解](../../references/costume-wearable-zones.md) 在主衣定形后逐项判断衣身附着装饰、独立肩件、胸腹挂载、上臂/前臂、手指/手掌/腕、腰件/腰挂、背部/背负、腿件与膝胫护具；只选有场景或设计任务的物件，明确无也是完整结果。有物件时交左右、固定点、尺度、承重/晃动、遮挡、穿脱与道具 ID。耳钉和颈饰交头耳颈专项，袖子、腰省和后片交剪裁专项；不能把另一角色的手链或项链写进本人物状态。

婚礼等仪式场景本身就是明确设计任务。至少检查手指/手腕、腰部独立件和衣身附着件，交一件以上可画候选及不采用其他件的理由；戒指先查剧本是否给出交换或佩戴时点，未写时只作待审候选，不把婚姻关系直接写成每个镜头都有戒指。旧手链已摘除只约束旧手链，不等于所有腕饰禁用。若没有独立件可采用，须说明原文或获批方向的强理由并交总控待确认，不能以主衣同布腰带完成本专项。

若腰扣、胸饰、头饰接口或可拆件承担重点造型，按 [物件级细节规则](../../references/costume-component-design.md) 像小道具一样写部件数、外轮廓、相对尺寸、背板/袢/扣、承力和拆装路径；平面刺绣不是立体别针。与剪裁专项共同核对挂点所在衣片，不能让饰件或外裙只在正面凭空悬浮。

## Packaged references

- [knowledge/index.md](../../knowledge/index.md)
- [references/specialist-contract.md](../../references/specialist-contract.md)
- [references/differentiation-framework.md](../../references/differentiation-framework.md)
- [references/design-detail-standard.md](../../references/design-detail-standard.md)
- [references/knowledge/character-costume-accessory-design/costume-accessory.md](../../references/knowledge/character-costume-accessory-design/costume-accessory.md)
- [references/knowledge/character-costume-designer/costume-deep.md](../../references/knowledge/character-costume-designer/costume-deep.md)
- [references/costume-wearable-zones.md](../../references/costume-wearable-zones.md)
- [references/costume-component-design.md](../../references/costume-component-design.md)

Read [wearable-hand-wrist-22](../../references/knowledge/character-costume-accessory-design/wearable-hand-wrist-22.md) when this capability needs the supplied knowledge.

Read [wearable-waist-23](../../references/knowledge/character-costume-accessory-design/wearable-waist-23.md) when this capability needs the supplied knowledge.

Read [wearable-arm-24](../../references/knowledge/character-costume-accessory-design/wearable-arm-24.md) when this capability needs the supplied knowledge.

Read [wearable-back-25](../../references/knowledge/character-costume-accessory-design/wearable-back-25.md) when this capability needs the supplied knowledge.

Read [wearable-leg-mount-28](../../references/knowledge/character-costume-accessory-design/wearable-leg-mount-28.md) when this capability needs the supplied knowledge.
