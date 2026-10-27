# 项目工作流与命令

命令从插件根目录运行，使用 Python 3.12+。`harness.py --help` 和各子命令 `--help` 为参数的实际依据。用户直接调用四个 Skill 时，由入口完成必要文件准备；无需用户手写下列 JSON。

## 建立与恢复

```sh
python3 harness.py doctor
python3 harness.py init --project /absolute/project --script /absolute/screenplay.json --assets /absolute/assets.json
python3 harness.py status --project /absolute/project
```

`init` 生成来源快照、哈希和 `sources/chunks.json`。必须实际阅读全文和来源单元后才提交上下文；自动切块不等于模型阅读。只有原始剧本时可省略 `--assets`，工作清单保持临时来源性质。不得凭名称生成正式 ID。恢复项目先看 `status`，不重新初始化覆盖旧记录。

## 全剧理解和美术基准

按照 [全文理解](full-script-understanding.md) 写来源覆盖和综合理解，按 [上下文 schema](../schemas/AssetProjectContextV1.schema.json) 提交。基准引用已提交上下文版本，按 [基准 schema](../schemas/AssetVisualBibleV1.schema.json) 写设计规则及待确认项。用户看到简洁推荐并明确接受后，记录原确认语句。

```sh
python3 harness.py submit-context --project /absolute/project --file /absolute/context.json
python3 harness.py submit-baseline --project /absolute/project --file /absolute/baseline.json
python3 harness.py approve-baseline --project /absolute/project --revision 1 --statement '用户实际确认语句'
```

不能把示例确认语句当作真实确认。关键待确认项影响当前设计时先解决，普通创作选择可随本轮方案审阅。

## 规划、调用与整合

按 [任务计划 schema](../schemas/DomainTaskPlanV1.schema.json) 准备目标批次。每项包含领域、资产／状态、具体目标、依赖、相关语境、限制和所需成果。只在具体专项问题上选择相应子 Skill，默认进入各领域主入口。详细交接见 [子插件交接](domain-handoff.md)。

```sh
python3 harness.py plan --project /absolute/project --file /absolute/tasks.json
python3 harness.py run --project /absolute/project --max-workers 3 --timeout 600
python3 harness.py status --project /absolute/project
```

执行器只推进上游已由总控采用的任务，独立项可并行。一次 `run` 不会自动采用返回物；查看真实产物并逐项 `adopt` 后，再运行 `run` 推进依赖任务。因具体原因失败或阻断后，修正必要输入再 `retry`，保留此前返回与尝试记录；取消仅停止当前执行，不删除历史。

```sh
python3 harness.py retry --project /absolute/project --task task-id
python3 harness.py adopt --project /absolute/project --task task-id --statement '采用内容、依据和保留问题'
python3 harness.py cancel --project /absolute/project
```

`adopt` 是整合采用，不是领域设计或图片批准。子插件已批准交付通过 [登记 schema](../schemas/DeliveryRegistrationV1.schema.json) 引用真实产物与原批准记录；未获批准的设计稿保留为任务产物。

```sh
python3 harness.py register-delivery --project /absolute/project --file /absolute/delivery.json
python3 harness.py index --project /absolute/project
```

统一索引连接原交付和批准记录，说明状态与未解决项，不取代原子插件产物。

## 导入和变更

```sh
python3 harness.py import-character --project /absolute/project --file /absolute/character-project/project.json
python3 harness.py refresh-sources --project /absolute/project --script /absolute/revised-screenplay.json --assets /absolute/revised-assets.json
```

显式导入核对来源、ID、文件及批准依据；不能验证的部分保留待复核。来源刷新后重新核对阅读覆盖、基准及影响任务，旧版本保留。改动传播见 [审批与变更](approval-and-change.md)。
