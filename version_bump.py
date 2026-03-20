import json, sys

with open("versions.json", "r") as f:
    data = json.load(f)

# Update sub-repo version passed as argument
repo_name = sys.argv[1]   # e.g. "repo1"
repo_ver  = sys.argv[2]   # e.g. "1.2.0"
data[repo_name] = repo_ver

# Bump umbrella's own MINOR version
major, minor, patch = data["umbrella"].split(".")
data["umbrella"] = f"{major}.{int(minor)+1}.0"

with open("versions.json", "w") as f:
    json.dump(data, f, indent=2)

with open("VERSION", "w") as f:
    f.write(data["umbrella"])

print(f"Umbrella version bumped to {data['umbrella']}")
```

---

### Step 2 — Add a `VERSION` file to Repo 1 and Repo 2

In **each** of your Python repos, create a plain `VERSION` file at the root:
```
1.0.0
