# 上游来源

- Bird's Nest / Skill Orchestrator 0.8.0，eggshrt/Bird-s-Nest，提交 `3f5a5f348c2f71b3c5c046128e0c679089ab801a`，MIT。Grill Me 原样收录；运行时借鉴并重写其事件存储、DAG 调度和 App Server 客户端，移除剧本/单资产耦合并增加通用能力执行、文件校验和建设工具。许可见 `licenses/Bird-s-Nest-MIT.txt`。
- OpenAI Skill Creator，本机随 Codex 提供的版本，Apache-2.0。Skill 编写与增量维护规范参考其指导原则，未将系统 Skill 作为运行依赖。许可见 `licenses/skill-creator-Apache-2.0.txt`。
- Python 第三方库版本与发行文件哈希见 `requirements.lock`；安装时保留各库自身的许可证。

生成插件默认携带此说明和上游许可。额外吸收的开源代码由 `sources.lock.json` 和相应 licenses 文件单独记录。

## 角色图片方法

角色出图提示词与修图知识快照参考了用户提供的 `刺猬星球/01-通用图片生成` 中 `SKILL.md` 和 `references/prompting.md`，按角色资产工作流重新编写。源目录附 Apache License 2.0，许可证文本见 `licenses/hedgehog-general-image-Apache-2.0.txt`。本插件未复制源 Skill、API/CLI 脚本或示例提示词。

具体文件 SHA-256、采用范围与改写说明见 `knowledge/source-register.json` 和 `sources.lock.json`。来源 Skill 与本机内置 `imagegen` Skill 主体几乎相同，因此这里只携带角色业务规则，不另装一套通用生图能力。
