# 来源与公开测试分发

本仓库由开宝箱工作室为 2026-10-27 外部测试建立，当前固定标签为 `public-test-2026-10-27-r4`。本轮记录三类来源及其逐文件公开导出哈希：

| 负责内容 | 权威来源 | 本轮固定提交 |
| --- | --- | --- |
| 剧本标准化、场记、资产表 | [script-plugins](https://github.com/kaibaoxiang-studio/script-plugins) | `b1f232c743a927a4f7c94f02c1dede2fab4e49a0` |
| 角色、场景、道具业务与知识 | [ZiChan](https://github.com/kaibaoxiang-studio/ZiChan) | `e089d1287c1499f08c42e75aca093131e9d3fbc0` |
| 资产母插件总控外壳 | [asset-design-plugin](https://github.com/kaibaoxiang-studio/asset-design-plugin) | `2c4a66669ced1d2ee2cc8cd1c1636c09e67599bf` |

母插件版本保持 0.1.0。本轮公开包将其旧封装的业务快照更新为指定 ZiChan 提交，角色为 0.2.13、场景为 0.9.5、道具为 0.2.5；这不代表对私有母仓库进行新正式发布。旧公开测试标签仍保留历史内容。

公开导出对本机绝对路径、历史聊天／日志定位符、项目名称和短反馈摘录作匿名化，并同步对应文件锁。领域业务变化来自权威来源提交；各组件功能版本沿用来源 manifest。来源与变换可从 `mirror-sources.json` 及资产组件 `public-export-manifest.json` 复核。

各组件已有的许可证、第三方说明、来源归属和使用边界随包保留。本轮没有给原始课程、私有素材或第三方依赖新增统一许可。原始业务剧本、图片、DOCX 与完整日志不包含在本测试镜像。

- [剧本工程来源说明](script-plugins/NOTICE.md)
- [资产组件来源说明](asset-design-plugin/THIRD_PARTY_NOTICES.md)
