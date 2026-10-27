# 安装与运行

## 从统一公开测试仓库安装

本目录是来源提交 `c1a101d87cd2d35f8c92ac382ed34e3860fb046e` 的公开测试快照。统一安装、资产设计插件和反馈说明见[测试仓库首页](../../README.md)。使用支持插件功能的 Codex：

```sh
codex plugin marketplace add https://github.com/kaibaoxiang-studio/script-assets-public-test.git --ref public-test-2026-10-27
codex plugin add screenplay-standardizer@script-assets-public-test
codex plugin add scene-log-extractor@script-assets-public-test
codex plugin add screenplay-asset-extractor@script-assets-public-test
```

也可以在 Codex 插件目录中打开统一公开测试市场并逐项安装。需要建设或维护插件时，再安装额外工程：

```sh
codex plugin add harness-creator@script-assets-public-test
```

固定标签 `public-test-2026-10-27` 对应本轮公开测试。跟随后续测试镜像时改用 `--ref main`。来源组件版本保持原值，镜像标签单独标识测试批次。市场结构与 Git 引用参数遵循 [Codex 官方插件文档](https://developers.openai.com/plugins/build/plugins)。

## 在聊天中使用

1. 选择「剧本标准化」，提供 DOCX、TXT 或 Markdown。说明是已有剧本还是纯细纲；默认轻审，需要跨集审查时明确要求深审。
2. 确认一级交付的 标准化剧本.json 和独立疑点报告。
3. 「场记表提取」读取一级 JSON；「剧本资产表提取」可调用 `script-asset-extractor` v0.1.1 读取标准 DOCX，也可调用 `extract-asset-table` 兼容入口读取一级 JSON。两个二级插件可以分别运行。
4. 检查报告中的疑点、来源提示和待审制作建议，再确认最终业务交付。

一级 Markdown 用于阅读。场记表和资产表 JSON 兼容入口的输入为 `standardized_screenplay_v1` JSON。剧本资产表提取的外层插件仍标为 v0.1.0，包含最新 DOCX Skill v0.1.1。向资产设计母插件交接时，优先提供相互匹配、保留来源哈希的一级 JSON 与资产 JSON；仅有 Excel 时须先核实交接条件。资产表登记图像和声音制作需求；图像设计与生成由统一测试仓库中的资产设计插件处理。

## Python 与命令行

四个组件都带有自己的 Harness runtime、Skill、知识和 requirements.lock。运行 Python 脚本需要 Python 3.12+；运行 Agent 能力还需要可用并已登录的 Codex CLI。Python 依赖安装与 Agent 调用分别消耗本机环境及对应账号资源。

先进入要用的插件根目录，或设置其绝对路径。以下以一级插件为例；解压独立 ZIP 后也可同样操作：

```sh
plugin_root="/absolute/path/script-plugins/level-1/screenplay-standardization/screenplay-standardizer"
python3.12 "$plugin_root/scripts/bootstrap.py" --install
```

bootstrap 按锁定版本与哈希在用户缓存中准备环境。将最后返回的 JSON 中的 `python` 路径填入下例：

```sh
runtime_python="/absolute/path/returned/python"
"$runtime_python" "$plugin_root/harness.py" doctor
"$runtime_python" "$plugin_root/harness.py" validate --plugin "$plugin_root"
```

每个插件执行一次自己的 bootstrap；依赖锁不同，缓存路径可能不同。

### 一级标准化

新建 `standardize-inputs.json`，将 source_path 改为实际输入文件的绝对路径：

```json
{
  "source_path": "/absolute/path/input.docx",
  "input_kind": "auto",
  "review_mode": "light"
}
```

```sh
"$runtime_python" "$plugin_root/harness.py" run-capability \
  --plugin "$plugin_root" --capability standardize-screenplay \
  --inputs /absolute/path/standardize-inputs.json \
  --workspace /absolute/path/standardize-work --confirmed
```

独立审查可改用 `review-screenplay`，输入只需 source_path、review_mode。输出位置见运行结果中的 artifacts；运行状态保存在指定 workspace 的 .harness 下。

### 二级场记表

切换至场记插件自己的 Python 环境和插件路径，可用整剧入口：

```sh
plugin_root="/absolute/path/script-plugins/level-2/scene-log-extraction/scene-log-extractor"
"$runtime_python" "$plugin_root/scripts/run_scene_log.py" \
  --source /absolute/path/标准化剧本.json \
  --workspace /absolute/path/scene-log-work \
  --output /absolute/path/scene-log-output
```

默认整剧；加 `--episodes 2,3` 指定集。续跑要求输入文件内容、插件内容与 workspace 保持一致，改用 `--resume run-运行编号`。同版本下修改插件文件也会使内容指纹变化。详见[场记组件 README](../level-2/scene-log-extraction/README.md)。

### 二级资产表

标准 DOCX 主入口：在聊天中调用 `$script-asset-extractor`，提供标准剧本 DOCX 并说明输出目录。该入口的 v0.1.1 规则涵盖四表 Excel、人物排序与保存后验收。

以下为一级 JSON 兼容入口，适用于与资产设计母插件保持来源哈希的交接。切换至资产插件的 Python 环境，新建 `asset-inputs.json`：

```json
{"source_path": "/absolute/path/标准化剧本.json"}
```

```sh
plugin_root="/absolute/path/script-plugins/level-2/asset-extraction/screenplay-asset-extractor"
"$runtime_python" "$plugin_root/harness.py" run-capability \
  --plugin "$plugin_root" --capability extract-asset-table \
  --inputs /absolute/path/asset-inputs.json \
  --workspace /absolute/path/asset-work --confirmed
```

四个交付物及范围见[资产组件 README](../level-2/asset-extraction/README.md)。

## 独立下载

[公开测试 Release](https://github.com/kaibaoxiang-studio/script-assets-public-test/releases/tag/public-test-2026-10-27) 提供本轮独立 ZIP、文件清单和 SHA256SUMS.txt。ZIP 顶层是插件名，解压后包含完整运行文件；无需回到 creator-src 或另装 Harness Creator。源码和测试材料保存在仓库，独立 ZIP 侧重安装运行。组件来源与内容差异见[测试仓库首页](../../README.md)。
