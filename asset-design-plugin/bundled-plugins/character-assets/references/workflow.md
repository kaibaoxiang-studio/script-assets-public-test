# 角色资产项目工作流 v0.2.6.2

## 无台词群演群像分支

先运行 `plan` 查看 `asset_mode`。`ensemble` 按[群像单图合同](group-ensemble.md)从标准剧本人数、动作、道具与已批视觉基准形成 `GroupEnsembleDesignV1`，文字稿获批后每状态只生成一张完整全身群像 `execution` 图，再审图、批准和打包。有指定台词的群演走 `speaking_extra`：以原文台词和获批风格设计 `SpeakingExtraDesignV1`，每状态只产一张独立 9:16 四格执行资产，跳过前三张身份图。旧项目已批准记录不自动迁移。

## v0.2.6 新项目链路

全文理解 → 人物方向 → 身份设计与头像 3:4 → 表情九宫格 → 身体设计与全身模卡 9:16 → 服饰设计师制定并获批穿衣风格圣经 → 每状态五专项实际成果和服饰文字快照获批 → 机械合成设计卡 → 每状态一张 9:16 竖版四格执行图 → 单图审查、批准、打包。文字阶段不是额外图片阶段。旧项目按 pipeline_version 回读。


主入口 `$character-assets`。先读 `knowledge/index.md` 与 [人物总控](director-understanding.md)，根据人物问题加载已有知识。模型负责阅读理解和创作，`scripts/character_project.py` 管理文件、哈希、批准和发布门槛；CLI 合同通过不证明人物或画面质量通过。

## 1. 接入与阅读

可以先独立接剧本、小传或片段做人物分析，说明范围；无项目且未指定阶段时默认identity/头像，只交人物定位、当前身份首稿和关键路由，身体衣装留方向或约束，正式登记时再补生产JSON。正式项目在用户工作目录初始化，剧本、资产表必填，场记可选；不把项目数据写插件目录。

```sh
python scripts/character_project.py init --project-root /work/role-project --project-id PROJECT_ID --screenplay /input/standardized_screenplay.json --asset-table /input/assets.json --design-progression phased
python scripts/character_project.py context-units --project-root /work/role-project
python scripts/character_project.py status --project-root /work/role-project
```

已有快照可改用 `init --project-root /work/role-project --snapshot /input/asset-project-snapshot.json`，先校验来源及可选视觉基准批准记录。需要场记加 `--scene-log`；未提供时注明缺少的校对来源。新项目默认 phased；先完整定卡用 complete；旧项目无字段按 complete。

实际阅读全文，长文分批并记录覆盖，建立轻量覆盖全roster的 `ScriptContextV1`；理解全剧因果后再检索目标角色、联读跨场言行和关系。已读内容按源哈希复用，不每位人物重读全剧；不能只检索姓名或仅读摘要就声称全文理解。context-units 是核对入口，不代替阅读。

## 2. 基准、人物方向与阶段设计

提交阅读综合：来源SHA、覆盖与结构完整且未决为空即自动ready，系统只确认阅读声明合同，interpretation_confirmed:false，不增加用户审批；未决非空须复核，手动approve可选。项目视觉基准和轻规划按原流程确认；人物解释在方向稿集中确认。人物定位先于外观：原文行为和评价分开，分析矛盾、弧线和观众信息，再提出一套推荐意图与确有必要的备选。普通细节主动补齐，有剧情含义的新经历或身份显式提出。

```sh
python scripts/character_project.py submit --project-root /work/role-project --kind script-context --file /draft/context.json
python scripts/character_project.py submit --project-root /work/role-project --kind visual-bible --file /draft/visual-bible.json
python scripts/character_project.py approve-record --project-root /work/role-project --kind visual-bible --operator OPERATOR
python scripts/character_project.py submit --project-root /work/role-project --kind cast-plan --file /draft/cast-plan.json
python scripts/character_project.py approve-record --project-root /work/role-project --kind cast-plan --operator OPERATOR
python scripts/character_project.py submit --project-root /work/role-project --kind design-brief --character-id CHR-001 --variant-id base --file /draft/direction.json
python scripts/character_project.py approve-record --project-root /work/role-project --kind design-brief --character-id CHR-001 --variant-id base --operator OPERATOR
python scripts/character_project.py submit --project-root /work/role-project --kind stage-design --scope identity --character-id CHR-001 --variant-id base --file /draft/identity.json
```

