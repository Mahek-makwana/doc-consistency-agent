import os
import sys
import json
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.utils.consistency_checker import ConsistencyChecker
from src.agent.ai_suggester import suggester
from src.agent.git_manager import GitManager

class CraftAIPipeline:
    """
    Combined Idea 1 + Idea 3 Pipeline.
    1. Statistical Analysis (Idea 1)
    2. Auto-Documentation & Git Automation (Idea 3)
    """
    
    def __init__(self, code_dir="src", doc_dir="docs"):
         self.checker = ConsistencyChecker(code_dir=code_dir, doc_dir=doc_dir)
         self.git_manager = GitManager(repo_path=".")
         self.stats = {}

    def run(self, perform_git_actions=False):
        print("🚀 Starting CraftAI Consistency Pipeline...")
        
        # --- Step 1: Analysis (Idea 1) ---
        print("🔍 Phase 1: Statistical & Semantic Analysis...")
        results = self.checker.run_check()
        self.stats = results["stats"]
        
        print(f"   Matches analyzed: {len(results['matches'])}")
        print(f"   Average Symmetry Score: {self.stats.get('average_similarity', 0)}")
        
        # --- Step 2: Auto-Generation (Idea 3) ---
        print("✨ Phase 2: Auto-Documentation Generation...")
        
        changes_made = False
        auto_docs_dir = os.path.join("docs", "auto_generated")
        os.makedirs(auto_docs_dir, exist_ok=True)
        
        # 2a. Handle Missing Documentation
        for missing_func in results["missing_docs"]:
            print(f"   Found undocumented function: {missing_func}. Generating docs...")
            
            # Retrieve code snippet (Mocking retrieval for now, in real app we'd get from parser)
            # logic to get code content would go here.
            # We'll generate a placeholder + suggestion.
            
            doc_content = suggester.suggest_markdown_doc(
                title=f"Documentation for {missing_func}",
                summary=f"Auto-generated documentation for function {missing_func} detected in source code."
            )
            
            filename = f"{missing_func}.md"
            filepath = os.path.join(auto_docs_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(doc_content)
                
            print(f"   -> Wrote {filepath}")
            changes_made = True
            
        # 2b. Handle Outdated/Low Consistency
        for match in results["matches"]:
            if match["similarity_score"] < 0.4:
                print(f"   ⚠️ Low consistency for {match['name']} ({match['similarity_score']}). Suggesting update...")
                
                # In a real scenario, we might overwrite or create a specific update file
                update_content = suggester.suggest_markdown_doc(
                    title=f"Update for {match['name']}",
                    summary=f"Existing docs match score is low ({match['similarity_score']}).\nIssues: {match['issues']}"
                )
                
                # Save as a suggestion file
                filename = f"{match['name']}_update_suggestion.md"
                filepath = os.path.join(auto_docs_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(update_content)
                changes_made = True

        # --- Step 3: Git Automation (Idea 3) ---
        if perform_git_actions and changes_made:
            print("🤖 Phase 3: Git Automation...")
            try:
                branch_name = self.git_manager.create_branch(base_name="craftai-auto-docs")
                self.git_manager.commit_changes(message=f"CraftAI: Auto-generated docs and consistency updates")
                
                # Mock Push if no remote credentials, or try real push
                # We'll just try and catch error
                success = self.git_manager.push_branch(branch_name)
                
                if success:
                    print(f"   ✅ Changes pushed to {branch_name}. Auto-PR created (simulated).")
                else:
                    print(f"   ⚠️ Changes committed to local branch {branch_name}, but push failed (check credentials).")
                    
            except Exception as e:
                print(f"   ❌ Git automation failed: {e}")
        elif not changes_made:
            print("   No documentation updates needed.")
        else:
            print("   Git actions skipped (use --git to enable).")

        # --- Step 4: Report ---
        print("📊 Pipeline Complete. Summary:")
        print(f"   Functions Checked: {self.stats['total_functions']}")
        print(f"   Documentation Consistency: {self.stats['average_similarity'] * 100:.1f}%")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--git", action="store_true", help="Enable Git operations")
    args = parser.parse_args()
    
    pipeline = CraftAIPipeline()
    pipeline.run(perform_git_actions=args.git)
