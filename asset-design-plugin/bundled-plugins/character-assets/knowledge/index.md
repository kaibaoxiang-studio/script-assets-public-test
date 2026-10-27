# 角色资产知识索引 v0.2.6.1

无台词群演／群像先由 `plan.asset_mode=ensemble` 路由 `$character-ensemble-designer`，加载 `references/group-ensemble.md`：剧本明确人数照数、未明确标代表人数；按获批世界美术基准做一张全身同画布执行图。有指定台词者走 `speaking_extra`，每状态只做一张独立 9:16 四格执行图。下文服饰设计师与四图链路只适用于常规 `individual`。

新项目独立人物服饰阶段必须调用 `$character-costume-designer`，先读 `references/costume-designer.md`，再按当前设计问题读 `references/knowledge/character-costume-designer/costume-deep.md`。它从人物总控已验证的全文理解与方向建立穿衣风格圣经和逐状态文字设计，统筹款式、剪裁、配色、材质、饰品五专项；前四项须有实际部位成果。头像身份阶段可用 `references/knowledge/character-face-design/original-face.md` 固定原创骨相与比例；服饰状态妆造用 `references/knowledge/character-costume-designer/state-makeup.md`，不改变已批准的脸。三份新增知识快照分别溯源用户 ZIP 与两份 DOCX，原文件成员哈希见 `knowledge/archive-manifest.json`。

`pipeline_version:3` 的独立人物采用头像、九宫格、全身模卡、逐状态 9:16 四格执行图四类图片；无台词群像每状态一张全身单图。旧 `costume_design` 图仅适用 v2 项目。

先读 [人物总控](../references/director-understanding.md)：全文理解人物与故事、定位、解析细节、形成设计意图后，再决定 Skill 执行和知识加载。先读用户全文或复用有效context，再按当前任务读取必要知识。references是目录，不是全读清单；可按问题读相关知识全文，但不机械全读，也不为了省时省略人物理解。knowledge/reference 是方法，当前人物事实与已确认决定优先；本次不新增知识采集工程。

| 情景 | 加载 | 用途 |
| --- | --- | --- |
| 全文阅读、人物理解与定位 | `references/director-understanding.md`、`references/evidence.md` | 连续阅读全文与覆盖复用；跨场言行、评价可靠性、关系、弧线与观众信息；理解后再路由 |
| 默认阶段深化与首图快看 | `references/phased-design.md` | ScriptContext、方向稿、身份/身体/服饰快照；冻结预览、同图转正、机械合成与旧项目兼容 |
| 项目启动、全员规划 | `references/evidence.md`、`references/character-design.md`、`references/differentiation-framework.md`、`references/knowledge/character-cast-differentiation/ensemble.md` | 建立第 -1 阶段视觉基准、比较组与五轴矩阵；旧 Skill 的占用表方法按需加载 `legacy-visual.md` |
| 无台词群演群像 | `$character-ensemble-designer`、`references/group-ensemble.md`、`references/differentiation-framework.md` | 核人数与同组差异，按项目获批风格设计一张全身同画布执行图 |
| 单张或批量产出、状态与技能路由 | `references/routing-and-integration.md`、`references/workflow.md` | 规格化需求，用 CLI plan 列阻断，按阶段和状态交接 |
| 环境、资源、科技改变外观 | `references/knowledge/character-world-appearance-design/world-appearance.md` | 区分实际接触的机制推演与世界相容的主动创作选择；没外观原文不等于跳过设计，避免族群刻板映射 |
| 面部标记、妆容或状态变化 | `references/knowledge/character-face-decoration-design/face-decoration.md` | 稳定痕迹、主动施加、临时效果分层，逐项写叙事与连续性 |
| 特征主次与三维形体缺口 | `references/feature-focus-and-body-form.md`；按路由分别加载 `character-feature-focus/feature-focus.md`、`character-body-design/body-proportion-3d.md` | 理解与意图先于路由；普通主控执行规范、复杂真实会诊；到身体阶段给可核对比例、体块和动作 |
| 逐人设计、Grill Me | `references/character-design.md`、`references/costume-and-morphology.md`、`references/specialist-contract.md` | 先理解定位并形成意图，主动填补留白；按难度采用inline或independent，不强制全员走完岗位 |
| 新建重点人形设计卡过于概括 | `references/design-detail-standard.md`、`references/knowledge/character-design/anti-stereotype-texture.md` | 对应阶段具象细节、十三项规划及实际执行收据；最终V2.5合成卡 |
| 剧本与三份输入冲突 | `references/evidence.md` | 按原文证据优先列疑点，不暗改事实 |
| 头像、九宫格、全身模卡提示词 | `references/prompting.md`、`references/model-card-baseline.md` | 从当前阶段已确认依据抽取可见锚点；preview冻结草案，指定参考职责和模卡衣着 |
| 每状态服饰设计图 | `references/costume-design-stage.md`、`references/prompting.md` | 一状态一图，绑定三张已批准身份图及状态卡 |
| 油亮、蜡感、材质空泛或脏糊 | `references/render-texture-standard.md`，再按设计/提示词/审查/修图的对应 `anti-stereotype-texture.md` 快照加载 | 分开设计层与渲染层；按媒介、证据和回图缺陷选词与修复 |
| 外部出图的通用提示词结构与原样中文 | `references/knowledge/character-image-prompt/hedgehog-general-image-skill.md`、`references/prompting.md` | 区分新图/编辑，控制补充细节，逐张标注参考图职责 |
| 已批准的 2D→3D 呈现 | `references/knowledge/character-image-prompt/hedgehog-2d3d.md`、`references/prompting.md` | 保留身份与服装，只转换已批准的媒介、材质和光照 |
| 表情资产 | `references/expression.md`、`references/prompting.md` | 默认九宫格并生成图内中文标签；16 格须明确用户选择 |
| 执行资产表 | `references/execution-sheet.md`、`references/prompting.md` | 人形 2×2 精确版式及非人适配 |
| 回图审查 | `references/review.md` | 核对事实、身份、版式、标签并分类阻断问题 |
| 局部修图 | `references/editing.md` | 描述目标区域、改变内容、保留内容与禁改内容 |
| 单项修图与回流重审 | `references/knowledge/character-image-edit/hedgehog-general-image-prompting.md`、`references/editing.md` | 每轮修一项，重申身份和其他格位不变量，再审查整张图 |
| 上游改版 | `references/workflow.md`、`references/evidence.md` | 比较输入版本并局部重开受影响的资产 |

