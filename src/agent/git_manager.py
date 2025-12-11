import subprocess
import os
import datetime

class GitManager:
    """
    Handles Git operations for the Documentation Consistency Agent.
    """
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def run_git_command(self, args: list):
        """
        Runs a git command and returns output/error.
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {' '.join(args)}")
            print(f"Error: {e.stderr}")
            return None

    def create_branch(self, base_name="doc-update"):
        """
        Creates a new branch with a timestamp.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"{base_name}-{timestamp}"
        
        print(f"Creating new branch: {branch_name}")
        self.run_git_command(["checkout", "-b", branch_name])
        return branch_name

    def commit_changes(self, message="Auto-update documentation"):
        """
        Stages and commits changes.
        """
        print("Staging changes...")
        self.run_git_command(["add", "."])
        
        print(f"Committing with message: {message}")
        self.run_git_command(["commit", "-m", message])

    def push_branch(self, branch_name):
        """
        Pushes the branch to origin.
        """
        print(f"Pushing branch {branch_name} to origin...")
        # Note: This requires credentials to be configured in the environment
        result = self.run_git_command(["push", "origin", branch_name])
        if result is not None:
             print("Push successful.")
             # In a real scenario, we might return the PR URL here if output provides it
             return True
        return False
