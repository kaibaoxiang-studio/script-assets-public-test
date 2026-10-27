---
name: character-image-review
description: "审查回流图片的剧本事实、身份与版式并产报告"
---

# 回图审查

先读 [知识索引](../../knowledge/index.md)，按情景只加载本轮需要的 reference。

必须实际打开目标图片、已定稿头像及设计卡，读取 [审查规则](../../references/review.md)。分别检查原文事实、身份不变量、体型/服装/配饰、格位、中文标签、裁切与背景依据。头像查默认 3:4，全身图查最终像素比例 9:16 与完整头手脚；新项目逐状态执行图查最终像素 9:16、衣装结构与妆面连续性；旧项目按原合同检查服饰设计图和执行图。按当前视角检查批准的主锚点与三维比例，分辨设计卡空泛与回图失真，查看油光、自然肌理、材质层次与伪影。人形执行表左下有嘴唇/头发残留就是错误；右上约 45°，右下完整背面。写 CharacterImageReviewV1，列阻断、待修与可采纳提案；无法看清即 uncertain。提交报告后由操作者明确选图批准，技能不能替代批准。

完整头像预览按 [头像颗粒度规则](../../references/avatar-identity-granularity.md) 逐项对照脸型、分缝发际、眉眼耳鼻唇、皮肤、妆面和饰品决定；实际放大查看额颊颈胸有无重复压印纹、发际有无无根乱丝。会话工具生成的图同样是未批准候选，提示词写了禁令不代表图像已通过。

## Packaged references

- [knowledge/index.md](../../knowledge/index.md)
- [references/review.md](../../references/review.md)
- [references/model-card-baseline.md](../../references/model-card-baseline.md)
- [references/execution-sheet.md](../../references/execution-sheet.md)
- [references/interfaces.md](../../references/interfaces.md)
- [references/render-texture-standard.md](../../references/render-texture-standard.md)
- [references/avatar-identity-granularity.md](../../references/avatar-identity-granularity.md)
- [references/costume-design-stage.md](../../references/costume-design-stage.md)
- [references/knowledge/character-costume-designer/state-makeup.md](../../references/knowledge/character-costume-designer/state-makeup.md)
- [references/knowledge/character-image-review/feature-focus-review.md](../../references/knowledge/character-image-review/feature-focus-review.md)
- [references/knowledge/character-image-review/anti-stereotype-texture.md](../../references/knowledge/character-image-review/anti-stereotype-texture.md)
