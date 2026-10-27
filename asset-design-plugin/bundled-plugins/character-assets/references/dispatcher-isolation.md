# 内部 dispatcher 会话隔离 v0.2.5.1

内部能力执行是一次后台工作，不是用户另开的聊天。所有 `harness.py run-capability`、workflow 节点、重试和等待回答后的继续都新建 `thread/start` 且显式设置 `ephemeral: true`。返回的 `thread.ephemeral` 必须为 `true`；接口拒绝、遗漏或返回 `false` 时停止，不退回持久模式。旧运行记录里的 thread ID 只用于诊断，不能拿来 `thread/resume`，从而避免已归档的旧测试聊天重新出现。

## 恢复语义

`harness.py resume` 恢复 Harness 本地任务。输入、操作者回答和上次 blocked 返回物在当前任务中重新交给临时会话；项目文件与已确认设计仍是业务依据。已成功节点按产物和 SHA 验证后复用，不重新执行。不能依靠一个临时会话的隐藏历史恢复工作，也不把 thread ID 当作业务状态。等待回答不要求用户打开内部聊天。

本地 `.harness/runs.sqlite3`、run-report、产物和审批记录继续保存，供恢复、审阅和追踪。临时会话只改变聊天持久化方式，不更改设计规则、画幅、阶段依赖或操作者批准。

## 历史验收与回归

旧包包含旧运行器。验证旧版本前，须先隔离其内部会话生命周期并记录这一非设计变更，或使用原生子代理测试；不能为版本对照再次向用户“最近”创建持久测试聊天。仅以标题匹配不能批量处理历史聊天，须同时核对本地 run 证据、线程目录和当前结束状态。历史测试使用可恢复归档，保留本地验收结果。

回归须验证：普通执行使用临时会话；携带历史 ID 时仍新建临时会话；blocked 后恢复保留回答与上次返回物；服务不确认临时会话时不启动 turn。发布检查还应通过真实 App Server 的无模型生命周期调用确认临时线程不进入持久列表，检查连接关闭后未落盘。结构测试和生命周期测试不替代人物设计或图像验收。

协议依据：[OpenAI App Server](https://learn.chatgpt.com/docs/app-server)。本机协议通过 `codex app-server generate-json-schema --out DIR` 核对 `ThreadStartParams.ephemeral`、`ThreadStartResponse.thread.ephemeral`；具体验收记录随修补版本保存。
