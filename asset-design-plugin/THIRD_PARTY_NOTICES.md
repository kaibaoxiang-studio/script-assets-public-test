# 来源与许可说明

本安装包包含开宝箱工作室 `ZiChan` 仓库中三个子插件的固定快照，本轮领域来源提交为 `e089d1287c1499f08c42e75aca093131e9d3fbc0`。逐文件来源、Git blob、SHA-256 和文件权限记载在 `bundle-lock.json`。

| 子插件 | 版本 | 保留位置 |
| --- | --- | --- |
| 角色资产插件 | 0.2.13 | `bundled-plugins/character-assets/` |
| 场景资产插件 | 0.9.5 | `bundled-plugins/scene-assets/` |
| 道具资产插件 | 0.2.5 | `bundled-plugins/prop-assets/` |

角色资产插件的上游方法与许可说明原样保留在 [子插件第三方说明](bundled-plugins/character-assets/THIRD_PARTY_NOTICES.md)，相关 MIT 与 Apache-2.0 文本保留在其 `licenses/` 目录。子插件中的知识来源、参考资料和归属说明随快照完整保留。

本文件不为未附公开许可的内容新增许可，也不改变各原始许可条款。本公开测试镜像及其安装包经维护方授权用于外部测试；源码公开可读不等于为原始第三方资料新增开源许可。

母插件 `runtime/asset_core/appserver.py` 基于该锁版角色插件中的 App Server 客户端改编，用于隔离的临时领域调用。原客户端上游为 Bird's Nest / Skill Orchestrator 0.8.0（`eggshrt/Bird-s-Nest`，提交 `3f5a5f348c2f71b3c5c046128e0c679089ab801a`），MIT。原版权与完整许可保留于 [Bird's Nest MIT 许可](bundled-plugins/character-assets/licenses/Bird-s-Nest-MIT.txt)。母插件的领域交接与项目台账是本次新增适配。

Python 第三方库按 [requirements.lock](requirements.lock) 的版本与发行文件哈希安装，未将依赖包重新许可；安装时保留各发行包自身的许可。

## 公开镜像变换

本镜像母层外壳沿用 v0.1.0；角色、场景、道具的业务与知识更新为上述 ZiChan 提交，并保留该提交的 manifest 版本与原有许可。剧本业务权威来源为 [script-plugins](https://github.com/kaibaoxiang-studio/script-plugins)。对开发机来源路径、真实项目标识及历史会话记录的匿名化与领域来源更新分别记录。逐文件原始／公开导出散列及原因见 `public-export-manifest.json`；`bundle-lock.json` 的 `sha256` 校验公开导出字节，`upstream_sha256` 与来源 Git blob 记录上游字节。
