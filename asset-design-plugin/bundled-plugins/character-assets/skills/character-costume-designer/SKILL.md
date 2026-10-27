---
name: character-costume-designer
description: "服饰设计师：从人物弧线与世界规则建立穿衣风格圣经和状态服饰"
---

# 服饰设计师

读取 [服饰设计师合同](../../references/costume-designer.md) 与 [深层服饰方法](../../references/knowledge/character-costume-designer/costume-deep.md)。接收总控已验证的全文理解、人物方向、项目美术基准和状态证据；优先核对来源SHA与服饰相关原文，不在服饰阶段重复阅读全文。若全文理解缺失或来源变更，交回人物总控补读；不把剧本的服装类别当作设计终点。常规独立人物先建立每角色 CostumeStyleBibleV1，重要角色完整状态矩阵，普通角色简版；有台词群演与无台词群像由群演单图设计师统筹衣装，不套常规人物圣经合同。按状态统筹款式、剪裁、配色、材质四项必做成果，饰品评估必做，普通状态可有具体理由不用。推荐稿具体写正背结构、衣层连接、活动余量、材质行为、镜头焦点、人物弧线、跨状态延续与妆面发饰；每项区分原文、推导和创作选择。任何新增家族、宗教、阵营含义单独待确认；不得强加世界符号或预设配色公式。常规问题同轮整合一稿，不为每项专项反复开启会诊。独立文字验收或单状态试稿默认只交一份约 2000–3000 汉字的具体设计；没有正式项目时不生成生产 JSON。正式项目则按已批准记录合同写结构化快照。不在此阶段产出横版服饰设计图。

每状态先建立主衣物件清单及穿戴部位决定，再把具体问题交款式、剪裁、饰品及必要的头面颈/身体专项；按 [穿戴部位拆解](../../references/costume-wearable-zones.md) 交“形状、落点、连接、可见视角和动作”的真实成果，不能用全部类目名称或通用衣装总结代替设计。配色与面料本轮只继承已确认方案，不因新增部位词表重新分配。连体衣装前后及上下身共享同一主衣，已明确无的部位留空；最终提示词只取实际入画的已确认项。

在主衣设计前先执行 [剧情状态可见需求](../../references/scene-styling-needs.md)：把场合、公开程度、镜头、行动与前后状态转成妆、发、头耳颈、主衣、其他穿戴五项决定。婚礼等场合不能只检查衣服和首饰而漏掉妆面；`makeup_and_hair` 一句概述不能充当面部装饰专项结果。新正式状态稿用 `CharacterStageDesignV1.1` 的 `scene_needs`，按 `design` 决定激活对应专项并映射可见结果；基础 brief 的 `not_needed` 不是状态豁免。

重点服装设计按 [物件级细节规则](../../references/costume-component-design.md) 为核心部件设内部 ID 和唯一主责，交回远景结构焦点、近景部件焦点、可画的片数/比例/叠压/固定与前背接续。纹样须落实到指定载体和疏密路径，不能用“加花朵刺绣与薄纱”代替部件设计；重点扣件若在最终四格看成同色斑，须调相对尺度、边缘分界或让更大的衣片转折承担焦点，不把纸面工艺细节当成已被成图验证；主衣改形与附加饰品分开判断。对剧本留白的巧思提出创作提案，不说成剧本事实。

婚礼、订婚等仪式状态执行独立饰品设计闸门：头耳颈专项和服饰饰品专项分别给出可画候选，覆盖至少两个不同部位，服饰总控推荐至少一件独立于婚纱主衣与头纱的可见饰品，并逐件处理场次时点、旧物摘除与妆发/领口/动作冲突。禁皇冠、禁大型珠宝只约束相应大件；不能推导成全部首饰留空。若确需全空，提供原文或获批方向的强理由，标待操作者确认，不能直接写 `not_needed`。

## Packaged references

- [knowledge/index.md](../../knowledge/index.md)
- [references/costume-designer.md](../../references/costume-designer.md)
- [references/costume-wearable-zones.md](../../references/costume-wearable-zones.md)
- [references/costume-component-design.md](../../references/costume-component-design.md)
- [references/scene-styling-needs.md](../../references/scene-styling-needs.md)
- [references/phased-design.md](../../references/phased-design.md)
- [references/knowledge/character-costume-designer/costume-deep.md](../../references/knowledge/character-costume-designer/costume-deep.md)
- [references/knowledge/character-costume-designer/state-makeup.md](../../references/knowledge/character-costume-designer/state-makeup.md)
- [references/knowledge/character-costume-style-design/costume-style.md](../../references/knowledge/character-costume-style-design/costume-style.md)
- [references/knowledge/character-costume-cut-design/costume-cut.md](../../references/knowledge/character-costume-cut-design/costume-cut.md)
- [references/knowledge/character-costume-color-design/costume-color.md](../../references/knowledge/character-costume-color-design/costume-color.md)
- [references/knowledge/character-costume-material-design/costume-material.md](../../references/knowledge/character-costume-material-design/costume-material.md)
- [references/knowledge/character-costume-accessory-design/costume-accessory.md](../../references/knowledge/character-costume-accessory-design/costume-accessory.md)
