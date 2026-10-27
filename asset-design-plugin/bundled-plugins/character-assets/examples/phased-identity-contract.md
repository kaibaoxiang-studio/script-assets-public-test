# 最小身份合同：由真实运行时测试导出的结构样例

这三份文件直接由[整理前提交的 test_v025_phased_runtime.py](https://github.com/kaibaoxiang-studio/ZiChan/blob/60e04bf1b45763bacb88ffbdc2bd6f5a96666bed/creator-src/tests/test_v025_phased_runtime.py) 中的 setup_brief、payloads、stage helper 在隔离临时项目导出，实际通过当前 submit 合同。使用同目录 sample-screenplay.json、sample-assets.json；仅演示精确结构和交接，不代表完整人物设计质量，也没有生成图片或批准用户资产。

- [ScriptContextV1](sample-script-context-v025.json)：全阅读单元和轻量全员索引。
- [DesignDirectionBriefV1](sample-design-brief-v025.json)：asset_domain为character；understanding是含schema_version的对象；specialist_plan是十三项ID到工作对象的映射，不是列表。
- [identity阶段](sample-identity-stage-v025.json)：payload.morphology为human，appearance是对象；parent_refs恰好只有design-brief:CHR-001:base。不得额外放script-context，方向稿已承接context_sha256。包含本阶段全部责任专项及一项inline执行收据。

样例中的context_sha256、parent_refs和knowledge_refs是真实导出值，但对应当前样例与知识版本，不是通用常量。正式项目先context-units并读全文，生成/提交本项目context，再把返回的当前记录SHA写入方向稿；方向稿提交后，用其当前记录SHA写identity.parent_refs。知识引用使用本次实际读取的插件内相对路径与文件SHA。不要复制其他项目或旧知识版本的SHA，更不要把占位字符串提交。

独立设计首稿中的类型标称不代表可直接submit：可读人物摘要还要转换为完整understanding对象、十三项specialist_plan和准确的分域payload；正式登记时补齐，而不是要求独立首稿先输出全套生产JSON。方向获用户确认后记录approve-record，再可走direction_first头像预览；明确先图后确认才用image_first。context本身在合同完整、未决空时系统自动ready，不追加用户审批。

身体和costume的parent_refs按阶段增加identity、body；不能把后续细节塞入此identity样例。使用 [完整接口](../references/interfaces.md) 与 [阶段门槛](../references/phased-design.md) 核对。测试helper中合成、泛化的措辞仅供结构回归，实际设计须遵守具象标准；这份模板通过结构校验不证明人物理解或审美通过。
