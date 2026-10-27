# 角色专项执行与交接 v0.2.5

专项服务于 [人物总控](director-understanding.md) 已建立的人物理解和设计意图，不从职业标签独立重造人物。主控负责定位、路由、焦点和整合，专项负责本领域结构方案；任何执行方式都不自行批准项目。

## 输入和执行方式

接受 `project_root`，或独立提供 `sources` 路径数组、`script_context_path`、`direction_brief_path` 和当前任务。独立剧本/小传可以先分析，说明阅读范围；无项目且未指定阶段默认identity/头像，只做当前首稿和关键路由，不先要求生产JSON或身体衣装详设。先读用户全文/复用有效context，再按任务加载必要规范，references是目录而非全读清单；正式登记按项目合同补记录。输入含人物言行证据、弧线和观众信息、已批准锚点、设计意图、生活行动条件、比较组、可创作范围及待解矛盾。可以读现有相关知识全文，不要求每次重读全部；知识不是原文事实。

- **inline**：常规问题由主控真实加载并执行专项规范。阶段 `specialist_execution` 记录 `mode:inline`、`decision`、`knowledge_refs[{path,sha256}]`、`rules_applied[]`、`results[{field,visible_result,basis,evidence_status}]`。路径相对插件根，必须对应实际知识快照；进入项目后复制到 knowledge-snapshots/sha 并保留收据，后续插件升级不因旧知识哈希改变而使历史项目失效；规则写具体采用方法，结果指向 `visual_details.face.contour` 等真实字段。`evidence_status` 为 `script_fact|inference|creative_choice`。不用伪造独立专家提案证明主控做过设计。
- **independent**：跨专项冲突、重要身份/信息取舍、复杂形体工艺或反复失败时真实委派会诊。保存返回提案，在阶段记录 `mode:independent`、`decision`、`proposal_ref`、`proposal_sha256`、`selected_option_id`、`applied_elements[{field,element_index}]`；目标角色、状态与专项匹配。仅写已调用、自己编造外部返回物或只记录名称不成立。
- **not_needed**：本阶段不适用或已有充分决定，写具体 `decision`。尚待身体或服饰阶段深化属于 `defer` 规划和 `deferred_dimensions`，不伪装成永不需要。

方向稿的 `specialist_plan` 覆盖十三项，状态为 `inline|independent|defer|not_needed`；inline/independent 项另有 `task{objective,character_context,constraints[],expected_result}`，把人物理解和设计意图变成具体委派目标。阶段只记录本阶段实际执行的项；从 defer 激活时在 work 写同结构 task 和 activation_reason，更改既定执行方式须 execution_change_reason，原 not_needed 不能悄悄激活；唯一例外是新服饰状态稿按 [剧情状态可见需求](scene-styling-needs.md) 为妆、发、头耳颈或其他穿戴提供具体 `work.task` 和 `state_activation_reason`，只改变本场施加层，不改基础身份方向。其他领域仍先修订方向稿。十三项不是十三轮询问或十三次独立会诊。复杂性看真实矛盾与返工风险，不按字段数量机械判断。

## 独立提案

当前新提案为 `CharacterSpecialistProposalV1.2`。保存 UTF-8 JSON 和简短可读 Markdown，至少有 `schema_version`、`specialist`、`character_id`、`variant_id`、`scope`、`execution_mode:inline|independent`、`task{objective,character_context,constraints[],expected_result}`、`knowledge_refs[{path,sha256}]`、`facts[{text,source_refs}]`、`options[]`、`recommended_option_id`、`unresolved[]` 和 `not_applicable_reason`。

默认一个推荐方案；确有重要取舍时给备选，`options` 为 1–3。每项保留 `id`、`visible_design`、`rationale`、`comparison_difference`、`production_check`、至少两条 `design_elements[{part,visible_feature,placement_or_structure,basis,evidence_status}]`。描述部位、形态、比例/连接、来源性质和实际使用约束，不能只写清秀、利落或自然。零基 `element_index` 指向被选方案元素。没有首饰、无特殊痕迹、衣装简洁可以是完整决定，不因交接而强加物件。

执行 `python scripts/validate_specialist_proposal.py --file /absolute/artifact_dir/proposal.json`。主控复制原样 JSON 到项目 `drafts/specialists/` 并记录 SHA；V1.2独立提案的知识路径/SHA同inline真实校验并归档knowledge-snapshots，应用到visual_details的元素必须属于该专项领域（例如发型提案不能映射脸部）；V1.1保持旧兼容。校验只验证合同和真实文件，人物理解、语义采纳及美感仍需审阅。推荐不等于批准，独立专家也不能覆盖原文、已批准身份或观众信息策略。

## 整合与回溯

每个提案说明解决了哪个人物问题，输出哪些可画结果、怎样与近邻区别、对动作和工艺的影响。总控裁决同一部位冲突，为跨头颈和衣身的同一饰物指定唯一主责；保持安静区，不把各专项焦点全部叠加。阶段稿将成果转为连贯人设文字，JSON 与 Markdown 同样具体。

群像审查继续使用 `CharacterCastDifferentiationReviewV1`，区分文本证据与实图，列比较组、五轴、具体混淆、真实度疑点、未做检查和未实施建议，不改批准状态。

历史 V1/V1.1 提案与 `CharacterSpecialistRouteV1`、旧卡 used/not_needed 交接继续回读；其原有选项数量、哈希和字段映射门槛保留。新 V2.5 阶段流程采用上述执行证据，不能把旧版必须独立提案的规则施加给新 inline 任务。
