# 资产设计插件 v0.1.0

从完整剧本建立共同美术基准，统筹角色、场景、道具的具体设计，并保留每个决定的来源、版本、审批和交付记录。

> 本页描述公开测试快照 `public-test-2026-10-27-r4`。母插件外壳保持 v0.1.0，包内角色、场景、道具业务以 [ZiChan](https://github.com/kaibaoxiang-studio/ZiChan) 提交 `e089d1287c1499f08c42e75aca093131e9d3fbc0` 为准，场景为 v0.9.5。来源文档经过匿名化，变换与原始字节依据见 [公开导出清单](public-export-manifest.json)。

剧本业务的权威来源是 [script-plugins](https://github.com/kaibaoxiang-studio/script-plugins)；角色、场景和道具的权威来源是 ZiChan。母仓库 [asset-design-plugin](https://github.com/kaibaoxiang-studio/asset-design-plugin) 提供跨资产总控外壳，本公开快照单独更新其领域封装，不对母仓库发布新正式版本。

`validation/` 中真实调用及原发布验收属于 2026-10-23 的上游历史验证，使用的是当时的子插件快照。本轮结构与回归结果见[公开镜像验证](../public-validation.json)；历史结果不能当成本轮场景 0.9.5 的新真实调用证明。

## 四个入口

| 入口 | 用途 |
| --- | --- |
| `$asset-design` | 明确请求跨资产协同时，阅读全文、形成项目美术基准、安排依赖、调用并整合三类资产 |
| `$asset-character` | 人物理解、身份与身体设计、服饰、提示词和回图审查 |
| `$asset-scene` | 静态场景设计、光影色卡、反打与其他角度、局部修改 |
| `$asset-prop` | 道具具体设计、批量 Prompt 表、选案、回图与状态扩展 |

单领域入口可直接使用，不必先启动总控。总控先做全剧轻规划，只深化用户当前指定批次；共同风格落实到世界规则和设计语言，保留各领域与角色差异。人物专属分析由角色子插件完成，场景按场景子插件准则推进，道具保留其选案和主视觉规则。

## 安装与开始

需要 Python 3.12+、Codex CLI 和当前用户的可用模型配置。包内 Python 依赖通过 `requirements.lock` 固定；缺少依赖时按启动器提示安装到用户缓存。

本公开测试版从[统一公开市场](../README.md#安装)安装，或下载 [r3 完整测试包](https://github.com/kaibaoxiang-studio/script-assets-public-test/releases/tag/public-test-2026-10-27-r4)，解压后在测试包根目录运行 `python3.12 scripts/install.py`。随后可在本资产插件目录运行 `python3.12 harness.py doctor`。

公开市场的资产入口为 `asset-design@script-assets-public-test`。旧标签安装者按首页先更新市场注册和资产插件缓存。安装后新开聊天刷新入口列表；母包已包含锁定的角色、场景、道具目录，原有独立安装可并存。

调用示例：

```text
请使用 $asset-design，读取这份标准化剧本和资产表，先建立全剧理解与美术基准，
本轮统筹 CHR-001、SCN-002 和 PRP-003，检查它们的使用、尺度与风格关系。

请使用 $asset-scene，只深化 SCN-002 当前已确认布局的光影，不重做其他资产。
```

正式剧本标准化、场记和资产提取由独立剧本插件提供。本插件接受这些产物；只有原始剧本时也可分析和提出临时工作清单，临时标识不冒充正式资产 ID。

## 工作流

```mermaid
flowchart TD
    A[剧本与正式资产表／已有项目] --> B[阅读全文并记录来源覆盖]
    B --> C[全剧理解与资产关系轻规划]
    C --> D[项目美术基准与当前批次方向]
    D --> E{用户确认共同基准}
    E --> F[按真实依赖拆分领域任务]
    F --> G[角色子插件]
    F --> H[场景子插件]
    F --> I[道具子插件]
    G --> J[实际成果与来源记录]
    H --> J
    I --> J
    J --> K[总控检查交互与风格并记录采用]
    K --> L[各领域保留设计／图片审批]
    L --> M[统一资产索引与原领域交付物]
    K --> N[冲突与未决项]
    N --> F
```

总控采用只表示该成果可用于整合。设计选案、阶段批准和具体图片定稿仍在对应领域记录。提示词已交、等待回图、领域批准与受变更影响待复核会分别展示。

## 时序图

```mermaid
sequenceDiagram
    actor U as 用户
    participant M as 资产设计总控
    participant L as 项目台账
    participant R as 隔离临时执行器
    participant D as 角色／场景／道具子插件
    U->>M: 指定跨资产范围与来源
    M->>L: 保存真实阅读覆盖、理解与关系
    M->>U: 共同美术基准与关键取舍
    U->>M: 确认基准
    M->>L: 记录版本与确认
    M->>R: 按依赖派发具体任务
    R->>D: 读取锁版入口、知识与相关语境
    D-->>R: 实际设计文件、决定与未决项
    R-->>L: 运行记录与文件哈希
    M->>L: 核对后采用或退回
    M-->>U: 连贯推荐及当前交付
    U->>D: 按领域规则选案／回图／确认
    D-->>L: 可核对的原批准记录与交付引用
    M-->>U: 统一资产索引
```

内部派发使用临时执行会话，不创建用户侧的新聊天。独立任务可以并行；任务完成后由总控查看真实文件并记录采用，再推进其依赖项。某项失败或缺资料只暂停相关任务，不能用模拟结果代替。

## 数据流图

```mermaid
flowchart LR
    S[剧本原文与来源哈希] --> C[全剧上下文与阅读覆盖]
    T[正式资产表／原项目] --> C
    C --> V[版本化项目美术基准]
    C --> G[资产关系与任务依赖]
    V --> Q[目标批次领域交接]
    G --> Q
    Q --> B[锁版子插件与知识]
    B --> O[原领域设计／提示词／审查文件]
    O --> A[总控采用记录]
    P[原领域用户批准记录] --> X[统一资产索引]
    O --> X
    A --> X
    G --> X
    Z[来源或基准变更] --> R[受影响项待复核]
    R --> G
    R --> X
```

源资料、推导、创作选择和新增设定分别记录。来源更新保留历史，标记受影响项目；总控不会用一条批准覆盖所有领域。已有角色项目通过显式导入核对来源版本、稳定 ID 与文件哈希，保留能验证的批准。

## 项目命令与数据

```sh
python3 harness.py init --project /absolute/project --script /absolute/screenplay.json --assets /absolute/assets.json
python3 harness.py status --project /absolute/project
python3 harness.py index --project /absolute/project
```

完整命令和阶段操作见 [工作流](references/workflow.md)，数据合同见 [接口](references/interfaces.md)。阅读覆盖由模型实际阅读后提交；结构校验只能证明记录完整，不能代替人物、空间和道具设计质量的检查。母插件以文字设计和提示词为主要交付，实际图像按各子插件规则回流与审批。

## 封装与验证

| 子插件 | 锁版版本 | 主要入口 |
| --- | --- | --- |
| 角色资产插件 | v0.2.13 | `character-assets` |
| 场景资产插件 | v0.9.5 | `sence-prompts` |
| 道具资产插件 | v0.2.5 | `prop-concept-design` |

本轮三类业务来源为 ZiChan 提交 `e089d1287c1499f08c42e75aca093131e9d3fbc0`，提交及逐文件哈希保存在 [bundle-lock.json](bundle-lock.json)，原目录、知识引用与来源声明随包保留。每次公开测试更新显式核对权威来源、锁版并检查兼容，不由旧母包版本推定领域内容。封装说明见 [来源追溯](references/package-provenance.md)及 [第三方来源](THIRD_PARTY_NOTICES.md)。

```sh
python3 harness.py validate
python3 -m unittest discover -s tests -v
```

2026-10-23 母插件原发布验证覆盖四入口、封装哈希、来源与 ID、审批保留、依赖调度、局部失效和临时执行隔离，并对当时三领域快照做过真实文字调用；记录见 [原 v0.1.0 验证](validation/v0.1.0.md)与[原真实调用报告](validation/real-call-report.json)。本轮更新快照的检查见[公开镜像验证](../public-validation.json)，完整项目与图片审美由使用者测试。
