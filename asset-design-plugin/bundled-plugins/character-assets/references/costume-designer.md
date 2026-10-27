# 服饰设计师：人物总控之后的必经环节 v0.2.6

## 输入与责任

读取来源版本一致的 `ScriptContextV1`、目标人物 `DesignDirectionBriefV1`、项目视觉基准、身份与身体快照、资产表登记的服饰状态，以及相关剧本场次。总控已解读全文；服饰设计师核对来源 SHA 并追溯与衣装有关的原文，不重复阅读全文。若上下文缺失或版本变化，交回总控补读。不能用“剧本只写婚纱”停止设计。服装类别、剧情作用及明确禁令为硬约束；剪裁、层次、纹样、穿着方式与镜头记忆点由设计师形成可审阅创作选择。

先写一句人物穿衣命题：人物试图呈现什么，与其真实处境有什么张力。随后制定 `CostumeStyleBibleV1`，每角色共用。资产表主角和重要角色必须用 `tier:full` 和登记状态完整 `state_matrix`；普通角色用 `tier:compact`，仍须具体廓形、剪裁、色材语法与记忆锚点；普通群像可用 `tier:group`，但每人还需个体差别。字段：`schema_version,character_id,variant_id:base,parent_refs,tier,wearing_thesis,world_translation,signature_silhouette,cut_grammar,palette_grammar,material_grammar,recognition_anchor,wearing_habits,state_logic,physical_and_camera_rules,state_matrix(full),new_lore_policy,unresolved`。`parent_refs` 绑定获批 brief、identity 和 body SHA。家族、宗教、阵营含义属于新增设定，须单独待确认；普通结构选择随整稿审。

## 每状态设计

独立文字验收和单状态试稿默认只交一份约 2000–3000 汉字的具象设计，不提前制造生产 JSON、审批文件或全员矩阵的重复长文；正式项目才按下列合同提交结构化记录。重点角色的状态矩阵可用短句覆盖其余状态，把篇幅留给本次状态的剪裁、材料和动作。

对每个资产表状态写 `CharacterStageDesignV1(scope:costume)`，其 `parent_refs` 在原有 brief、identity、body 外加入 `costume-bible:CHR:base` 当前 SHA。`payload.costume_direction` 至少有：`script_requirement`、`narrative_function`、`front_structure`、`back_structure`、`cut_and_fastening`、`layering`、`color_placement`、`material_behavior`、`recognition_focus`、`mobility_and_camera`、`state_continuity`、`makeup_and_hair`、`evidence_status`、`script_refs`。`payload.costume` 与 `visual_details.costume` 保持本轮原有合同。正背结构写具体部位、形状、尺寸/比例或穿法；布料写厚薄、光泽、垂坠和动作表现；妆造只改施加层，不改获批骨相。

统筹五专项：

| 专项 | 交付到衣装的实际成果 |
| --- | --- |
| 款式 | 品类内的廓形、衣长、层次、穿法与身份关系 |
| 剪裁 | 领肩袖腰摆、拼片、缝/扣/拉链、前背连接和活动余量 |
| 配色 | 实际部位的明度/色相/面积关系，和同框角色区分 |
| 材质 | 各衣层表面、厚度、重量、反射、垂坠与磨损逻辑 |
| 饰品 | 功能、固定点与镜头作用；不用时给出具体理由 |

前四项必须在 `specialist_execution` 留真实的 inline 规则、知识 SHA 和映射到 `costume_direction.*` 或 `visual_details.costume.*` 的可见成果，或独立会诊提案和已采纳元素。不能只打标签。饰品可 `not_needed`。复杂跨域问题可独立会诊，常规问题设计师实际执行专项规范并记录结果。风格圣经不取代逐状态文本设计。

## 审查与出图

检验剧本约束、人物弧线、正背、剪裁连接、动作、拍摄视角、材质物理和近邻角色差异。对于“白色婚纱”，要守住婚纱与白色，但必须给出这个人物独有的结构与穿法；不要自动指定 A 字裙、泡泡袖或首饰，也不要自动禁止所有配饰。一个到两个主要锚点足够；符号、纹样、色彩公式和叠穿都是可选方法。

用户批准文字快照后，合成设计卡，再生成**一张** `execution` 正式图：9:16 竖版 2×2；上方正面脸与 45° 脸，下方放大无头正面服装与头鞋完整背面。逐状态一张、一次审查批准、直接打包。不要制作新项目的 `costume_design` 横版双视图。已有 pipeline 2/1 仍按各自原链路；`upgrade-pipeline` 用于无已批准服饰或执行图的 pipeline 2 项目，保留获批头像、九宫格、全身模卡。

深层方法见 `references/knowledge/character-costume-designer/costume-deep.md`。学术文献只解释服饰社会语境、视觉显著性和布料物理，不能把课程比例说成经过验证的定律。
