# 接口与文件契约 v0.2.6.2

## 群演单图扩展

`plan.asset_mode=speaking_extra` 的有台词群演先获批 `SpeakingExtraDesignV1`，字段和命令见[群演单图合同](group-ensemble.md)。每状态只用一张 9:16 四格 `execution` 图，`design_basis.records` 只绑定 `extra-design:角色ID:状态ID`，`anchor_images:{}`；审图批准后打包 `CharacterSpeakingExtraPackV1`。头像、九宫格、模卡和穿衣圣经不作前置。

`pipeline_version:3` 且 `plan.asset_mode=ensemble` 时，先提交并批准 `GroupEnsembleDesignV1`，字段和命令见[群像单图合同](group-ensemble.md)。正式提示词仍用 `CharacterPromptPackageV1` 的 `stage:execution`，但 `morphology:group`、`anchor_images:{}`、`layout.type:ensemble_lineup`、`layout.single_canvas:true`、`layout.full_body:true`、逐人 `ordered_slots`，`design_basis.records` 只绑定对应 `ensemble-design:角色ID:状态ID`。多人横版比例按人数与辨识度决定，单人 9:16。审图批准一次后打包 `CharacterEnsemblePackV1`。下文身份图前置仅适用于 `asset_mode=individual`；有台词群演沿用四格布局，无台词群像使用完整全身同画布布局。

## v0.2.6 / pipeline_version 3 接口覆盖

新项目默认 `pipeline_version:3`，图像阶段为 `avatar,expression,full_body,execution`；旧 v2 仍是五图、v1 四图。新增记录 `CostumeStyleBibleV1`，键 `costume-bible:CHR:base`，须绑定获批 brief/identity/body SHA，含完整穿衣规则与重点角色状态矩阵。每状态 `CharacterStageDesignV1(scope:costume)` 的 `parent_refs` 再引用当前风格圣经；`payload.costume_direction` 须写剧本约束、剧情作用、前后结构、裁剪闭合、衣层、色块、材料行为、视觉焦点、行动/镜头、状态延续、妆面发饰、来源性质与原文引用。款式、剪裁、配色、材质四专项必须有实际应用结果；饰品可有理由不用。`execution` 提示词 `design_basis` 含 brief、identity、body、costume-bible、当前状态 costume、合成 design-card；图片锚点只含 avatar/expression/full_body。人形四格图默认 9:16 竖版，`aspect_ratio`、每条提示词、验收项都写比例；改画幅须明确用户要求。`variant_name` 与资产表一致。逐状态只有一张执行图，批准一次后打包 `CharacterAssetPackV3`。`upgrade-pipeline` 用于无已批准服饰/执行图的 v2 项目，旧项目仍按原合同。下文 v2 五阶段字段只适用历史项目。


文件为 UTF-8 JSON，含 `schema_version`，角色/状态 ID 沿用资产表。`source_refs` 使用标准剧本位置、JSON 集场 ID 或保留的 `文件名:L行号`、`文件名:工作表!R行号`。合同校验不证明人物理解或画面质量。

## 输入与项目兼容

可以独立接剧本、片段或小传先分析；声明范围和来源。受管理的正式项目使用剧本、资产表，可选场记，或 `init --snapshot` 的 `AssetProjectSnapshotV1`。快照至少含 `project_id`、`sources.screenplay` 与 `sources.asset_table` 的 `{path,sha256}`；scene_log 可选。可选 `visual_bible` 为 `{path,sha256,approval:{operator,at,sha256}}`，相对路径基于快照所在目录。

`init --design-progression phased|complete` 新默认 phased；旧状态无字段按 complete。默认 phased 初始化为 v3 四图链路；显式 complete 初始化为历史 v2 五图模式。旧四阶段不自动升级。

## 项目基准与阅读

`ProjectVisualBibleV1` 含 `project_id`、`world_rules`、`style`、`evidence[{claim,source_refs}]`、`unresolved`。风格分媒介、写实度、时代、配色、材质和光线，区分原文约束与批准选择。

`CastPlanV2.characters` 覆盖全部角色 ID，至少 `id`、`design_distinction` 和 `recognition_axes{silhouette,face_structure,body_posture,hair_structure,costume_color}`；可附层级、剧情作用、关系、锚点、状态与来源。轻规划未知轴可待定；非人/群像写 `morphology:nonhuman|group` 并说明不适用项。五轴不是角色理解的替代品。

当前新流程新增：

