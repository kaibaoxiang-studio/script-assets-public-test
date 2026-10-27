---
name: character-image-prompt
description: "把已批准设计转成 GPT Image 2.5 分阶段提示词"
---

# 图像提示词

先读 [知识索引](../../knowledge/index.md)，按情景只加载本轮需要的 reference。

读取 [出图规则](../../references/prompting.md) 与当前阶段规则。先检查当前阶段的设计依据是否具象：新项目读取对应阶段快照，旧项目读取整卡；空泛则回设计轮补细。按真实质感规则选择适量可见肌理和材料词。正式提示词使用本阶段已批准的设计依据及当前选定图片；新项目按 [阶段合同](../../references/phased-design.md) 的 design_basis 绑定快照。avatar preview 可引用冻结未批准草案，须明确候选用途，未转正不能作下游锚点。按画幅抽取主锚点，标注每张参考图的身份/服装/风格职责。背景也是设计维度：无明确批准时仅用无场景、无纹理的中性底色作核对背景；不得自行加入地点、建筑、地貌、天气或借光线描述暗示剧情场景。头像默认 3:4 竖版且每条提示词写明比例，只有操作者明确指定才覆盖；新分阶段项目默认一条推荐提示词，重要分歧再给备选；旧项目保留其候选合同；人形头像与表情以脸为主体，可取完整头部、双肩及上胸，不固定裁到锁骨以上；服装不入画用 face_only，上胸入画用对应白色背心，整组模式一致；新项目默认九宫格并写中文标签，16 格须有用户明确要求；全身图默认 9:16 竖版，每条提示词与验收项写明比例，穿对应白色背心、短裤并赤脚，头到双脚完整并留边界，逐条继承已批准身体快照（旧项目为设计卡）中的头身、肩胯与腿身关系并核对；常规独立人物九宫格和全身模卡批准后，每状态从已批准的穿衣风格圣经和服饰文字快照直接产出一张 9:16 竖版四格执行图：上正脸/45°半侧脸、下无头放大正面服装/完整背面。有指定台词的群演直接以 SpeakingExtraDesignV1 做同版式的一张 9:16 执行图，无前三张锚图。无台词群像按 GroupEnsembleDesignV1 出一张所有成员全身可见的图，人数和横向比例依剧本与辨识度确定；不得套四格。单图审查批准后直接打包。非人使用已批准替代布局。输出 CharacterPromptPackageV1 与检查点，经 CLI 合同校验后交操作者外部出图。

## Packaged references

- [knowledge/index.md](../../knowledge/index.md)
- [references/prompting.md](../../references/prompting.md)
- [references/model-card-baseline.md](../../references/model-card-baseline.md)
- [references/expression.md](../../references/expression.md)
- [references/execution-sheet.md](../../references/execution-sheet.md)
- [references/group-ensemble.md](../../references/group-ensemble.md)
- [references/costume-design-stage.md](../../references/costume-design-stage.md)
- [references/interfaces.md](../../references/interfaces.md)
- [references/phased-design.md](../../references/phased-design.md)
- [references/knowledge/character-costume-designer/state-makeup.md](../../references/knowledge/character-costume-designer/state-makeup.md)
- [references/design-detail-standard.md](../../references/design-detail-standard.md)
- [references/render-texture-standard.md](../../references/render-texture-standard.md)
- [references/knowledge/character-image-prompt/feature-focus-prompt.md](../../references/knowledge/character-image-prompt/feature-focus-prompt.md)
- [references/knowledge/character-image-prompt/hedgehog-2d3d.md](../../references/knowledge/character-image-prompt/hedgehog-2d3d.md)
- [references/knowledge/character-image-prompt/hedgehog-general-image-skill.md](../../references/knowledge/character-image-prompt/hedgehog-general-image-skill.md)
- [references/knowledge/character-image-prompt/anti-stereotype-texture.md](../../references/knowledge/character-image-prompt/anti-stereotype-texture.md)
