"""Claim 25: the team's certifier, imported by path, run on two inputs of my own."""
import os, sys, importlib.util, copy
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Rec
R = Rec()
if len(sys.argv) < 2:
    print('usage: cert.py <path to transformational_steelman_certifier.py>  (Foundation-0/cave-expedition PR 1 head 80606f1, symbiosis/round10/arm5-transformational-steelman/)')
    sys.exit(2)
PATH = sys.argv[1]
sp = importlib.util.spec_from_file_location('tsc_under_check', PATH)
mod = importlib.util.module_from_spec(sp)
sp.loader.exec_module(mod)
fn = mod.certify_transformational_steelman

rescue = {
    "claim_id": "SECOND-CHECK-RESCUE-1",
    "proposed_verdict": "TRANSFORMED_EXACT",
    "literal_failed": True,
    "literal_failure_witness": "The literal identity fails at a point nobody computed; this sentence is invented",
    "families_searched": ["T1_GAUGE_SIMILARITY"],
    "applied_family": "T1_GAUGE_SIMILARITY",
    "transform_dof": 1,
    "held_out_constraints": 2,
    "fixed_globally_before_holdout": True,
    "target_pass_count": 2,
    "target_total_count": 2,
    "null_false_pass_count": 0,
    "null_total_count": 10,
    "max_null_false_pass_rate": Fraction(1, 10),
    "transform_rank": 1,
    "preserved_invariant_core": "Some invariant core that is named but not checked",
    "modified_hypotheses": "Some hypothesis change that is named but not checked",
    "residual_gap": Fraction(0, 1),
    "max_residual_gap": Fraction(0, 1),
    "relabelled_as_literal": False,
    "obstruction_invariant": None,
    "obstruction_survives_all_searched": False,
}
r1 = fn(copy.deepcopy(rescue))
print('INPUT 1 (internally consistent TRANSFORMED_EXACT, witness is an invented string):', r1['status'], r1['admitted'], r1['reasons'])
R.check('C25a consistent numbers + invented witness string is ADMITTED', r1['admitted'] is True)
# same numbers, witness changed to a different invented string: same outcome (the witness is never evaluated)
w2 = copy.deepcopy(rescue); w2['literal_failure_witness'] = 'Two plus two equals five fails'
r1b = fn(w2)
R.check('C25a the witness text does not matter (a different invented string is also ADMITTED)', r1b['admitted'] is True)
# inconsistent numbers are refused (the certifier does check numbers)
bad = copy.deepcopy(rescue); bad['target_pass_count'] = 1
r1c = fn(bad)
R.check('CTRL inconsistent numbers (target 1 of 2 on an exact rescue) are REFUSED', (not r1c['admitted']) and 'G1_TRANSFORMED_TARGET_FAILED' in r1c['reasons'], r1c['reasons'])
bad = copy.deepcopy(rescue); bad['transform_dof'] = 2
r1d = fn(bad)
R.check('CTRL dof not below constraints is REFUSED', (not r1d['admitted']) and 'G2_OVERPARAMETERIZED_EPICYCLE_DOF' in r1d['reasons'])

falsified = {
    "claim_id": "SECOND-CHECK-FALSIFIED-1",
    "proposed_verdict": "INVARIANT_FALSIFIED",
    "literal_failed": True,
    "literal_failure_witness": "Identical observables give opposite answers (invented for this check)",
    "families_searched": list(mod.MORPHISM_FAMILIES),
    "applied_family": None,
    "transform_dof": 0,
    "held_out_constraints": 4,
    "fixed_globally_before_holdout": True,
    "target_pass_count": 0,
    "target_total_count": 4,
    "null_false_pass_count": 0,
    "null_total_count": 10,
    "max_null_false_pass_rate": Fraction(1, 10),
    "transform_rank": 0,
    "preserved_invariant_core": None,
    "modified_hypotheses": None,
    "residual_gap": Fraction(1, 1),
    "max_residual_gap": Fraction(1, 1),
    "relabelled_as_literal": False,
    "obstruction_invariant": "A named invariant that is claimed to survive every family",
    "obstruction_survives_all_searched": True,
}
rf = fn(copy.deepcopy(falsified))
print('CONTROL falsified spec with gap 1:', rf['status'], rf['admitted'], rf['reasons'])
R.check('CTRL invariant-falsified spec with nonzero gap and invented witness/obstruction strings is ADMITTED', rf['admitted'] is True)
fz = copy.deepcopy(falsified); fz['residual_gap'] = Fraction(0, 1); fz['max_residual_gap'] = Fraction(0, 1)
r2 = fn(fz)
print('INPUT 2 (invariant-falsified, residual gap zero):', r2['status'], r2['admitted'], r2['reasons'])
R.check('C25b invariant-falsified spec with residual gap 0 is REFUSED with G4_FALSIFIED_HAS_ZERO_GAP', (not r2['admitted']) and 'G4_FALSIFIED_HAS_ZERO_GAP' in r2['reasons'])
# schema controls
for name, mut in [('extra key', lambda s: s.update({'extra': 1})), ('float', lambda s: s.update({'transform_dof': 1.0})), ('null cap above 1/10', lambda s: s.update({'max_null_false_pass_rate': Fraction(1, 5)}))]:
    s = copy.deepcopy(rescue); mut(s)
    try:
        fn(s)
        refused = False
    except ValueError:
        refused = True
    R.check('CTRL schema violation (%s) raises ValueError' % name, refused)
print('FAILS:', R.bad)
sys.exit(1 if R.bad else 0)
