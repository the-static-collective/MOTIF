from abstraction_cli import main
if __name__=='__main__':raise SystemExit(main(['--backend','offline','--tasks',
    'food_safe,food_recalled_elsewhere,volunteer_eligible,food_donations,shifts_override,not_on_shelf,cancel_or_add,reverse_outreach,vague_access,unknown_beliefs',
    '--output','offline-results.json']))