本索引描述何时加载；采用方法与实际可见成果仍须记录，不能把列出路径视为已执行Skill。每份规则的出处、采用方式和未采用内容见 `references/source-notes.md` 与插件根目录 `sources.lock.json`。历史服装知识是灵感入口；需要具体时代准确性时另查可靠材料，记录查证位置。

## 专项知识加载

| 缺口 | Skill 与知识快照 |
| --- | --- |
| 世界环境、资源与技术在外观中的结果 | `$character-world-appearance-design` → `references/knowledge/character-world-appearance-design/world-appearance.md` |
| 主锚点、安静区、自然不对称 | `$character-feature-focus` → `references/knowledge/character-feature-focus/feature-focus.md` |
| 发际、发流、发型块面与背面 | `$character-hair-design` → `references/knowledge/character-hair-design/hair.md` |
| 年龄比例、骨架、体重分布、体态 | `$character-body-design` → `references/knowledge/character-body-design/body.md` |
| 五官与脸部骨相、模板脸 | `$character-face-design` → `references/knowledge/character-face-design/face.md` |
| 面部记忆点、发耳颈饰 | `$character-face-signature-design` → `references/knowledge/character-face-signature-design/face-memory.md` |
| 痣疤、面绘、眼唇妆与临时面部状态 | `$character-face-decoration-design` → `references/knowledge/character-face-decoration-design/face-decoration.md` |
| 皮肤纹理、光泽、生活痕迹 | `$character-skin-design` → `references/knowledge/character-skin-design/skin.md` |
| 衣装品类、长度、松紧与层次 | `$character-costume-style-design` → `references/knowledge/character-costume-style-design/costume-style.md` |
| 结构线、缝接与活动余量 | `$character-costume-cut-design` → `references/knowledge/character-costume-cut-design/costume-cut.md` |
| 衣装主辅色和色块 | `$character-costume-color-design` → `references/knowledge/character-costume-color-design/costume-color.md` |
| 纤维/皮革/金属表面与磨损 | `$character-costume-material-design` → `references/knowledge/character-costume-material-design/costume-material.md` |
| 衣身、腰、手与随身穿戴饰品 | `$character-costume-accessory-design` → `references/knowledge/character-costume-accessory-design/costume-accessory.md` |

群像差异化总控是横向审查，不代替以上专项。主控和专项围绕本轮问题加载必要知识，必要时读全文；同一件越过锁骨的饰品由主控指定唯一主责。

历史 0.2.1 新增《拒绝脸谱化人物设计》来源的 7 份定点快照：`character-design`、`character-cast-differentiation`、`character-skin-design`、`character-costume-material-design`、`character-image-prompt`、`character-image-review`、`character-image-edit`。头像 3:4 规则在 `references/prompting.md` 和 CLI 提示词包合同中，回图按 `references/review.md` 核对。

历史 0.2.2 新增特征聚焦与身体比例/三维体块两份来源，分别落在设计、形体、提示词、回图审查的 5 份定点快照。逐人设计先保存专项路由；used 交接必须有提案文件、SHA、所选方案和字段映射。

历史 0.2.3 加强身体比例从形体专项到设计卡、全身提示词和回图验收的交接；全身图默认 9:16 竖版，提示词包和最终回图均检查比例。头像/表情与单独全身图采用模卡基线，正式服装由执行资产表承接；见 `references/model-card-baseline.md`。比例字段见 `references/feature-focus-and-body-form.md` 与 `examples/body-proportion-contract.md`。不新增知识来源。

历史 0.2.4.1 新增环境技术外貌与面部装饰妆容两份知识快照及两个按需专项。新项目使用五阶段链路和 V2.4 卡；单张/批量路由见 `references/routing-and-integration.md`，状态服饰图见 `references/costume-design-stage.md`。旧项目维持四阶段。


0.2.5 复用已有知识，新增人物总控与阶段深化方法：全文理解→定位→细节解析→设计意图→Skill/knowledge路由；方向稿规划十三项，常规inline执行、复杂independent会诊，当前阶段产出可画设计。新默认phased，最终V2.5卡由已批快照合成；旧complete和批准记录兼容。
