import sys
import re
import subprocess
import json


def get_latest_tag_local():
    try:
        result = subprocess.run(
            ["git", "tag"],
            capture_output=True, text=True
        )
        tags = result.stdout.strip().splitlines()
        tags = [t.strip() for t in tags if re.match(r'^v\d+\.\d+\.\d+$', t.strip())]
        if not tags:
            return "1.0.0"
        tags.sort(key=lambda v: list(map(int, v.lstrip('v').split('.'))), reverse=True)
        return tags[0].lstrip('v')
    except Exception:
        return "1.0.0"


def get_latest_tag_remote(url):
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", url],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().splitlines()
        versions = []
        for line in lines:
            if 'refs/tags/v' in line and '{}' not in line:
                m = re.search(r'refs/tags/v(\d+\.\d+\.\d+)$', line)
                if m:
                    versions.append(m.group(1))
        if not versions:
            return "1.0.0"
        versions.sort(key=lambda v: list(map(int, v.split('.'))), reverse=True)
        return versions[0]
    except Exception:
        return "1.0.0"


def bump_version(version):
    major, minor, patch = map(int, version.split('.'))
    if patch < 9:
        patch += 1
    elif minor < 9:
        minor += 1
        patch = 0
    else:
        major += 1
        minor = 0
        patch = 0
    return f"{major}.{minor}.{patch}"


def main():
    repo_name    = sys.argv[1]
    repo_version = sys.argv[2]
    git_user     = sys.argv[3]
    git_token    = sys.argv[4]

    test_url  = f"https://{git_user}:{git_token}@github.com/Rohitsss-lab/test.git"
    test1_url = f"https://{git_user}:{git_token}@github.com/Rohitsss-lab/test1.git"

    # Get current umbrella version and bump it
    current_umbrella = get_latest_tag_local()
    new_umbrella     = bump_version(current_umbrella)

    # Get latest versions of test and test1
    if repo_name == 'test':
        test_version  = repo_version
        test1_version = get_latest_tag_remote(test1_url)
    elif repo_name == 'test1':
        test_version  = get_latest_tag_remote(test_url)
        test1_version = repo_version
    else:
        test_version  = get_latest_tag_remote(test_url)
        test1_version = get_latest_tag_remote(test1_url)

    # Write versions.json
    versions = {
        "umbrella": new_umbrella,
        "test":     test_version,
        "test1":    test1_version
    }
    with open('versions.json', 'w') as f:
        json.dump(versions, f, indent=2)
        f.write('\n')

    # Print results for Jenkins to read
    print(f"NEW_VERSION={new_umbrella}")
    print(f"REPO1_VERSION={test_version}")
    print(f"REPO2_VERSION={test1_version}")


if __name__ == "__main__":
    main()
