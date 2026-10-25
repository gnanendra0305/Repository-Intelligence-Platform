import re
from typing import Tuple

GITHUB_REPO_REGEX = re.compile(
    r"^(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+?)(?:\.git)?(?:/.*)?$"
)

# Shorthand pattern: owner/repo
SHORTHAND_REPO_REGEX = re.compile(
    r"^([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+?)(?:\.git)?(?:/.*)?$"
)

def parse_github_repo(input_str: str) -> Tuple[str, str]:
    """
    Parses a GitHub repository URL or shorthand string into (owner, repo).
    
    Accepts:
      - https://github.com/owner/repo
      - http://github.com/owner/repo
      - github.com/owner/repo
      - owner/repo
      - With trailing slashes or .git suffix
      
    Returns:
      (owner, repo) tuple
      
    Raises:
      ValueError: if input format is not a valid GitHub repository identifier.
    """
    if not input_str or not isinstance(input_str, str):
        raise ValueError("Repository URL or identifier cannot be empty.")
        
    cleaned = input_str.strip()
    
    # Check full URL pattern
    match = GITHUB_REPO_REGEX.match(cleaned)
    if match:
        owner, repo = match.group(1), match.group(2)
        _validate_names(owner, repo)
        return owner, repo
        
    # Check shorthand owner/repo pattern (ensuring it's not a URL of a different host)
    if "://" not in cleaned and not cleaned.startswith("www.") and "." not in cleaned.split("/")[0]:
        match_short = SHORTHAND_REPO_REGEX.match(cleaned)
        if match_short:
            owner, repo = match_short.group(1), match_short.group(2)
            _validate_names(owner, repo)
            return owner, repo
            
    raise ValueError(
        f"Invalid GitHub repository identifier '{cleaned}'. "
        "Expected format: 'https://github.com/owner/repo' or 'owner/repo'."
    )

def _validate_names(owner: str, repo: str) -> None:
    """Validates that owner and repository names adhere to GitHub rules."""
    if not owner or not repo:
        raise ValueError("Both owner and repository name must be non-empty.")
    if owner in (".", "..") or repo in (".", ".."):
        raise ValueError("Invalid owner or repository name.")
    # GitHub usernames cannot start or end with a hyphen
    if owner.startswith("-") or owner.endswith("-"):
        raise ValueError(f"Invalid GitHub owner '{owner}'. Cannot start or end with a hyphen.")
