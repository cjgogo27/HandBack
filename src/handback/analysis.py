"""Recompute released tables without a model, simulator, network or GPU.

This verifies the derived evidence package. It does not regenerate raw trajectories.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

METHODS = ('U', 'B', 'F4', 'Fbest', 'S1', 'S2', 'V')
LABELS = {'U': 'No further update', 'B': 'Replay only', 'F4': 'Fixed 4',
          'Fbest': 'Dev-selected fixed 1', 'S1': 'First support',
          'S2': 'Two scheduled supports', 'V': 'Learning-value exit'}

def load(path):
    return json.loads(Path(path).read_text(encoding='utf8'))

def jsonlines(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf8').splitlines() if line.strip()]

def read_rows(path):
    with Path(path).open(encoding='utf8', newline='') as f:
        rows = list(csv.DictReader(f))
    int_keys = ('seed','original_predicate','complete_and_held','joint_1mm','joint_2mm','joint_5mm','infrastructure_retry')
    for row in rows:
        for k in int_keys:
            row[k] = int(row[k])
        row['external_depth_mm'] = float(row['external_depth_mm'])
    return rows

def aggregate(rows):
    counts = {}
    assert len(rows) == 84 and len({(r['method'],r['seed']) for r in rows}) == 84
    for method in METHODS:
        group = [r for r in rows if r['method'] == method]
        assert sorted(r['seed'] for r in group) == list(range(4062104001,4062104013))
        for r in group:
            assert all(r[k] in (0,1) for k in ('original_predicate','complete_and_held','joint_1mm','joint_2mm','joint_5mm','infrastructure_retry'))
            assert 0 <= r['external_depth_mm'] < 1000
            assert r['complete_and_held'] <= r['original_predicate']
            for mm in (1,2,5):
                assert r[f'joint_{mm}mm'] == int(r['complete_and_held'] and r['external_depth_mm'] <= mm)
        counts[method] = dict(n=len(group), original_predicate=sum(r['original_predicate'] for r in group),
            complete_and_held=sum(r['complete_and_held'] for r in group),
            **{f'joint_{mm}mm':sum(r[f'joint_{mm}mm'] for r in group) for mm in (1,2,5)},
            deep_over_5mm=sum(r['external_depth_mm'] > 5 for r in group))
    return counts

def bounds(rows, interruption):
    partial = {(r['name'],r['seed']):r['original_partial_contact']['observed_external_depth_lower_bound_m']
               for r in interruption['interrupted_reexecution_comparisons']}
    assert len(partial) == 3
    result = {}
    for method in METHODS:
        complete = [r for r in rows if r['method']==method and (method,r['seed']) not in partial]
        observed = [v for (m,_),v in partial.items() if m==method]
        known = sum(r['joint_2mm'] for r in complete)
        result[method] = dict(joint=[known,known+sum(v<=.002 for v in observed)],
            deep=[sum(r['external_depth_mm']>5 for r in complete)+sum(v>.005 for v in observed),
                  sum(r['external_depth_mm']>5 for r in complete)+len(observed)])
    return result

def verify(root):
    root = Path(root)
    data = root/'data'
    manifest = load(data/'export_manifest.json')
    for item in manifest['records']:
        p = root/item['public_file']
        assert p.is_file(), f'Missing exported file: {p}'
        if 'public_sha256' in item:
            assert hashlib.sha256(p.read_bytes()).hexdigest() == item['public_sha256'], f'Export hash mismatch: {p}'
    rows = read_rows(data/'stage_a.csv')
    counts = aggregate(rows)
    recorded = load(data/'recorded_stage_a.json')
    for m in METHODS:
        for key in ('n','joint_1mm','joint_2mm','joint_5mm','deep_over_5mm'):
            assert counts[m][key] == recorded['counts'][m][key]
        assert counts[m]['complete_and_held'] == recorded['counts'][m]['raw']
    audits = {r['public_episode_id']:r for r in jsonlines(data/'contact_audits.jsonl')}
    predicates = {r['public_episode_id']:r for r in jsonlines(data/'predicate_audits.jsonl')}
    assert len(audits)==len(predicates)==84
    for r in rows:
        key = f"{r['method']}_{r['seed']}"
        a,p = audits[key],predicates[key]
        assert abs(a['maximum_external_robot_penetration_m']*1000-r['external_depth_mm']) < 1e-9
        assert bool(a['raw_complete_and_held']) == bool(r['complete_and_held'])
        assert bool(a['joint_2mm']) == bool(r['joint_2mm'])
        assert a['native_loss_false'] and a['independent_contact_recomputation']
        assert a['protocol_cutoff_step'] == a['control_samples']-20
        assert p['independent_predicate_reconstructed'] and p['runtime_flags_used_as_input'] is False
        assert bool(p['terminal']['success']) == bool(r['original_predicate'])
        assert len(p['registered_ten_holds'])==10
    from .selector import crossfit, select
    selection = load(data/'selection.json')
    records = selection['features']
    for rec in records:
        for k in ('features','values','supported'):
            rec[k] = {int(a):b for a,b in rec[k].items()}
    learned = crossfit(records)
    for rec,fold in zip(records,learned['folds']):
        at = lambda k:dict(feature=rec['features'][k],supported=rec['supported'][k])
        for method in ('V','S1','S2'):
            d = select(at,method,fold['models'] if method=='V' else None)
            expected = next(r for r in selection['methods'][method] if r['parent']==rec['parent'])
            for key in ('retained_k','handoff','read_prefixes'):
                assert d[key]==expected[key], f'Selection mismatch {method}/{rec["parent"]}'
    mech = load(data/'mechanism_audit.json')
    assert mech['V_S1']['same_realized_training_targets_order_replay_and_hyperparameters']
    assert mech['methods']['V']['training_schedule'] == mech['methods']['S1']['training_schedule']
    assert mech['methods']['V']['realized_training_schedule_sha256'] == mech['methods']['S1']['realized_training_schedule_sha256']
    first = bounds(rows,load(data/'interruption_audit.json'))
    with (data/'first_attempt_bounds.csv').open(encoding='utf8',newline='') as f:
        for r in csv.DictReader(f):
            assert first[r['method']]['joint'] == [int(r['joint_success_lower']),int(r['joint_success_upper'])]
            assert first[r['method']]['deep'] == [int(r['deep_5mm_lower']),int(r['deep_5mm_upper'])]
    differences = {m:counts['V']['joint_2mm']-counts[m]['joint_2mm'] for m in ('Fbest','S1','S2')}
    gain = all(v>=2 for v in differences.values())
    physical = counts['V']['deep_over_5mm'] <= counts['Fbest']['deep_over_5mm']
    assert gain == recorded['predeclared_gain_gate'] and physical == recorded['predeclared_deep_contact_gate']
    assert not gain and not physical and not recorded['proceed_to_frozen_stage_B']
    costs=load(data/'costs.json')
    development=costs['actual_value_estimation_and_replay_control_training']
    pooled=costs['method_specific_pooled_training']
    assert len(development)==20 and sum(a['optimizer_steps'] for j in development for a in j['arms'])==100
    assert len(pooled)==6 and sum(a['optimizer_steps'] for j in pooled for a in j['arms'])==144
    assert costs['teacher_acquisition_shared_once']['teacher_full_client_wrapper']['calls']==85
    assert costs['future_actual_completed_and_original_partial_calls']==1885
    closure=load(data/'closure_verification.json')['completion_verification_v1.json']
    assert closure['logical_units']==84 and closure['native_images_hash_checked']==1844
    assert closure['native_and_raw_artifact_hashes_checked']==2432 and closure['frozen_source_assets_verified']==3679
    pairing=load(data/'model_pairing.json')
    assert len(pairing['by_seed'])==12
    assert all(r['methods']==7 and len(r['unique_compiled_model_hashes'])==1 for r in pairing['by_seed'].values())
    return dict(counts=counts,V_minus_baselines=differences,gain_gate=gain,deep_contact_gate=physical,
        stage_B_executed=False,selection_V_equals_S1=selection['methods']['V'] != [] and
            [(r['retained_k'],r['handoff']) for r in selection['methods']['V']]==[(r['retained_k'],r['handoff']) for r in selection['methods']['S1']],
        first_attempt_bounds=first,logical_units=84,physical_attempts_including_original_partials=87,
        infrastructure_retry_units=sum(r['infrastructure_retry'] for r in rows),
        verification_scope='Recompute released tables and cross-check derived audit evidence; no raw-trajectory or training regeneration')

def tables(summary):
    lines=['| Method | Original predicate | Complete + held | Joint <=1mm | Joint <=2mm | Joint <=5mm | >5mm |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for m,c in summary['counts'].items():
        vals=[c[k] for k in ('original_predicate','complete_and_held','joint_1mm','joint_2mm','joint_5mm','deep_over_5mm')]
        lines.append('| '+m+' | '+' | '.join(str(v)+'/12' for v in vals)+' |')
    lines += ['', 'Includes three infrastructure re-executions; engineering contact thresholds are not hardware safety limits.', '',
              '| Method | Original-attempt joint interval | Original-attempt >5mm interval |', '|---|---:|---:|']
    for m,b in summary['first_attempt_bounds'].items():
        lines.append(f"| {m} | {b['joint'][0]}–{b['joint'][1]} /12 | {b['deep'][0]}–{b['deep'][1]} /12 |")
    return '\n'.join(lines)+'\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.cwd(),help='Repository root containing data/')
    parser.add_argument('--output',type=Path,default=None)
    args=parser.parse_args()
    summary=verify(args.root)
    if args.output:
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
        (args.output/'tables.md').write_text(tables(summary),encoding='utf8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