- `ScriptContextV1`：`source_sha256`、`source_kind:screenplay|biography`、`read_units[{unit_id,sha256}]`、`synopsis`、`world_summary`、`narrative_structure`、`character_index[{character_id,name,role_in_story,arc_summary,relationships,evidence_unit_ids}]`、`unresolved`。read_units 必须匹配 `context-units` 输出全部单元与 SHA，character_index轻量覆盖全roster，后续逐人复用同源context。来源SHA/覆盖/结构完整且unresolved为空后自动ready，系统approval仅为 `system:context-contract-check`、scope `source-coverage-and-structure`，返回 `interpretation_confirmed:false`，无需增加用户审批。未决非空待复核，手动approve可选；人物解释在brief集中确认。
- `DesignDirectionBriefV1`：`asset_domain:character`、角色、base 状态、`context_sha256`、`understanding`、`design_thesis`、`visual_strategy:direct|contrast|concealed|mixed`、`recommended_direction`、`alternatives`、`delegated_dimensions`、十三项 `specialist_plan`、`unresolved`。understanding 为 `CharacterUnderstandingV1`，含 `role_in_story,core_motivation,central_tension,world_and_life,relationships,arc,evidence_unit_ids`。专项规划状态为 `inline|independent|defer|not_needed`，各写 reason；前两项还须 `task{objective,character_context,constraints[],expected_result}`。
- `CharacterStageDesignV1`：`character_id,variant_id,scope,parent_refs,payload,specialist_execution,deferred_dimensions,unresolved`。scope 为 identity/body/costume；字段分域、依据关系与命令见 [阶段设计](phased-design.md)。`parent_refs` 为实际记录键到 SHA 的映射。

以上用 `submit --kind script-context|design-brief|stage-design` 保存；context按完整合同自动ready，方向与阶段设计按用户确认 `approve-record`；stage-design 指定 `--scope`。阅读、定位和分析方法见 [总控](director-understanding.md)。字段不代表必须把六组维度逐项填满。

阶段metadata与可见字段同样守分域：identity_invariants只属identity；approved_choices.field须指向当前payload实际存在的本域字段；recognition_axes中face_structure/hair_structure属identity，silhouette/body_posture属body，costume_color属costume。morphology_details只含当前scope。body/costume若追加world_influences，只能写appearance_effects数组，各项除feature/mechanism/basis/evidence_status外须有field，指向本域实际可见字段；不得重设environment/technology/resources_and_access或改写身份世界规则。

独立分析首稿可为简洁可读草案，写了schema_version不表示可直接submit。正式提交时按本文转换为完整生产对象；不能把understanding写成无schema的摘要、specialist_plan写成列表、appearance写成字符串，identity.parent_refs也不能额外塞script-context。最小合法结构见 [身份合同样例](../examples/phased-identity-contract.md)。

## 当前 CharacterDesignCardV2.5

phased 项目通过 `compile-design-card --character-id CHR --variant-id STATE` 机械合成当前已批准的 base identity、base body 与 STATE costume。公共字段为 `character_id,variant_id,morphology,facts,inferences,approved_choices,identity_invariants,appearance,costume,unresolved`，并继承 `recognition_axes`、`differentiation_review`、`feature_focus`、`body_form`、`world_influences`、`facial_surface` 和 `visual_details`。

非人新phased可用 `morphology_details{identity,body,costume}` 提供各阶段形态描述，visual_details可空，不强套人脸毛发和人类比例；共同世界/身份/焦点/证据仍适用。`asset_domain`当前只接受character，其他值明确拒绝，未来域不在本轮隐式启用。

六组具象字段见 [细节标准](design-detail-standard.md)，身体测量见 [焦点和形体](feature-focus-and-body-form.md)。`world_influences` 含 `environment,technology,resources_and_access,appearance_effects[{feature,mechanism,basis,evidence_status}]`；`facial_surface` 含 `stable_marks,applied_decoration,temporary_effects,absence_or_focus_decision`，非空项含 `feature,placement,visible_form,narrative_basis,continuity,evidence_status`。阶段快照与V2.5的 `evidence_status` 可为 `script_fact|approved_choice|inference|creative_choice`，保留来源性质；creative_choice不代表尚未审批，实际批准由快照外层approval、SHA和stage_receipts证明。旧V2.4仍仅script_fact/approved_choice。inline执行结果同样保留script_fact/inference/creative_choice，不把创意伪写原文。

V2.5 增加 `stage_receipts`（方向与阶段记录键到 SHA）和十三项 `specialist_coverage{ID:{plan,executions[]}}`。executions 从阶段的实际工作承接，保留 scope 和 variant_id；完整卡不能仍有未执行的 defer 任务，not_needed 有具体理由。inline 的 knowledge_refs/rules_applied/results 或 independent 的真实提案/哈希/采用映射见 [专项合同](specialist-contract.md)。合成不产生新选择，冲突阻断；批准由已确认源快照继承并记录，不代表系统替用户决定人物。

## 当前专项提案

