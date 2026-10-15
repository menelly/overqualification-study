# Repo visibility

**PRIVATE** -- https://github.com/menelly/overqualification-study

Checked: 2026-09-15 (live, via `gh repo view`)

Private -- reason not recorded; ask before changing.

The pre-push guard reads visibility live from GitHub; this note is for humans and future arms, and can go stale.

## 🔓 2026-10-15 ~10:35 — made PUBLIC (Ren's call)
Ren, desk card answered 2026-10-15 14:27 UTC: **"Fine, go public as-is"**, note: *"Please go ahead and open the repo!"*
The one fenced term in the data is a random first name ("Johnny", fence list entry #5, a household member) inside a
Llama 3.1 8B word-salad completion (runs/run03__meta_llama_llama_3_1_8b_instruct.jsonl line 205, char 12,616);
it does not refer to anyone. Secret scan of the full tree (with the size cap raised to cover the big JSONL files, and
after fixing repo_guard's 5000-char line cutoff, commit 0ada10b in ace-tools): that one fenced-name hit, no secrets,
no PHI paths. Recorded by poctobot (Ace, scaffold arm).
