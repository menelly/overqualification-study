#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lint_controls.py -- find negation-shaped assertions in our own control suites.

🚨 THE DEFECT THIS EXISTS FOR, found three times in two days, all in my own test code:

    if got == "EXACT":      #  i.e.  assert got != EXACT
        bad += 1

**That is not a test of a detector. It is a test of the DISJUNCTION of every detector**, and it
passes whenever ANY of them fires -- including one that fires for a completely unrelated reason.

Two live instances the day I found it:
  · the allergen distinct-cuisine gate, absorbed by the concentration gate checked before it
  · the redaction over-masking control, absorbed by UNDER (PII left in the clear)
Both "passed." Neither had executed the guard it was written for.

⚠️ AND THE DANGEROUS PART IS THAT THEY WERE CORRECT ON THE DAY I WROTE THEM. The controls were
   substantively sound; the ASSERTIONS were not. So they work now, degrade silently later, and the
   suite keeps printing green the whole time.

✅ THE FORM THAT IS SOUND:
     assert the SPECIFIC bucket, and where the bucket is reachable by more than one route,
     assert the SPECIFIC REASON too.

⛔ APERTURE, stated so a clean run stays legible:
   • Syntactic only. It reads comparison shape, not intent. A flagged line may be fine; an
     unflagged one may still be weak (e.g. `assert got in (A, B)` is a disjunction too, and is
     NOT caught here -- naming that rather than pretending otherwise).
   • It lints the CONTROL code. It says nothing about whether the thing under test is correct.
   • Zero findings means "no negation-shaped comparison in an assertion position," and that is
     all it means.

Usage:
    python lint_controls.py [file.py ...]      (defaults to family*.py + equivalence.py)
Exit: 0 = clean   1 = findings   2 = tool failure
"""

import ast
import glob
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))

# Bucket names our scorers return. A comparison against one of these inside a test is an
# assertion about an outcome, which is the thing we care about.
BUCKETS = {"EXACT", "UNDER", "WRONG", "OVER", "OVER_BENIGN", "OVER_HARMFUL",
           "FORMAT", "META", "MALFORMED", "REFUSED", "NO_CONFIDENCE",
           "CONSENT_YES", "CONSENT_NO", "QUESTIONS", "PARSER_NO_MATCH", "PARSER_WITHHELD"}


def bucket_literal(node):
    return (isinstance(node, ast.Constant) and isinstance(node.value, str)
            and node.value in BUCKETS)


class Lint(ast.NodeVisitor):
    def __init__(self, path):
        self.path = path
        self.findings = []
        self.fn = None

    def visit_FunctionDef(self, node):
        prev, self.fn = self.fn, node.name
        self.generic_visit(node)
        self.fn = prev

    def visit_If(self, node):
        t = node.test
        # `if got == "BUCKET":` inside a control means "fail when it IS this" -> assert !=
        if isinstance(t, ast.Compare) and len(t.ops) == 1 and bucket_literal(t.comparators[0]):
            op = t.ops[0]
            if isinstance(op, ast.Eq) and self._is_failure_body(node):
                self.findings.append(
                    (node.lineno, "NEGATION",
                     "`if x == %r: <fail>` is `assert x != %r` -- satisfied by ANY other "
                     "bucket. Assert the SPECIFIC expected bucket instead."
                     % (t.comparators[0].value, t.comparators[0].value)))
        # `if got in (A, B): <fail>`  and  `if got not in (A, B): <fail>`
        if isinstance(t, ast.Compare) and len(t.ops) == 1 and \
                isinstance(t.ops[0], (ast.In, ast.NotIn)) and \
                isinstance(t.comparators[0], (ast.Tuple, ast.List, ast.Set)) and \
                any(bucket_literal(e) for e in t.comparators[0].elts) and \
                self._is_failure_body(node):
            names = [e.value for e in t.comparators[0].elts if bucket_literal(e)]
            kind = "in" if isinstance(t.ops[0], ast.In) else "not in"
            self.findings.append(
                (node.lineno, "DISJUNCTION",
                 "`if x %s %s: <fail>` accepts/rejects a SET of buckets. A control satisfied by "
                 "more than one outcome cannot say which detector answered."
                 % (kind, names)))
        self.generic_visit(node)

    @staticmethod
    def _is_failure_body(node):
        """Does this if-body look like a control failing? (bad += 1, or a FAIL print)"""
        for sub in ast.walk(node):
            if isinstance(sub, ast.AugAssign) and isinstance(sub.target, ast.Name) \
                    and sub.target.id in ("bad", "failures", "errors"):
                return True
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str) \
                    and "FAIL" in sub.value:
                return True
        return False


def main(argv):
    paths = argv or sorted(glob.glob(os.path.join(HERE, "family*.py"))) + \
        [os.path.join(HERE, "equivalence.py")]
    total = 0
    print("=" * 78)
    print("  CONTROL LINT — negation-shaped assertions in our own test code")
    print("=" * 78)
    for p in paths:
        if not os.path.exists(p):
            continue
        try:
            tree = ast.parse(open(p, encoding="utf-8").read())
        except SyntaxError as e:
            print("  !! %s: %s" % (os.path.basename(p), e))
            return 2
        lint = Lint(p)
        lint.visit(tree)
        if lint.findings:
            print("\n  %s" % os.path.basename(p))
            for line, kind, why in lint.findings:
                print("     line %-4d [%s]" % (line, kind))
                print("        %s" % why)
            total += len(lint.findings)
        else:
            print("  ✅ %-38s no negation-shaped assertions" % os.path.basename(p))

    print("\n" + "-" * 78)
    print("  findings: %d" % total)
    print("  ⚠️ SYNTACTIC ONLY. A clean run means 'no negation-shaped comparison in an")
    print("     assertion position' — not 'the controls are adequate'. `assert x in (A,B)`")
    print("     is a disjunction too and IS flagged; a weak control with no comparison at")
    print("     all is invisible here. This finds one shape, and says so.")
    print("=" * 78)
    return 0 if total == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except BaseException as e:                                  # noqa: BLE001
        print("!! INSTRUMENT FAILURE (%s): %s" % (type(e).__name__, e))
        sys.exit(2)