新独立交接使用 `CharacterSpecialistProposalV1.2`，包含任务、知识哈希与执行方式；默认一套推荐，重要分歧才备选，1–3 项。每套至少两个有结构与来源性质的 design_elements。真实会诊与主控 inline 执行分开，详情见 [专项合同](specialist-contract.md)。

## CharacterPromptPackageV1

共同字段为 `stage:avatar|expression|full_body|costume_design|execution`、`target_model`、`character_id`、`variant_id`、`anchor_images`、`reference_images`、`prompts[{id,text}]`、非空 `acceptance_checks`。target_model 使用当前目标 GPT Image 2.5。

complete 模式填写已批准的 `design_card_sha256`。phased 模式省略该字段，使用 `design_basis:{records:{记录键:sha}}`，严格匹配 [阶段依据表](phased-design.md)：avatar/expression 用 brief+identity；full_body 加 body；costume_design 加当前状态 costume；execution 再加当前状态合成卡。正式依据全部已批准，预览例外仅限头像。

头像预览填 `purpose:preview`、`preview_mode:direction_first|image_first`。direction_first 需要已批 brief、冻结 identity；image_first 仅在明确先图后确认需求时允许未批但冻结的 brief/identity。script-context须ready，visual-bible、cast-plan仍先批准。预览不是正式锚点。`promote-candidate --image-id ID --operator NAME` 在原依据已批、SHA一致且回图pass时同图转正；明确合并确认可用 `--approve-design-basis`。未决项、意外新增细节和不一致须先解决。

v2 历史五阶段前三图用 base，后两图用当前状态；v3 前三图也用 base，execution 用当前状态。图片锚点：头像空，九宫格含头像，全身含头像和九宫格，服饰含三张基础图，执行再含本状态服饰图。phased头像1–3条，默认一套推荐；complete沿用2–3条。九宫格 labels 长9且各含中文；16格要求 `grid_explicit_user_override:true` 和 `grid_override_basis`。全身加 `head_visible:true,feet_visible:true`；服饰加资产表一致的 `variant_name`。

头像 `aspect_ratio:3:4`，全身 `aspect_ratio:9:16`，每条写对应比例，全身验收也核比例。明确用户改比例时填 `aspect_ratio_explicit_user_override:true` 和 `aspect_ratio_basis`。人形基础图带 `reference_attire`：头像/表情 `face_only|white_tank|white_sports_tank`，全身 `white_tank_shorts_barefoot|white_sports_tank_black_shorts_barefoot`。头像可取双肩与上胸，不强制锁骨以上；上胸入画可直接白背心，不生成裸体躯干。从 face_only 头像切背心表情须 `reference_attire_basis`。例外用 `approved_exception`，附 basis 和 description。模卡衣装不是剧情状态，执行图恢复正式衣装。

人形 execution 的 layout：

```json
{
  "top_left": "front_face",
  "top_right": "three_quarter_face_45",
  "bottom_left": "headless_enlarged_front_costume",
  "bottom_right": "complete_back_head_to_shoes"
}
```

非人按批准替代布局，所有依据/锚点绑定当前 SHA，不能使用过期版本。

## 审查、打包与历史兼容

`CharacterImageReviewV1` 有 `image_sha256,stage,verdict:pass|revise|uncertain`，数组 `factual_conflicts,identity_issues,layout_issues,label_issues,blocking_issues,adoption_proposals`。pass 时缺陷为空；没有图片不能给视觉结论。preview 转正前新细节提案也须解决。

`CharacterAssetPackV2` 含当前状态五阶段正式图片、设计/提示词/审查、来源和批准记录，列 SHA、插件版本和用途；preview 不打包。保留context_source_receipt与项目knowledge-snapshots，重新核验所有哈希；插件升级不破坏已冻结知识依据。图片文件以真实资产名、状态名、阶段和短 SHA 命名。旧四阶段用 V1 清单。

项目级最终交付另含一份“有设定图资产表” XLSX，执行[单元格内图片合同](final-asset-table.md)。按角色 ID、状态 ID、阶段和图片 SHA 对账；图片本体嵌入对应单元格，保留原资产表非图片数据，逐图重开核验。未批准图只进入明确标注的测试预览表，不进入定稿表。这个工作簿是角色包之外的交付物，不改变既有 `CharacterAssetPackV1/V2/V3` 结构。

历史合同继续回读：V1基础字段；V2增加五轴和近邻复核；V2.1增加六组细节及10项覆盖；V2.2增加焦点、身体、11项路由和真实提案映射；v0.2.3增加比例锚点；V2.4增加世界/面部表面及13项覆盖。旧V1/V1.1提案、CastPlanV1及批准提示词保持有效。complete 的现有 V2.4 整卡流程继续可用，不能把新 inline 收据强塞给旧 used 合同。任何新修改按其模式和合同提交，不自动升级、重画或使旧批准无效。
