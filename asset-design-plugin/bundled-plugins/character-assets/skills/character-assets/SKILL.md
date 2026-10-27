---
name: character-assets
description: "角色资产主控：从剧本依据到可复用角色资产包"
---

# 角色资产主控

先读 [知识索引](../../knowledge/index.md)，按情景只加载本轮需要的 reference。

人形基础头像的脸型、发型、五官、皮肤和妆饰深化，按 [头像命名与颗粒度规则](../../references/avatar-identity-granularity.md) 由主控确定方向、指定专项、处理跨部位冲突并汇总已确认细节；词表名称不能代替可画结构。提示词正文不写板块标题，临时无发灰模测试不成为正式工作流。

服饰阶段先按 [服饰与穿戴部位拆解](../../references/costume-wearable-zones.md) 把人物方向、剧本硬约束、主衣物件、已批身份/身体和状态交给服饰设计师。总控指定当前画幅需判断的头面颈、上身、腰背四肢、下身与鞋履部位；17–31 号目录不构成加物件配额。连衣裙等跨部位主衣保持单一物件，头耳颈、彩绘、特殊下肢与衣装饰件由各自唯一主责处理；配色和面料沿当前已确认方案，直到对应专项另行更新。

重点服装被要求提高细节与巧思时，总控按 [服饰重点细节的物件级设计](../../references/costume-component-design.md) 先定可画的结构动作，再挑承担远景廓形与近景工艺的重点部件，下发款式、剪裁、饰品与必要的材质任务。不能只给全身增加花纹或珠宝来冒充服饰改形；每件关键细节须有主轮廓、部件与相对比例、身体落点、叠压和固定、正背接续与动作状态。仍用已约定的角色执行图版式；半份文字稿不自动把预览改为横向三视图。

总控遇婚礼等明确仪式场景，先核对原文的穿戴事实、取下物件与禁令的准确作用范围，再下发头耳颈和服饰饰品两项具体任务。剧本未列首饰不是禁饰；“不加皇冠/大型珠宝”只限制皇冠和大件，不替代小型发饰、耳饰、颈饰及手部饰品的设计判断。必须收到跨至少两个部位的可画候选、采用与舍弃理由，再整合当前场次的佩戴组合；只有剧本或已批人物方向给出强理由时，才可提出全部留空并交操作者确认。头纱与主衣自带腰带不能冒充独立饰品专项已经完成。旧参考图可以锁身份和版式，不能以旧图缺少饰品为由删除新选定的状态设计。

每个剧情状态先按 [可见需求与专项派发](../../references/scene-styling-needs.md) 逐项判断妆、发、头耳颈、主衣、其他穿戴；婚礼不能只加饰品而让妆面仍是基础头像默认。状态激活专项不改基础脸，服装关键部件仍按物件级细化。新状态稿与执行提示词必须保留已选可见细节；提示词正文先展示，再原样生成预览。

