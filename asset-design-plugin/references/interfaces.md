# 数据接口与责任

精确字段、必填项和类型以根目录 schemas 为准；本页说明业务含义，不建立第二套合同。结构验证只证明交接形状与状态合法，不能证明模型真正理解或审美达标。

| 接口 | 业务责任 | 要点 |
| --- | --- | --- |
| [AssetProjectContextV1](../schemas/AssetProjectContextV1.schema.json) | 母总控保存全文理解 | `source_sha256` 匹配来源；`coverage` 对应实际读过的块；综合故事、世界和跨域设计关系；证据区分剧本事实、推导、创作选择、新设定；隐藏信息不提前外显 |
| [AssetVisualBibleV1](../schemas/AssetVisualBibleV1.schema.json) | 母总控提出，用户确认共同基准 | 引用 `context_revision`；将风格意图、世界、材料、光色和符号落到三领域适用约束；未知集中列出 |
| [DomainTaskPlanV1](../schemas/DomainTaskPlanV1.schema.json) | 母总控形成具体任务与依赖 | `tasks` 包含 `id/domain/asset_id/state_id/objective/depends_on/context/constraints/deliverables`；可选 `skill` 选择该领域真实专项；不以角色名作正式 ID |
| [DomainResultV1](../schemas/DomainResultV1.schema.json) | 子插件返回真实成果 | envelope 保留成功／阻断／失败，业务结果保留摘要、设计决定、未决问题与实际用到的知识；真实文件单独登记 |
| [DeliveryRegistrationV1](../schemas/DeliveryRegistrationV1.schema.json) | 登记领域已有批准产物 | 保留 `asset_id/state_id/domain/stage/artifact_path/approval_record_path/task_id`；批准记录须真实可核对，不因整合采用产生批准 |

## 公共语境与子插件合同

母台账负责来源、共同基准、任务、采用、跨域依赖和交付引用。子插件保留自身项目格式、阶段、设计／图片审批及交付规范。人物 `ScriptContextV1`、分阶段快照与 `CostumeStyleBibleV1`，场景的可靠图／文基准，道具的选案与主视觉记录继续由对应领域维护。

母上下文不是上述合同的改名替代品。交接时传递适用摘录和原来源，必要时按子合同补齐。相同词语不表示相同状态：任务执行成功、总控采用、设计批准和图片批准各有记录，不能互相推定。

## 来源与临时标识

资产表存在时沿用其稳定 ID、状态与名称，保持输入身份。只有原始剧本时允许带来源定位的临时工作条目；进入正式资产登记前需要正式表或显式映射。新增剧情身份、功能、家族或阵营含义单列待确认。

知识使用记录写实际文件或 Skill 与解决的问题；不能把包内存在等同于已经加载，更不能把读取资料写成独立会诊。统一索引保留真实路径、文件哈希、领域版本、批准来源、关系与未解决项。
