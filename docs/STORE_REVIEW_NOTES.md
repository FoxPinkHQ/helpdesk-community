# Store Review Notes

> One append-only log of every Odoo Apps Store submission and its outcome, per
> module. Reused for all FoxPink modules. Fill a new block for **each** submit /
> re-submit. Never delete history — a reject that was fixed is knowledge.
>
> Rejection reasons that turn out to be general policy get promoted into
> `docs/compatibility/store-rules/` as a `STORE-xxx` rule.

---

## Template (copy for each submission)

```
### Submission #N — <module> <version>

- Submission date:        YYYY-MM-DD
- Submitted by:           <publisher account>
- Repo / branches:        <url> #<series list>
- Artifacts (sha256):     <market-release.json ref>
- Channel:                repo-scan | zip-upload
- Reviewer / contact:     <name or "automated">
- Reviewer notes:         <verbatim message>
- Rejected?:              yes | no
- Reason(s):              <bullet list, verbatim where possible>
- Maps to store-rule:     <STORE-xxx | new>
- Required changes:       <what Odoo asked for>
- Action taken:           <commits / branches / version bump>
- Resubmitted:            YYYY-MM-DD | n/a
- Approved:               yes | no | pending
- Approval date:          YYYY-MM-DD | n/a
- Live listing URL:       <apps.odoo.com/...>
```

---

## helpdesk_community

### Submission #1 — helpdesk_community 19.0.1.0.2

- Submission date:        _pending_
- Submitted by:           FoxPink (aduy000@gmail.com)
- Repo / branches:        https://github.com/FoxPinkHQ/helpdesk-community #14.0 #15.0 #16.0 #17.0 #18.0 #19.0
- Artifacts (sha256):     dist/market-release.json (release 1.0.2, validated:true)
- Channel:                repo-scan
- Reviewer / contact:     _pending_
- Reviewer notes:         _pending_
- Rejected?:              _pending_
- Reason(s):              _pending_
- Maps to store-rule:     _n/a yet_
- Required changes:       _pending_
- Action taken:           _pending_
- Resubmitted:            _n/a_
- Approved:               _pending_
- Approval date:          _n/a_
- Live listing URL:       _n/a_

> Pre-submission blockers to clear first (see STORE_SUBMISSION_GUIDE §1–2 and
> store-rules): (1) series branches 14–18 are stale/wrong-versioned; (2) module
> currently sits at repo root instead of a `helpdesk_community/` subfolder;
> (3) embedded PAT in git remote must be rotated/removed.
