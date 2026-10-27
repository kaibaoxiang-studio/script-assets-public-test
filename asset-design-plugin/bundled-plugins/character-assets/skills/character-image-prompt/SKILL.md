---
name: character-image-prompt
description: "把已批准设计转成 GPT Image 2.5 分阶段提示词"
---

# 图像提示词

先读 [知识索引](../../knowledge/index.md)，按情景只加载本轮需要的 reference。

读取 [出图规则](../../references/prompting.md) 与当前阶段规则。先检查当前阶段的设计依据是否具象：新项目读取对应阶段快照，旧项目读取整卡；空泛则回设计轮补细。按真实质感规则选择适量可见肌理和材料词。正式提示词使用本阶段已批准的设计依据及当前选定图片；新项目按 [阶段合同](../../references/phased-design.md) 的 design_basis 绑定快照。avatar preview 可引用冻结未批准草案，须明确候选用途，未转正不能作下游锚点。按画幅抽取主锚点，标注每张参考图的身份/服装/风格职责。背景也是设计维度：无明确批准时仅用无场景、无纹理的中性底色作核对背景；不得自行加入地点、建筑、地貌、天气或借光线描述暗示剧情场景。头像默认 3:4 竖版且每条提示词写明比例，只有操作者明确指定才覆盖；新分阶段项目默认一条推荐提示词，重要分歧再给备选；旧项目保留其候选合同；人形头像与表情以脸为主体，可取完整头部、双肩及上胸，不固定裁到锁骨以上；服装不入画用 face_only，上胸入画用对应白色背心，整组模式一致；新项目默认九宫格并写中文标签，16 格须有用户明确要求；全身图默认 9:16 竖版，每条提示词与验收项写明比例，穿对应白色背心、短裤并赤脚，头到双脚完整并留边界，逐条继承已批准身体快照（旧项目为设计卡）中的头身、肩胯与腿身关系并核对；常规独立人物九宫格和全身模卡批准后，每状态从已批准的穿衣风格圣经和服饰文字快照直接产出一张 9:16 竖版四格执行图：上正脸/45°半侧脸、下无头放大正面服装/完整背面。有指定台词的群演直接以 SpeakingExtraDesignV1 做同版式的一张 9:16 执行图，无前三张锚图。无台词群像按 GroupEnsembleDesignV1 出一张所有成员全身可见的图，人数和横向比例依剧本与辨识度确定；不得套四格。单图审查批准后直接打包。非人使用已批准替代布局。输出 CharacterPromptPackageV1 与检查点，经 CLI 合同校验后交操作者外部出图。

人形基础头像把已确认的名称与骨点、五官、发际发流、肤质和妆饰按 [头像命名与颗粒度规则](../../references/avatar-identity-granularity.md) 转为无板块标题的连续提示词正文；正常头像尺度不主动要求逐根额前发丝或全脸可见毛孔、绒毛。

完整头像请求须把眉、眼、可见耳、鼻、唇分别核对，显式承接稳定标记与头耳颈饰的存在或留空决定；本能力先交文字，不把省略部位或图像模型随机补出的部位当作已设计。用户另外要求生成预览时，由角色主控在文字展示之后按当前可用工具处理，预览标未批准。

正式服饰执行图按 [穿戴部位拆解](../../references/costume-wearable-zones.md) 从已确认状态稿提取可见件：连体主衣只描述一次，按领肩胸腰、下摆、背部和鞋的画面顺序细化；头面颈只用当前状态已确认物件。内部部位清单的“明确无/不适用”不逐项塞进提示词，也不凭词表新增装饰。配色与面料沿当前已批方案，确保上右45°和下右背面沿用相同开合、挂载、鞋与耳饰。

新状态稿先读 [剧情状态可见需求](../../references/scene-styling-needs.md) 的五项决定；凡 `design` 的 `prompt_cues` 逐字进入最终正文，并在验收项覆盖该项。妆面不可压缩为“自然肤质”，必须把已设计的底妆、眉眼、颊、唇中当前可见的具体颜色、边界和强度放入上方两格；发型与头耳颈饰同样逐件承接。若状态稿只有旧版概述、缺少需求或实际设计，退回状态设计，不在提示词里临时编妆。服装关键部件的轮廓与连接 cue 均需保留；按最终格位尺寸判断能否被看见，微小同色部件需回设计稿调整尺度或分界，不能只堆更多微纹样词。

婚礼等仪式状态须核对已选饰品是否逐件进入相应格位；旧执行图用作身份或版式参考时，其饰品缺席不是保留约束。按原文的准确范围写禁令，不能把“禁皇冠、大型珠宝”改写成全体饰品缺席；未确认的戒指候选不可偷偷加进正式提示词。

重点服装按 [物件级细节规则](../../references/costume-component-design.md) 从已选部件稿提取轮廓、起止、片数/相对尺度、叠压、固定、纹样路径与正背接续，不能把“腰扣锁住翻页式外裙”压缩成“精致腰饰和层叠薄纱”。用户只完成半份设计时，预览也保持原 9:16 竖版 2×2 执行图，除非用户明确改版式；提示词先交完整可复制正文，再用同一正文生成预览，不临时追加另一套未展示的设计。

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
- [references/costume-wearable-zones.md](../../references/costume-wearable-zones.md)
- [references/costume-component-design.md](../../references/costume-component-design.md)
- [references/scene-styling-needs.md](../../references/scene-styling-needs.md)
- [references/render-texture-standard.md](../../references/render-texture-standard.md)
- [references/knowledge/character-image-prompt/feature-focus-prompt.md](../../references/knowledge/character-image-prompt/feature-focus-prompt.md)
- [references/knowledge/character-image-prompt/hedgehog-2d3d.md](../../references/knowledge/character-image-prompt/hedgehog-2d3d.md)
- [references/knowledge/character-image-prompt/hedgehog-general-image-skill.md](../../references/knowledge/character-image-prompt/hedgehog-general-image-skill.md)
- [references/knowledge/character-image-prompt/anti-stereotype-texture.md](../../references/knowledge/character-image-prompt/anti-stereotype-texture.md)