approve 命令在用户已确认相应内容后执行，不把示例命令当作模型自行批准的授权。方向默认先确认；用户明确先看图时才走 image_first 预览。常规项由主控执行规范、记 inline 结果，复杂项独立会诊、保存真实提案；见 [专项合同](specialist-contract.md)。阶段门槛、payload 与全部命令见 [分阶段设计](phased-design.md)。不为十三专项固定十三轮。

参考图通过 `import-reference --role identity|costume|style|inspiration --desired-strength '具体提取点'` 登记，按用户已指定用途采纳，不整体照搬。近邻比较按 [差异化框架](differentiation-framework.md) 执行；`cast_diff_audit.py` 只找相同文本/缺轴候选，不证明成图辨识度。

## 3. 首图快看与正式五阶段

phased 身份草案可先生成 preview 头像。提示词使用冻结的 `design_basis.records`，填写 `purpose:preview`；默认 direction_first 的 brief 已批准、identity 可未批。image_first 只按明确先图需求允许两者冻结未批；script-context须ready，项目基准和cast-plan仍先批。preview 不能作为正式下游锚点或打包。

```sh
python scripts/character_project.py submit --project-root /work/role-project --kind prompt-package --character-id CHR-001 --variant-id base --stage avatar --file /draft/avatar-prompt.json
python scripts/character_project.py import-image --project-root /work/role-project --character-id CHR-001 --variant-id base --stage avatar --path /images/avatar-1.png
python scripts/character_project.py submit-review --project-root /work/role-project --image-id avatar-HASH --file /draft/avatar-review.json
```

实际看图并保存 `CharacterImageReviewV1`。方向、身份与该图获用户确认，review pass、无待采纳新细节、依据和图片 SHA 不变后，可 `promote-candidate --project-root /work/role-project --image-id avatar-HASH --operator OPERATOR --approve-design-basis`，显式承接同 SHA 方向/身份审批并同图转正；已先批依据则省略 flag。不需要重新生图，不能自动接纳其他候选。改变身份快照后原图不能沿旧 SHA 转正。

v3 常规独立人物顺序为头像 → 九宫格 → 全身模卡 → 每状态一张 9:16 四格执行图；服饰设计先以文字批准。v2 历史项目保持每状态服饰设计图 → 对应执行图。后续阶段的设计快照按需深化并批准，图像提示词只取当前可见项。头像默认3:4，身体图默认9:16；基础图采用 [模卡基线](model-card-baseline.md)，正式服饰图和执行图恢复角色衣装。头像可完整头部、双肩与上胸，不强制锁骨以上；上胸入画可直接白背心；全身背心、短裤、赤脚。背景未另获批时用中性纯色。

正式图片继续 import-image → 实际审图 → submit-review → `approve-image --image-id ... --operator ...`。与近邻已有图并排比较；只换衣发色却同脸同体型属于设计或执行缺陷，分别回设计或修图。`character-image-edit` 针对具体缺陷修图，重新导入后整图复核。

## 4. 合成、打包与变更

body和当前状态costume快照批准后，`compile-design-card --project-root /work/role-project --character-id CHR-001 --variant-id STATE_ID` 合成 V2.5 卡。它只合并同 SHA 已批准快照，冲突阻断，并记录 `system:approved-scope-composition` 与 `inherited_from`，不新增设计也不重复要求批准同一套细节。新创意必须回阶段快照，不直接 submit 手写 V2.5 卡。

v3 当前状态服饰文字快照、穿衣圣经和合成卡批准后才能做唯一执行图；v2 历史项目仍须先批准服饰图。最终 `package --character-id ... --variant-id STATE_ID --output NEW_DIRECTORY` 按项目版本汇总正式阶段、设计、提示词、审查、批准与来源；输出目录必须新建，preview不能混入。

项目级最终交付还须按[有设定图资产表规则](final-asset-table.md)制作工作簿：把已批准图片回填到资产表对应角色与状态行，以真正的单元格内图片保存并重开核验。只出角色包或把图片浮在格子上均不满足最终输出；测试图可另存明确标注的预览表。

来源改版用 refresh。资产表变化按角色定位，剧本/场记先补读并分析影响，pending_impact 时停止新决策和发布。核对后 `resolve-impact --affected CHR-001 CHR-002 --operator OPERATOR`，改变整体风格/世界规则加 `--global-style`。未受影响批准保留，不凭空断言无影响。

旧 complete 保留先完整设计卡批准后出图，旧四阶段继续原打包链路；旧卡与提案回读、不自动迁移和重画。新总控分析不自动覆盖已批准身份。CLI不发图、不读懂画面、不自动得出历史文化结论。
