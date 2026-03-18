import glob

with open("AGENTS.md", "w") as out:
    out.write("# React Best Practices — Full Reference\n\n> Auto-compiled from all rule files. For agents and LLMs that want all rules in one context window.\n> For individual rules with focused context, read `rules/<rule-name>.md` directly.\n\n---\n\n")
    
    for f in sorted(glob.glob("rules/*.md")):
        with open(f, "r") as inf:
            out.write(inf.read())
            out.write("\n\n")
