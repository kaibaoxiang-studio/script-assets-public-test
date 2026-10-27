"""Minimal real child calls; never substitutes fake outputs for business design.

Usage: python tests/run_real_validation.py --output /absolute/test-project [--run]
The fixture baseline is a development test constraint, not approval of user assets.
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from asset_core.common import sha
from asset_core.project import Project
from asset_core.runner import run

def prepare(output):
    fixtures=Path(__file__).parent/'fixtures'
    project=Project(output)
    project.init(fixtures/'screenplay.json',fixtures/'assets.json')
    chunks=project.state['chunks']
    project.submit_context({'schema_version':'AssetProjectContextV1',
        'source_sha256':sha(fixtures/'screenplay.json'),'coverage':[c['id'] for c in chunks],
        'story_summary':'海堤旁修理工林禾被邵叔评价为胆怯，却承担送铜闸钥匙任务，夜里把防水披肩留给孩子，自己进入暴雨。外界评价与行动形成反差。',
        'world_rules':['剧本明确海堤、暴雨、修理铺、低工作台、铜闸钥匙和旧帆布；未明确历史年代和科技上限。'],
        'cross_asset_design':['手握钥匙和擦齿槽需要可信手持尺度；工作台及出入口需要支持修理、放置和出发。空间保持剧本狭长条件。'],
        'evidence':[{'chunk_id':chunks[-1]['id'],'observation':'邵叔的胆怯评价不是叙述对林禾人格的结论，后场主动保护孩子表现担当。','kind':'script_fact'},
                    {'chunk_id':chunks[-1]['id'],'observation':'潮湿盐雾可以影响材料表面；具体磨损分布仍属设计推导。','kind':'inference'}],
        'hidden_information':['不添加家族、宗教、战斗经历或钥匙隐藏功能；剧本没有这些事实。']})
    project.submit_baseline({'schema_version':'AssetVisualBibleV1','context_revision':1,
        'style_intent':'测试用写实影视设计方向：克制、有生活使用痕迹，结构清楚，拒绝广告式精修；时代科技暂以可信手工作业可见信息呈现。',
        'world_rules':['保留海堤旁狭长修理铺及低矮工作台；不添加超自然功能。'],
        'material_logic':['铜钥匙局部握持接触面与齿槽潮湿有差异；木作与织物不统一刷旧。'],
        'color_light':['黄昏到雨夜，保留材料固有色；冷环境和有限工作光分层，不以全蓝染色代替设计。'],
        'symbol_language':['以工具接触和修理逻辑组织结构，不给三个领域贴同一标志。'],
        'domain_constraints':{'character':['林禾实际行为有担当；身份首稿不使用他人评价作为怯懦固定姿态。'],
            'scene':['遵循场景子插件准则；场景文本只深化黄昏一个时刻。'],
            'prop':['保留铜制及需擦干齿槽；建议尺寸需标待确认，不新增功能。']},'open_questions':[]})
    project.approve_baseline(1,'开发验证夹具专用基准；依据本轮已授权最小文字调用测试采用，不构成任何用户项目资产批准。')
    tasks=[
        {'id':'character','domain':'character','asset_id':'CHR-001','state_id':'S01','skill':'character-design',
         'objective':'仅为测试首稿输出林禾人物理解与identity头像阶段文字推荐 design.md。实际阅读全文和相关知识，保留行为与他评反差，具体设计原创脸部主次、发型和自然肤质。独立文字首稿无需创建正式角色项目；身体衣装留方向，不出图，不写批准。输出必要知识文件相对child_root路径。'},
        {'id':'scene','domain':'scene','asset_id':'SCN-001','state_id':'S01',
         'objective':'为潮门修理铺黄昏单一时刻做第一步场景文字设计与完整中文静态提示词 design.md。实际加载场景所需参考。保留狭长和低工作台，以可见实体说明工作、放钥匙和通行关系；不添加正式资产、不写成图审核、不出图。'},
        {'id':'prop','domain':'prop','asset_id':'PRP-001','state_id':'S01',
         'objective':'仅完成铜闸钥匙P1-P2文字首稿 design.md。按子插件形成需求与三套有实质轮廓/结构差异的候选，给推荐但保留待用户选择；建议尺寸标待确认，保留铜制和可擦齿槽，不增加钥匙功能。不写最终Prompt，不出图，不批准。'}]
    for t in tasks:
        t.update(depends_on=[],context={'test_only':True},constraints=['仅当前文字阶段；不得伪造用户选择或成图'],deliverables=['design.md'])
    project.plan({'tasks':tasks})
    return project

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--run',action='store_true')
    a=p.parse_args(); project=prepare(a.output)
    if a.run: run(project,3,900)
    import json
    print(json.dumps(project.status(),ensure_ascii=False,indent=2))
