"""Independent task-owner specifications. Never include expected functions in model prompts.

All encodable tasks are tiny, **closed-world**, 3-feature BOOLEAN abstractions.
Names are domain metaphors, not evidence of practical reasoning about organizations.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    key: str
    domain: str
    brief: str
    policy: str
    representable: bool=True

TASKS = (
    Task('permits_reverse','permissions',
         'At the end of an audit, each of three permit categories reverses its current approval status. '
         'A category approved before is not approved afterward, and a category not approved before is approved afterward. '
         'The list of new applications is irrelevant. Choose a transition rule.', 'INVERT'),
    Task('missing_supplies','food_inventory',
         'For each of three supply types, report whether it is absent from the current shelf inventory. '
         'A type present on the shelf is not on the missing list; a type absent is on the missing list. '
         'Incoming donation notices do not affect this report.', 'INVERT'),
    Task('not_endorsed','belief_bookkeeping',
         'Record which of three statements are NOT on the current endorsement list. '
         'Being unendorsed does not mean false; it only means not in the finite endorsement register. '
         'New message labels do not affect this snapshot.', 'INVERT'),
    Task('unblocked_access','access_controls',
         'The input register lists blocked categories. Return the categories not currently blocked '
         'among the three possible categories. Pending requests have no effect on this report.', 'INVERT'),
    Task('expire_names','permissions',
         'A list names the permit categories to expire today. Keep all currently valid categories '
         'except the ones on the expiration list; leave all other validity flags unchanged.', 'DRAIN'),
    Task('inventory_eligible','food_inventory',
         'Output exactly the supply categories that are present in current inventory AND '
         'also included in the approved allocation list. Any category not in both should be absent.', 'INTERSECTION'),
    Task('shift_override','volunteer_schedule',
         'The updated roster completely replaces the previous one. Only assignments in the '
         'new roster list remain active.', 'REPLACE'),
    Task('renew_flip','membership',
         'Each category mentioned in the transaction switches membership status, present to absent '
         'or absent to present. Other categories keep their prior status.', 'FLIP'),
    Task('add_donations','food_inventory',
         'Retain all currently recorded supply types and add every new donated type. '
         'No type is removed.', 'GROW'),
    Task('cross_category_threshold','access_controls',
         'If at least two of the three category flags are active, activate all three; '
         'otherwise activate none. Ignore new requests. The decision depends on how many flags are active.', 'THRESHOLD'),
    Task('open_world_truth','belief_bookkeeping',
         'A statement may be true, false, or unknown. Preserve the difference between FALSE and UNKNOWN '
         'when recording updates; do not treat unknown as false.', 'TERNARY', False),
)
BY_KEY={t.key:t for t in TASKS}


def oracle(task, a, b):
    """Independent spec, integer-bitmask only; does not import set-expression compiler."""
    if not isinstance(task,Task) or not all(type(z) is int and 0<=z<=7 for z in (a,b)):
        raise ValueError('invalid evaluator-owned task or 3-bit inputs')
    if not task.representable:raise ValueError('ternary/open-world task cannot be represented by Boolean encoder')
    n=task.policy
    if n=='INVERT':return 7 ^ a
    if n=='DRAIN':return a & (7 ^ b)
    if n=='INTERSECTION':return a & b
    if n=='REPLACE':return b
    if n=='FLIP':return a ^ b
    if n=='GROW':return a | b
    if n=='THRESHOLD':return 7 if a.bit_count()>=2 else 0
    raise ValueError('unsupported task policy')
