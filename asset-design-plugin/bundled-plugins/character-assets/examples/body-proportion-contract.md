# 身体比例交接样例（待审设计，不是人体默认值）

本页演示字段颗粒度。示例里的 7.2 个头高与 47% 是**待审创作选择**，不能从身高、体重或“瘦高型”推算，也不能直接套给其他角色。角色设计卡须在操作者选择后才可批准。

```json
{
  "body_form": {
    "proportion_anchors": {
      "measurement_frame": "去鞋正立，以头顶至足底为全高，从正面核对骨点落位。",
      "head_body": {
        "mode": "numeric",
        "reference_points": ["头顶至足底", "头顶至下颏"],
        "relation": "头顶至足底约为头顶至下颏的7.2倍",
        "basis": "角色身体造型的待审设计选择，非剧本测量"
      },
      "shoulder_hip": {
        "mode": "landmark",
        "reference_points": ["双肩峰外缘", "骨盆外缘"],
        "relation": "双肩峰外缘宽度略窄于骨盆外缘宽度",
        "basis": "角色剪影的待审设计选择"
      },
      "torso_legs": {
        "mode": "numeric",
        "reference_points": ["裆点至足底", "头顶至裆点"],
        "relation": "裆点至足底约占全高47%，短于头顶至裆点",
        "basis": "腿身关系的待审设计选择"
      },
      "arm_segments": {
        "mode": "landmark",
        "reference_points": ["肘尖", "自然腰线", "腕骨"],
        "relation": "肘尖与自然腰线齐平，腕骨落在髋部下缘",
        "basis": "站姿与握笔动作的待审设计选择"
      },
      "leg_segments": {
        "mode": "landmark",
        "reference_points": ["裆点", "膝中心", "踝中心"],
        "relation": "膝中心略高于裆点至踝中心的中点",
        "basis": "下肢体块的待审设计选择"
      }
    }
  }
}
```

正式卡的 `visual_details.body.frame_proportions` 应出现头身、肩胯、躯腿三项 `relation` 原文；`body_form.proportions.torso_legs/arm_segments/leg_segments` 应分别出现对应关系。全身提示词的每个候选复述头身、肩胯、躯腿关系，`acceptance_checks` 至少逐项核头身和躯腿。这样即使删掉身高体重，画师仍知道哪个长度与哪个骨点比较。侧面与背面延用同一骨架；回图若被衣装或透视遮挡，审查标记未验证。
