# 场景资产插件 v0.9.5

本插件包装了 [`$sence-prompts`](skills/sence-prompts/SKILL.md) 的当前维护版 **v0.9.5**，包含 352 个技能文件。Skill 名称沿用作者原拼写。插件包与技能包统一使用 **v0.9.5**；后续发布时，两份插件配置中的 `version` 与 `SKILL.md` 的 `metadata.version` 必须一致，相关版本说明同步更新。发布包仅将维护入口的个人电脑路径替换为可移植的定位说明，其余技能文件与维护源码一致。

本次同步保留三步流程，更新整体空间与场所规格、适用构造／装饰／使用细节、光影增强与转化、首稿实体关系预检，以及对应回归资料。检查通过表示文件与脚本验证通过，不代表所有行为用例或生图效果已验证。

## 能做什么

- 根据完整场景资产表和对应剧本，主动设计中文静态场景提示词；保留原资产 ID、名称与子场景粒度。
- 在已有可靠场景基准上深化光影氛围并给色卡，或设计反打与其他角度。
- 对已确定场景做局部修改和纹理修复，并守住空间布局、材料本色、光源及相机关系。
- 区分剧本事实、已确认选择、设计提案与未知；同一场景不同状态和角度分别交付。

插件不负责资产提取、视频分镜、自动生图或置景施工。第一步、第二步、第三步和局部修改的输入、知识加载与验收要求均在 [Skill 入口](skills/sence-prompts/SKILL.md)及其 `references/` 中。

## 安装

在 ZiChan 仓库根目录注册统一市场并安装：

```sh
codex plugin marketplace add "$PWD"
codex plugin add scene-assets@zichan-suite-local
```

若只安装 Skill，也须完整复制 `skills/sence-prompts/`，不能只复制 `SKILL.md`。第二步色卡绘制需要 Python、Pillow 与可用的中文字体；纯文字提示词不依赖绘卡环境。

## 使用示例

```text
$sence-prompts 依据这份场景资产表与剧本，按原资产 ID 设计静态场景提示词。
先区分剧本事实与设计提案，再给每个场景的一稿完整提示词。
```

已有可靠的场景图或文字基准时，可以直接要求光影深化、反打、多角度或局部调整，不必重做首稿。图片生成仍由操作者在外部工具完成；实际回图应作为下一轮审查依据。

## 维护与来源

当前唯一正式技能目录为 `skills/sence-prompts/`。其 [`tests/index.md`](skills/sence-prompts/tests/index.md) 给出受影响范围的验证入口；脚本检查入口为 `skills/sence-prompts/scripts/check_skill_files.py`。旧场景 Harness 实现、历史构建脚本和旧 ZIP 保留在[整理前 Git 提交](https://github.com/kaibaoxiang-studio/ZiChan/tree/60e04bf1b45763bacb88ffbdc2bd6f5a96666bed)，不属于当前插件安装内容。
