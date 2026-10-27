# 焦点与三维形体交接 v0.2.5

本方法服务于已确认项目美学与 [人物设计意图](director-understanding.md)。少量焦点与剪影检查是启发，不是机械配额。剧情事实、行动与观众信息优先；不把五官、体型、伤痕固定映射成品格，也不默认美型、疤痕、痣或夸张长腿。

## 当前路由与分阶段执行

先完成全文理解、人物定位和方向稿，再规划十三项 `inline|independent|defer|not_needed`。特征聚焦与身份一起解决，身体比例、颅胸盆体块和动作在 body 阶段深化。常规主控真实执行规范，复杂冲突独立会诊；用 [专项合同](specialist-contract.md) 记录实际成果，不能以写已调用模拟执行。尚未开始身体不等于无需身体设计。

## 身份阶段的焦点

`feature_focus` 包含 `core_sentence,primary_anchors,quiet_features,imperfection_policy,view_checks`。core_sentence 来自人物设计意图；锚点含 `part,geometry,basis,visible_views`，通常少量，需要其他数量时写 `anchor_count_rationale`。安静区含 `part,decision`，保持普通也要可画，不必故意变丑。

`imperfection_policy{status:none|existing|operator_approved,detail,basis}` 可以明确不新增瑕疵。普通痣雀斑可随首稿整体审阅；有新经历含义的伤痕等显式决定。`view_checks` 的 silhouette/occlusion 各为 `{status:passed|failed|not_tested,evidence}`，没有实际视图保持 not_tested，不能因写了剪影描述就报告实图通过。

## 身体阶段的比例和体块

`body_form` 含 `proportions,masses,views,action_check,proportion_anchors`。比例写躯干/腿、臂段、腿段的相对关系；体块写颅、胸、盆及连接；正侧背解释同一骨架；动作写站姿、原文动作、活动能力判断与检查状态。没有图像或关键姿态时为 not_tested。性格可以通过获选的常态姿态暗示，不能证明某种骨相或永久身体缺陷。

`proportion_anchors` 的 `measurement_frame` 写姿态、鞋履和测量端点；`head_body,shoulder_hip,torso_legs,arm_segments,leg_segments` 各为 `{mode:numeric|landmark,reference_points:[至少两个明确部位],relation,basis}`。head_body 给约数或范围的头高/全高；其余可用数值或可定位骨点。上段/下段可用第7颈椎至臀纹与臀纹至足底，也可选另一体系，但端点必须一致。relation 逐字包含 reference_points，便于交接。

`visual_details.body.frame_proportions` 呈现头身、肩胯与躯腿；`body_form.proportions` 各组同步。全身提示词逐字继承前三组关系，验收至少核对头身与躯腿。165cm/48kg只记录事实，不能据此推算头身比或长腿。例子数值不成为全剧默认。

头像阶段可以留下后续形体方向与稳定身份约束，但不强制提前完成这五组数值；进入 full_body 前 body 快照须完整确认。非人按实际部件适配，不能强套人体。

## 合成与历史边界

V2.5合成身份与身体的已批准快照，冲突先解决；完整细节不等于所有焦点都挤进提示词。头像只提可见身份，身体图核比例，侧背/动作无法判断则未验证。

旧V2.2/V2.4和 CharacterSpecialistRouteV1 的11/13项 invoke/skip、used提案映射继续原合同。缺比例锚点的旧卡若要新做全身，应先补为待审设计并更新，不能在提示词环节猜数。升级不自动推翻旧批准或要求重画。
