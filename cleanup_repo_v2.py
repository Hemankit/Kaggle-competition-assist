#!/usr/bin/env python3
"""
Comprehensive Repository Cleanup Script - Pre-Launch
Organizes files into proper directories and removes temporary files
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Define cleanup operations
CLEANUP_OPERATIONS = {
    "test_scripts_to_archive": {
        "destination": "archive/tests",
        "files": [
            "check_chromadb_discussions.py",
            "check_chromadb_notebooks.py",
            "check_chromadb_simple.py",
            "check_collection_metadata.py",
            "check_notebook_keys.py",
            "check_notebook_metadata.py",
            "test_agent_labels.py",
            "test_chromadb_content.py",
            "test_data_scraper.py",
            "test_discussion_query.py",
            "test_embedding_model.py",
            "test_evaluation_detailed.py",
            "test_evaluation_fix.py",
            "test_frontend_quick.py",
            "test_intent_routing.py",
            "test_notebook_query.py",
            "test_orchestration_agents.py",
            "test_query_vs_get.py",
            "test_routing_fix.py",
        ]
    },
    "populate_scripts_to_archive": {
        "destination": "archive/data_population",
        "files": [
            "populate_all_competition_data.py",
            "populate_data_description.py",
            "populate_titanic_data_manual.py",
            "reset_chromadb.py",
        ]
    },
    "deployment_scripts_to_history": {
        "destination": "deployment_history/fixes",
        "files": [
            "upload_embedding_fix.ps1",
            "upload_populate_fix.ps1",
            "install_playwright_ec2.sh",
            "fix_embedding_dimensions.sh",
            "fix_handler_tracking.py",
        ]
    },
    "documentation_to_archive": {
        "destination": "archive/documentation",
        "files": [
            "ALL_AGENTS_AUDIT_FINAL.md",
            "ARCHITECTURE_DIAGRAM_FINAL.txt",
            "CLARIFICATION_SUMMARY.md",
            "CRITICAL_AGENT_IMPLEMENTATION_AUDIT.md",
            "END_OF_DAY_SUMMARY.md",
            "FINAL_READINESS_CHECKLIST.md",
            "IDEA_INITIATOR_AGENT_AUDIT.md",
            "ORCHESTRATOR_FIX_COMPLETE.md",
            "ORCHESTRATOR_ROLE_EXPLAINED.md",
            "ORCHESTRATOR_STATUS_REPORT.md",
            "ORCHESTRATOR_VS_YOUR_MODEL.txt",
            "PRODUCTION_READY_CONFIRMATION.md",
            "QUERY_FLOW_ARCHITECTURE_EXPLAINED.md",
            "TOMORROW_TASKS.md",
        ]
    },
    "remove_files": [
        "backend_output.log",
        "QUICK_TEST_REFERENCE.txt",
    ]
}

def move_files(files, destination):
    """Move files to destination directory"""
    dest_path = BASE_DIR / destination
    dest_path.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    for file in files:
        source = BASE_DIR / file
        if source.exists():
            dest = dest_path / file
            print(f"Moving: {file} -> {destination}/")
            shutil.move(str(source), str(dest))
            moved_count += 1
        else:
            print(f"WARNING: Not found: {file}")
    
    return moved_count

def remove_files(files):
    """Remove files from repository"""
    removed_count = 0
    for file in files:
        file_path = BASE_DIR / file
        if file_path.exists():
            print(f"Removing: {file}")
            file_path.unlink()
            removed_count += 1
        else:
            print(f"WARNING: Not found: {file}")
    
    return removed_count

def main():
    print("REPOSITORY CLEANUP - PRE-LAUNCH")
    print("=" * 60)
    
    total_moved = 0
    total_removed = 0
    
    # Move test scripts
    print("\n[1/5] Moving test scripts to archive...")
    count = move_files(
        CLEANUP_OPERATIONS["test_scripts_to_archive"]["files"],
        CLEANUP_OPERATIONS["test_scripts_to_archive"]["destination"]
    )
    total_moved += count
    
    # Move populate scripts
    print("\n[2/5] Moving population scripts to archive...")
    count = move_files(
        CLEANUP_OPERATIONS["populate_scripts_to_archive"]["files"],
        CLEANUP_OPERATIONS["populate_scripts_to_archive"]["destination"]
    )
    total_moved += count
    
    # Move deployment scripts
    print("\n[3/5] Moving deployment scripts to history...")
    count = move_files(
        CLEANUP_OPERATIONS["deployment_scripts_to_history"]["files"],
        CLEANUP_OPERATIONS["deployment_scripts_to_history"]["destination"]
    )
    total_moved += count
    
    # Move documentation
    print("\n[4/5] Moving old documentation to archive...")
    count = move_files(
        CLEANUP_OPERATIONS["documentation_to_archive"]["files"],
        CLEANUP_OPERATIONS["documentation_to_archive"]["destination"]
    )
    total_moved += count
    
    # Remove temporary files
    print("\n[5/5] Removing temporary files...")
    total_removed = remove_files(CLEANUP_OPERATIONS["remove_files"])
    
    # Summary
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE!")
    print(f"   Files moved: {total_moved}")
    print(f"   Files removed: {total_removed}")
    print("\nRepository is now clean and ready for launch!")
    print("=" * 60)

if __name__ == "__main__":
    main()

