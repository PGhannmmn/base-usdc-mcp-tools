"""Read ONLY public, product-specific feedback. No cookies, tracking or writes."""
import json
import os
import sys
import urllib.error
import urllib.request


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "base-usdc-qa-public-interest-v1",
        },
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.load(response)


def summarise(repo_name, repository, issue, comments):
    """Report potential feedback, never visits, downloads, or paying demand."""
    if repository.get("private") is not False:
        raise ValueError("Metrics require a public repository")
    if int(issue.get("number", -1)) != 1:
        raise ValueError("Unexpected issue number")
    owner = repository["owner"]["login"].casefold()
    independent = []
    for comment in comments:
        user = comment.get("user") or {}
        login = (user.get("login") or "").casefold()
        if not login or login == owner or user.get("type") == "Bot":
            continue
        independent.append(comment)
    authors = {
        c["user"]["login"].casefold()
        for c in independent
    }
    return {
        "product": "Base USDC Payment QA Fixture Kit v0.1",
        "repo": repo_name,
        "feedback_issue": f"https://github.com/{repo_name}/issues/1",
        "issue_state": issue.get("state"),
        "potential_external_comments": len(independent),
        "potential_external_commenters": len(authors),
        "last_external_comment_at": max(
            (c.get("created_at", "") for c in independent), default=None
        ),
        "actual_downloads": None,
        "actual_users": None,
        "paying_customers": None,
        "verified_demand": None,
        "note": (
            "External comments may be spam or irrelevant. Qualify manually. "
            "Repo-wide stars, forks and branch ZIP links cannot measure product demand."
        ),
    }


def main():
    repo = os.getenv(
        "GITHUB_REPOSITORY",
        sys.argv[1] if len(sys.argv) > 1 else "PGhannmmn/base-usdc-mcp-tools",
    )
    if repo.count("/") != 1 or not all(repo.split("/")):
        raise SystemExit("Expected owner/repo")
    base = f"https://api.github.com/repos/{repo}"
    try:
        repository = get_json(base)
        issue = get_json(base + "/issues/1")
        count = int(issue.get("comments", 0))
        # Bounded read: never give an apparently complete count from truncated data.
        if count > 1000:
            raise ValueError("Too many comments for bounded public fetch")
        comments = []
        for page in range(1, (count + 99) // 100 + 1):
            page_comments = get_json(
                base + f"/issues/1/comments?per_page=100&page={page}"
            )
            if not isinstance(page_comments, list):
                raise ValueError("Invalid comments response")
            comments.extend(page_comments)
        if len(comments) != count:
            raise ValueError("Issue comments changed during snapshot; retry later")
        print(json.dumps(summarise(repo, repository, issue, comments), indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, urllib.error.URLError) as exc:
        print("metrics_unavailable: " + str(exc), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
