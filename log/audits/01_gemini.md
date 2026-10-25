# Audit: Gemini (version not recorded)

Verbatim from the planning chat (https://claude.ai/share/75dfaaef-866c-4979-8016-b7747f9ddaa3), messages 21–24: the human pasting Gemini's output, Claude's check of it against the sources, the human's go-ahead, and the changes made. Gemini's full response is pasted as text in message 21 (`file_count: 0`), so the share holds it whole; no separate raw file is needed.

- **Auditor output pasted:** 2026-10-22T03:53:53.740755Z (2026-10-21 23:53 EDT, the brief's "October 21, 2026")
- **Resolved by Claude:** 2026-10-22T03:54:13.223558Z
- **Version:** not recorded in the chat or the brief (the fact card reads "Gemini [version]"). Open item.
- **Lyrics audited:** the draft before this audit. Gemini quotes "two hundred million spent to learn"; the audit changed it to "pledged".
- **Sources given to Gemini:** none. Per the human, Gemini summarized the fund first and then audited, with no citations. The brief's checklist calls for a rerun with the announcement page pasted in.

## Message 21: human, 2026-10-22T03:53:53.740755Z

I had Gemini audit the lyrics after asking it to summarize the fund (much like how I started this session), and it had this to say (it did not provide any citations unfortunately):

---

Here is an audit of your draft's accuracy and fairness regarding Anthropic's Public Benefit Fund:

The Misses (Factual Corrections)

* The Math is Confused: The chorus confidently claims "five in every hundred" (5%), but Anthropic's actual commitment is approximately 20%. The song contradicts itself later in the bridge when the Founder accurately mentions "a fifth of us." You'll want to adjust the chorus lyrics to reflect the 20% reality.

* The LLC Claim: The Lawyer's verse claims the fund is an "LLC, wholly owned." While tech companies do frequently use LLCs for philanthropy to avoid the strict rules of traditional charities (e.g., the Chan Zuckerberg Initiative), Anthropic has not explicitly designated this fund as a wholly owned LLC in its public announcements.

The Hits (Factual Accuracies)

* The Valuation Escalator: The line "And if we grow by half again, two more... then" perfectly captures the actual mechanism where 2% of shares are added for every 50% increase in the company's valuation.

* The $200M Study: The Worker's reference to "two hundred million spent to learn what happens to my place" is a highly accurate nod to Anthropic's prior $200 million commitment to study AI's impact on the global labor market.

The Satirical Fairness As a piece of satire, the draft is remarkably fair and hits the right pressure points. Poking fun at opaque corporate philanthropy—specifically the "baseline to be announced" for the valuation escalators and the Worker's plea for a voice in how the funds are actually distributed—perfectly mirrors legitimate public skepticism regarding tech companies acting as self-appointed wealth redistributors.

You have a solid foundation; just fix the 5% metric in the chorus so the satire is anchored in the correct data.

## Message 22: Claude, 2026-10-22T03:54:13.223558Z

Gemini's fairness read is useful, but both of its corrections are wrong, and the announcement itself settles them. I'd keep the chorus as is.

**The two "misses"**

- **5% is right for the fund.** Anthropic is committing 5% of its shares to the fund. The roughly 20% is a company-wide total: Anthropic said that, combined with the new fund, about 20% of its shares are now dedicated to the public good. So the chorus (the fund) and the bridge ("a fifth of us, all told") describe different things, and both are accurate. Gemini's confusion does show the bridge could mislead viewers, so the fact card should spell it out: "5% to the fund; about 20% in total, counting Anthropic's other commitments."
- **The LLC is in the announcement, almost word for word.** Anthropic says it is establishing the fund as a wholly-owned LLC rather than a 501(c)(3), to allow different forms of giving.

**One small fix Gemini missed**

- **"Two hundred million spent to learn" should be "pledged to learn."** It's a commitment, not money already spent, and "pledged" scans the same.

**For the audit log**

Record this audit as it is, alongside the primary source that contradicts its corrections, since a cross-lab check is only worth something if it's checked too. I'd also rerun it with the announcement page pasted in, so it judges the lyrics against the source instead of its own summary. Its fairness verdict is the part to keep. I'm the conflicted party in that comparison, so the rerun should settle it rather than my word.

Want me to make the "pledged" change and the fact-card clarification in the doc?

Sources:
- [Investing in the public benefit – Anthropic](https://www.anthropic.com/news/public-benefit-fund)
- [ESG Today](https://www.esgtoday.com/anthropic-commits-5-of-shares-to-a-new-public-benefit-fund/)

## Message 23: human, 2026-10-22T03:56:05.344182Z

yes, and record the audit in the doc (it is what will eventually get sent to Claude Code to implement)

## Message 24: Claude, 2026-10-22T03:56:25.580783Z

> *[Claude Docs: Update]*

Done. The Worker's line now says "pledged." The fact card separates the fund's 5% from Anthropic's roughly 20% total. The audit log under the production notes has a table of each finding and how it was resolved. The checklist now includes rerunning the audit with the announcement pasted in, and filling in Gemini's version, which goes in the fact card's credit line too.