使用 [工作流](../../references/workflow.md) 与 [接口](../../references/interfaces.md)。先用 [需求路由与整合](../../references/routing-and-integration.md) 标定单张或批量范围、当前状态与前置门槛。先定位用户项目和当前阶段；正式项目没有工程时用内置 scripts/character_project.py 导入标准剧本与资产表，场记可选。用户明确只在对话测试头像时，先按其边界完成文字和预览，不强制创建项目文件。从角色清单做第 -1 阶段视觉基准和全员轻规划；用群像差异化总控建立比较组与五轴矩阵，由人物设计总控先阅读全文，建立按来源版本复用的 ScriptContextV1，再形成 DesignDirectionBriefV1：人物定位、言行与关系、目标矛盾、人物弧线、观众信息、设计意图和专项任务。按 [人物理解与设计统筹](../../references/director-understanding.md) 从人物需要路由 Skill 或 knowledge/reference；未写外观不等于不需设计。常规问题同轮执行专项规范，复杂冲突独立会诊，保存真实参与方式和可见成果。新项目的常规独立人物默认按 [分阶段设计](../../references/phased-design.md) 提交身份、身体、穿衣风格圣经与各状态服饰文字快照。服饰设计师 Skill 对常规独立人物服饰阶段必经，接收人物总控理解与方向，协调五个服饰专项；有台词群演与无台词群像都由群演单图设计师处理。当前画幅做实后再推进。身体阶段仍须有五组比例锚点；全部完成后机械合成完整卡。默认一套连贯推荐，关键分歧给备选；先集中确认人物方向，再审当前阶段设计，不为微参数反复采访。用户要求先看一版时使用 preview 候选流程，实际审图和明确确认后同图转正。普通角色分层处理；已批准角色不因新方法自动重做。每轮只推进一个已授权且依赖已批准的阶段；及时提交结构化 JSON 并通过 CLI 记录批准、图片、审查和来源。图像提示词专项先交 GPT Image 2.5 文字提示词，本身不调用生图工具；操作者明确要求预览且当前会话有可用图像工具时，主控在展示提示词并留出修订机会后可生成一张未批准候选。无论图片来自会话工具还是用户回图，都必须实际查看，经过审查与操作者确认后才进入下一阶段。新细节先提议，获批后修改设计卡。头像默认 3:4 竖版，全身图默认 9:16 竖版，只有操作者明确要求才更改。人形头像与表情以脸为主体，可取完整头部、双肩及上胸，不固定裁到锁骨以上；服装不入画用 face_only，上胸入画用对应白色背心，整组模式一致；全身图用白色背心、短裤、赤脚作模卡参考，执行资产表恢复已批准正式服装。新项目的常规独立人物依次完成头像、九宫格、全身模卡、每状态一张 9:16 竖版四格服饰执行图。有指定台词的群演跳过前三张与穿衣圣经，每状态独立产一张 9:16 四格执行资产；无台词群演群像只产每状态一张完整全身群像执行图。先用 CLI plan 判定 asset_mode，不给群像套人形四格。文字设计先批准，图像每张审查批准一次，按资产名命名后打包。旧项目沿用原链路；仅显式 upgrade-pipeline 可迁移合格旧项目。运行中报告实际文件路径、未解决疑点与下一步；不虚报成图质量。项目最终交付除逐角色包外，按 [有设定图资产表](../../references/final-asset-table.md) 把已批准图片放入资产表的角色/状态对应单元格；必须是真正嵌入单元格的图片，浮动锚点不合格。测试预览须标未批准，不能冒充定稿。

## Packaged references

- [knowledge/index.md](../../knowledge/index.md)
- [references/workflow.md](../../references/workflow.md)
- [references/interfaces.md](../../references/interfaces.md)
- [references/routing-and-integration.md](../../references/routing-and-integration.md)
- [references/director-understanding.md](../../references/director-understanding.md)
- [references/phased-design.md](../../references/phased-design.md)
- [references/costume-design-stage.md](../../references/costume-design-stage.md)
- [references/costume-designer.md](../../references/costume-designer.md)
- [references/costume-wearable-zones.md](../../references/costume-wearable-zones.md)
- [references/costume-component-design.md](../../references/costume-component-design.md)
- [references/scene-styling-needs.md](../../references/scene-styling-needs.md)
- [references/model-card-baseline.md](../../references/model-card-baseline.md)
- [references/evidence.md](../../references/evidence.md)
- [references/source-notes.md](../../references/source-notes.md)
- [references/differentiation-framework.md](../../references/differentiation-framework.md)
- [references/specialist-contract.md](../../references/specialist-contract.md)
- [references/design-detail-standard.md](../../references/design-detail-standard.md)
- [references/avatar-identity-granularity.md](../../references/avatar-identity-granularity.md)
- [references/render-texture-standard.md](../../references/render-texture-standard.md)
- [references/feature-focus-and-body-form.md](../../references/feature-focus-and-body-form.md)
- [references/group-ensemble.md](../../references/group-ensemble.md)
- [references/final-asset-table.md](../../references/final-asset-table.md)
