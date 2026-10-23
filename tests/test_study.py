import copy
from pathlib import Path
import unittest
import numpy as np
from handback.analysis import aggregate, bounds, load, read_rows, verify
from handback.contacts import raw_peaks
from handback.features import public_features
from handback.selector import select, self_test
from handback.support import encode_action

ROOT=Path(__file__).resolve().parents[1]

class StudyTests(unittest.TestCase):
    def test_complete_reproduction(self):
        s=verify(ROOT)
        self.assertEqual(s['counts']['V']['joint_2mm'],6)
        self.assertEqual(s['first_attempt_bounds']['V']['joint'],[5,5])
        self.assertTrue(s['selection_V_equals_S1'])
        self.assertFalse(s['gain_gate'])
        self.assertFalse(s['deep_contact_gate'])

    def test_future_and_heldout_label_access(self):
        self.assertTrue(all(self_test().values()))

    def test_no_support_does_not_filter_out_training_data(self):
        r=select(lambda k:dict(feature=np.zeros(10),supported=False),'S1')
        self.assertEqual(r['retained_k'],4)
        self.assertFalse(r['handoff'])

    def test_S2_scheduled_not_every_action(self):
        r=select(lambda k:dict(feature=np.zeros(10),supported=k!=2),'S2')
        self.assertFalse(r['handoff'])

    def test_unknown_action_parameter_rejected(self):
        with self.assertRaises(AssertionError):
            encode_action({'name':'move','arguments':{'hidden_object_id':1}})

    def test_feature_extractor_rejects_hidden_state(self):
        with self.assertRaises(TypeError):
            public_features(teacher_count=1,prior_decisions=1,past_actions=[],past_target_nll=[],snapshot={})

    def test_incomplete_or_duplicated_units_rejected(self):
        rows=read_rows(ROOT/'data/stage_a.csv')
        with self.assertRaises(AssertionError):aggregate(rows[:-1])
        with self.assertRaises(AssertionError):aggregate(rows[:-1]+[rows[0]])

    def test_joint_threshold_changes_are_detected(self):
        rows=read_rows(ROOT/'data/stage_a.csv')
        rows[0]['joint_2mm']=1-rows[0]['joint_2mm']
        with self.assertRaises(AssertionError):aggregate(rows)

    def test_extra_audit_holds_do_not_change_registered_peak(self):
        records=[dict(phase='control_step',step=i,sim_time=i,contacts=[dict(g1=0,g2=1,distance=-.001 if i<=20 else -.009)]) for i in range(1,41)]
        a=raw_peaks(records,['robot0_finger','box'],20)
        self.assertEqual(a[:2],(.001,.009))

    def test_self_contacts_not_external(self):
        rows=[dict(phase='control_step',step=1,sim_time=0,contacts=[dict(g1=0,g2=1,distance=-.02)])]
        self.assertEqual(raw_peaks(rows,['robot0_arm','gripper0_finger'],1)[0],0)

    def test_missing_raw_control_step_rejected(self):
        with self.assertRaises(AssertionError):
            raw_peaks([dict(phase='control_step',step=2,contacts=[])],['box'],2)

    def test_partial_depth_cannot_be_undone_by_missing_tail(self):
        rows=read_rows(ROOT/'data/stage_a.csv')
        result=bounds(rows,load(ROOT/'data/interruption_audit.json'))
        self.assertEqual(result['V']['joint'],[5,5])
        self.assertEqual(result['V']['deep'],[5,5])

if __name__=='__main__':unittest.main()
