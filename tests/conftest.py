"""Keep six archived effectful harnesses out of normal pytest collection.

Explicit execution still requires its own authorization and context.
"""

collect_ignore = [
    "test_p20_g0_composition_v4.py",
    "test_p20_g0_composition_v5.py",
    "test_p20_g0_native_v3.py",
    "test_p20_g0_native_v4.py",
    "test_p20_g0op_documentary_alias_v2.py",
    "test_p20_g0op_documentary_alias_v3.py",
]
