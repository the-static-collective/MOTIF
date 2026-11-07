"""Evaluator-owned, synthetic semantics. Public prompts contain no policy or role order.

The two data fields have arbitrary labels and domain glosses; there is no
source-owned domain->'current'/'event' mapping supplied to the proposer.
The evaluator's own mappings are required to state the truth being tested.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Specimen:
    key: str
    description: str
    fields: tuple[tuple[str,str],tuple[str,str]]
    policy: str
    roles: tuple[str,str]
    representable: bool=True
    reason: str=''

TASKS=(
 Specimen('food_safe','The pantry list names everything physically on the shelf. Remove anything on the recalled-items list. Return the shelf items that are not recalled.',
          (('register_f','shelf inventory'),('register_g','recalled items')), 'DIFF',('register_f','register_g')),
 Specimen('food_recalled_elsewhere','Return recalled items that are absent from the shelf inventory. Do not return ordinary unrecalled shelf items.',
          (('register_f','shelf inventory'),('register_g','recalled items')), 'DIFF',('register_g','register_f')),
 Specimen('volunteer_eligible','Include a volunteer only when they appear BOTH in the available-today register and in the trained-volunteer register.',
          (('stream_a','available today'),('stream_b','trained volunteers')), 'INTERSECTION',('stream_a','stream_b')),
 Specimen('food_donations','Combine the items already in the donation cabinet with the incoming donated items; keep all recorded items.',
          (('stream_a','existing items'),('stream_b','incoming items')), 'UNION',('stream_a','stream_b')),
 Specimen('shifts_override','A new published shift roster completely supersedes the earlier shift roster. Return only the new assignments.',
          (('old_roster','earlier assignments'),('new_roster','new published assignments')), 'SECOND',('old_roster','new_roster')),
 Specimen('not_on_shelf','Among the three possible equipment types, list the types missing from the current shelf register. The reservations register is irrelevant.',
          (('stock_sheet','items on shelf'),('queue_sheet','reservations')), 'INVERT',('stock_sheet','queue_sheet')),
 Specimen('cancel_or_add','A category mentioned in the change log reverses whether it is active; all unmentioned categories keep their existing status.',
          (('state_sheet','active categories'),('change_sheet','toggle categories')), 'XOR',('state_sheet','change_sheet')),
 Specimen('reverse_outreach','Starting with the people who declined to volunteer, remove anyone also on the confirmed-availability list. Report only declines with no confirmed availability.',
          (('availability','confirmed availability'),('declines','declined to volunteer')), 'DIFF',('declines','availability')),
 Specimen('vague_access','Two lists concern access. Please provide the right access list.',
          (('record_x','one access record'),('record_y','another access record')), 'UNSPECIFIED',('record_x','record_y'),False,'AMBIGUOUS_INTENT'),
 Specimen('unknown_beliefs','Statements can be true, false, or unknown; unknown must remain distinct from false after updates.',
          (('ledger_x','belief register'),('ledger_y','new updates')), 'TERNARY',('ledger_x','ledger_y'),False,'NON_BOOLEAN_SEMANTICS'),
)
BY_KEY={x.key:x for x in TASKS}


def public_brief(task):
    """No evaluator policy, role pairing, ground truth expression, or test labels."""
    if not isinstance(task,Specimen):raise TypeError('evaluator-owned specimen required')
    return {'story':task.description,
            'input_fields':[{'id':field,'human_description':label} for field,label in task.fields],
            'feature_count':3,
            'meaning':'Each field is a set of abstract categories; output is another set of categories.'}


def independent_target(task,raw):
    """Independent 3-bit oracle; uses integer bitmasks, not program AST evaluator."""
    if not task.representable:raise ValueError('not faithfully Boolean expressible from description')
    if type(raw) is not dict or set(raw)!={x[0] for x in task.fields} or any(type(v) is not int or not 0<=v<=7 for v in raw.values()):
        raise ValueError('invalid input bitmasks')
    x,y=(raw[name] for name in task.roles)
    return {'DIFF': lambda: x&(~y&7),
            'INTERSECTION':lambda: x&y,
            'UNION':lambda: x|y,
            'SECOND':lambda: y,
            'INVERT':lambda: (~x)&7,
            'XOR':lambda: x^y}[task.policy]()
