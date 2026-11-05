# MOTIF-027 — The Last Inch: a bounded real-app handoff

The research problem is not generating an email: it is **connecting an explicitly human-defined finish line to a real, usable capability without silently granting delivery authority**.

027 source-owns an auditable local capability switchboard, grounded in the actual MOTIF-026 preparation gate. The caller must supply the original question, the selected example or custom criterion, the exact previously confirmed SHA-256 contract ID, and a staged action. The source independently reruns 026's confirmation and preparation logic.

**DISCOVER_LOCAL_CAPABILITIES** returns only relevant, actually supported local routes:
- `local_workkit`: existing MOTIF-026 four real local files, with prior independent permission.
- `local_workshop`: local Static OS research/workshop page prefill, with no automatic computation or action. Available for suitable non-river domains.
- `local_email_composer`: a **user-operated mailto handoff**, only for community/outreach domains (donation, volunteers, gatherings, food exchange). Recipient is never inferred, harvested or guessed.

The email capability has **two separate stages** after the existing goal and workkit approvals:
1. `PREVIEW_MAIL_APP_HANDOFF`: a person enters exactly one recipient's address, subject and message. The handler validates length, address grammar, header controls, explicit domain permission, and computes a digest binding **goal + recipient + subject + body**. It returns an inspectable preview. No mailto URI yet.
2. `AUTHORIZE_MAIL_APP_OPEN`: requires exact unchanged preview digest, `open_consent:true` and `open_permission:"OPEN_LOCAL_MAIL_COMPOSER_ONLY"`. The source returns a strictly encoded `mailto:` URI. **Only the browser's explicit user click** is allowed to open the person's preferred email application. It does not submit or send. A mail app may still prompt for account details, change the content, refuse to open or fail; none are evidence that delivery happened.

The source returns `actual_message_sent:false`, `external_delivery:false`, `no_delivery_receipt:true`, no network calls, no stored user text, no trained model and unknown electrical Joules. The recipient may not exist or be a donor; its authenticity is not proven by address syntax. It **never uses third-party mail credentials** or attempts SMTP/API sending.

The local workshop route is a *prefill-only* handoff into the existing `/workshop` app. Transferring the question does not trigger Static OS, save an artifact or imply any result. User explicitly chooses to start a separate workshop action.

## Reproduce

```sh
python3 -m unittest discover -s experiments/027 -p 'test_*.py' -v
```

All paths are no-cost stdlib Python. Future actual delivery could be supported only behind a separately installed mail integration, an authenticated sender identity, explicit per-recipient authorization, delivery receipts and revocation; none are implemented here.

The contribution is **a bounded source-owned gate from a human-specified goal to a real-world application's composer**, without falsely claiming the message was sent.

Recipient parser excludes percent characters to prevent ambiguity around encoded `mailto:` delimiters. A possible valid percent-containing mailbox is deliberately unsupported; HOLD is safer than introducing confusion about which third party receives an outreach draft.
