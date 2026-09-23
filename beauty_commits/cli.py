#!/usr/bin/env python3
import subprocess
import sys

# Standard types from the Conventional Commits specification
TYPES = {
    "feat": "A new feature for the user",
    "fix": "A bug fix",
    "docs": "Documentation only changes",
    "style": "Formatting, missing semi-colons, etc. (no code change)",
    "refactor": "Refactoring code without changing functionality or fixing bugs",
    "perf": "A code change that improves performance",
    "test": "Adding missing tests or correcting existing tests",
    "build": "Changes that affect the build system or external dependencies",
    "ci": "Changes to CI configuration files and scripts",
    "chore": "Other changes that don't modify src or test files",
    "revert": "Reverts a previous commit"
}

def check_git_repo():
    """Checks if the current directory is inside a Git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError:
        print("❌ Error: Current directory is not a Git repository.")
        sys.exit(1)

def ask_choice(prompt, choices):
    """Prompts the user to select an option from a numbered list."""
    print(f"\n{prompt}")
    keys = list(choices.keys())
    for idx, key in enumerate(keys, 1):
        print(f"  {idx}) {key.ljust(10)} - {choices[key]}")
    
    while True:
        choice = input("\nSelect a type (enter number or name): ").strip()
        if choice in choices:
            return choice
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        print("Invalid option. Please try again.")

def ask_input(prompt, required=False):
    """Prompts the user for text input."""
    while True:
        value = input(f"{prompt}: ").strip()
        if value or not required:
            return value
        print("This field is required.")

def ask_boolean(prompt):
    """Prompts the user for a Yes/No response."""
    while True:
        reply = input(f"{prompt} (y/N): ").strip().lower()
        if reply in ["y", "yes"]:
            return True
        if reply in ["n", "no", ""]:
            return False
        print("Please answer with 'y' (yes) or 'n' (no).")

def main():
    check_git_repo()
    print("=== Conventional Commit Interactive Runner ===")

    # 1. Select Type
    commit_type = ask_choice("Select the TYPE of commit:", TYPES)

    # 2. Scope (Optional)
    scope = ask_input("\nEnter the SCOPE (optional, e.g., auth, parser, api)")
    
    # 3. Breaking Change Flag (!)
    is_breaking = ask_boolean("\nDoes this commit introduce a BREAKING CHANGE?")

    # 4. Short Description (Subject)
    description = ask_input("\nEnter a short DESCRIPTION (imperative mood, e.g., add login flow)", required=True)

    # 5. Body (Optional)
    print("\nEnter the BODY of the commit (detailed explanation, press Enter to skip):")
    body = input("> ").strip()

    # 6. Breaking Change Description / Footers (Optional)
    breaking_description = ""
    if is_breaking:
        breaking_description = ask_input("\nDescribe the BREAKING CHANGE (for the footer)")

    footer_issue = ask_input("\nRelated Issues (optional, e.g., Fixes #123)")

    # --- Constructing the Commit Message ---
    
    # Header: type(scope)!: description
    header = commit_type
    if scope:
        header += f"({scope})"
    if is_breaking:
        header += "!"
    header += f": {description}"

    commit_message_parts = [header]

    # Body
    if body:
        commit_message_parts.append(body)

    # Footers
    footers = []
    if is_breaking and breaking_description:
        footers.append(f"BREAKING CHANGE: {breaking_description}")
    if footer_issue:
        footers.append(footer_issue)

    if footers:
        commit_message_parts.append("\n".join(footers))

    full_commit_message = "\n\n".join(commit_message_parts)

    # Preview
    print("\n" + "="*40)
    print("COMMIT MESSAGE PREVIEW:")
    print("="*40)
    print(full_commit_message)
    print("="*40)

    # Confirmation & Execution
    if ask_boolean("\nDo you want to execute this commit?"):
        try:
            subprocess.run(["git", "commit", "-m", full_commit_message], check=True)
            print("\n✅ Commit created successfully!")
        except subprocess.CalledProcessError:
            print("\n❌ Failed to create the commit.")
    else:
        print("\nOperation cancelled. No commit was made.")

if __name__ == "__main__":
    main()