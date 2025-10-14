#!/usr/bin/env python3
"""
Repository Cleanup Script

Organizes files into:
- tests/ (all test files)
- archive/ (unused/debug/experimental files)
- docs/ (markdown documentation)

Run this before deployment!
"""
import os
import shutil
from pathlib import Path

# Test files to move to tests/ folder
TEST_FILES = [
    "test_backend_agent_integration.py",
    "test_backend_comprehensive.py",
    "test_backend_flask_app.py",
    "test_backend_health.py",
    "test_backend_logging.py",
    "test_cache_debug.py",
    "test_cache_optimization.py",
    "test_chromadb_integration.py",
    "test_comprehensive_full_scale.py",
    "test_discussion_ocr.py",
    "test_discussion_scraper.py",
    "test_dynamic_orchestrator.py",
    "test_flask_backend.py",
    "test_integration_quick.py",
    "test_kaggle_api.py",
    "test_llm_config.py",
    "test_llm_initialization.py",
    "test_multiagent_component.py",
    "test_multiagent_final.py",
    "test_multiagent_simple.py",
    "test_multiagent_structure.py",
    "test_multiagent_system.py",
    "test_workflow_fixes.py",
    "test_working_llms.py",
]

# Unused/debug/experimental files to archive
ARCHIVE_FILES = [
    "analyze_discussion_html.py",
    "check_discussion_url.py",
    "debug_chromadb_structure.py",
    "debug_discussion_html.py",
    "debug_discussion.html",
    "debug_overview_scraper.py",
    "discussion_page_source.html",
    "backend_error.txt",
    "backend_output.txt",
    "comprehensive_test_results.json",
    "rmdir",
    "main.py",  # Old entry point (minimal_backend.py is main now)
    "run_app.py",  # Old entry point
    "start_backend.py",  # Old entry point
]

# Folders to archive
ARCHIVE_FOLDERS = [
    "null",  # Unused agent folder
    "llm_tests",  # Old LLM tests
    "notebook",  # Experimental notebooks
    "agent_tests",  # Old agent tests (use component_tests instead)
]

# Markdown documentation to move to docs/
MARKDOWN_FILES = [
    "INTEGRATION_COMPLETE.md",
    "LEADERBOARD_INTEGRATION.md",
    "COMMUNITY_ENGAGEMENT_WORKFLOW.md",
    "COMMUNITY_ENGAGEMENT_AGENT_SUMMARY.md",
    "COMMUNITY_ENGAGEMENT_COMPLETE.md",
    "DEPLOYMENT_STRATEGY.md",
    "DEPLOYMENT_CHECKLIST.md",
    "DISCUSSION_PHASE_SUMMARY.md",
    "LLM_CONFIGURATION_SUMMARY.md",
    "TOMORROW_DEPLOYMENT_PLAN.md",
    "TODAY_ACHIEVEMENTS.md",
]

# Keep these markdown files in root
KEEP_IN_ROOT = [
    "README.md",
    "preflight_checklist.md",
]

def create_directories():
    """Create tests, archive, and docs directories."""
    os.makedirs("tests", exist_ok=True)
    os.makedirs("archive", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    print("✅ Created directories: tests/, archive/, docs/")

def move_tests_to_tests_folder():
    """Move test files to tests/ folder."""
    moved = 0
    skipped = 0
    for file in TEST_FILES:
        if os.path.exists(file):
            try:
                dest = f"tests/{file}"
                if os.path.exists(dest):
                    print(f"   ⚠️  Skipping {file} (already exists in tests/)")
                    skipped += 1
                else:
                    shutil.move(file, dest)
                    print(f"   → Moved {file} to tests/")
                    moved += 1
            except Exception as e:
                print(f"   ❌ Failed to move {file}: {e}")
    
    print(f"✅ Moved {moved} test files to tests/ (skipped {skipped})")

def move_to_archive():
    """Move unused files and folders to archive."""
    moved = 0
    
    # Move files
    for file in ARCHIVE_FILES:
        if os.path.exists(file):
            try:
                dest = f"archive/{file}"
                shutil.move(file, dest)
                print(f"   → Moved {file} to archive/")
                moved += 1
            except Exception as e:
                print(f"   ❌ Failed to move {file}: {e}")
    
    # Move folders
    for folder in ARCHIVE_FOLDERS:
        if os.path.exists(folder):
            try:
                dest = f"archive/{folder}"
                if os.path.exists(dest):
                    print(f"   ⚠️  Skipping {folder}/ (already exists in archive/)")
                else:
                    shutil.move(folder, dest)
                    print(f"   → Moved {folder}/ to archive/")
                    moved += 1
            except Exception as e:
                print(f"   ❌ Failed to move {folder}/: {e}")
    
    print(f"✅ Archived {moved} files/folders")

def move_to_docs():
    """Move markdown files to docs."""
    moved = 0
    for file in MARKDOWN_FILES:
        if os.path.exists(file):
            try:
                dest = f"docs/{file}"
                shutil.move(file, dest)
                print(f"   → Moved {file} to docs/")
                moved += 1
            except Exception as e:
                print(f"   ❌ Failed to move {file}: {e}")
    
    print(f"✅ Moved {moved} markdown files to docs/")

def delete_empty_folders():
    """Delete empty directories and files."""
    deleted_folders = 0
    deleted_files = 0
    
    # Delete empty folders
    for root, dirs, files in os.walk(".", topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # Skip important folders
            if dir_name in ["__pycache__", ".git", "node_modules", "chroma_db", "logs", "data"]:
                continue
            # Delete if empty
            try:
                if os.path.isdir(dir_path) and not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"   → Deleted empty folder: {dir_path}")
                    deleted_folders += 1
            except Exception as e:
                pass  # Silently skip if can't delete
    
    # Delete specific empty/unused files
    empty_files = ["rmdir"] if not os.path.exists("rmdir") else []
    
    # Check for empty __init__.py files (keep them, they're needed for Python packages)
    
    print(f"✅ Deleted {deleted_folders} empty folders")
    if deleted_files > 0:
        print(f"✅ Deleted {deleted_files} empty/unused files")

def create_gitignore_entries():
    """Add analytics.db and logs to .gitignore."""
    gitignore_entries = [
        "\n# Analytics and Logs\n",
        "data/analytics.db\n",
        "logs/*.log\n",
        "logs/trace_*.json\n",
        "logs/langgraph_execution.png\n",
    ]
    
    try:
        with open(".gitignore", "a") as f:
            f.writelines(gitignore_entries)
        print("✅ Updated .gitignore with analytics/logs entries")
    except Exception as e:
        print(f"⚠️ Could not update .gitignore: {e}")

def print_summary():
    """Print final directory structure."""
    print("\n" + "="*70)
    print("📁 CLEAN DIRECTORY STRUCTURE")
    print("="*70)
    print("""
Kaggle-competition-assist/
├── agents/               ✅ 11 specialized agents
├── orchestrators/        ✅ Multi-agent orchestration
├── routing/              ✅ Agent registry & routing
├── evaluation/           ✅ Guideline validation
├── Kaggle_Fetcher/       ✅ API integration
├── RAG_pipeline_chromadb/ ✅ Vector storage
├── scraper/              ✅ Playwright scraping
├── llms/                 ✅ Multi-model LLM config
├── query_processing/     ✅ Intent classification
├── hybrid_scraping_routing/ ✅ Deep scraping
├── workflows/            ✅ LangGraph workflows
├── frontend/             ✅ React frontend
├── streamlit_frontend/   ✅ Streamlit UI
├── data/                 ✅ Guidelines & discussions
├── chroma_db/            ✅ Vector database
├── logs/                 ✅ Application logs
├── tests/                🆕 All test files
├── docs/                 🆕 All documentation
├── archive/              🆕 Old/unused files
├── component_tests/      ✅ Integration tests
├── minimal_backend.py    ✅ Main backend
├── README.md             ✅ Project overview
├── requirements.txt      ✅ Dependencies
└── .env                  ✅ Configuration
    """)
    print("="*70)
    print("✅ Repository cleanup complete!")
    print("\n📊 Summary:")
    print(f"   • Test files organized in tests/")
    print(f"   • Documentation in docs/")
    print(f"   • Unused files in archive/")
    print(f"   • Empty folders removed")
    print("\n📋 Next Steps:")
    print("   1. Review moved files in tests/, archive/, and docs/")
    print("   2. Commit changes: git add -A && git commit -m 'Clean up repository structure'")
    print("   3. Start Phase 2: Competition Browser")
    print("\n🚀 Ready for deployment prep!")

if __name__ == "__main__":
    print("="*70)
    print("🧹 REPOSITORY CLEANUP - Starting...")
    print("="*70)
    print("\nThis script will:")
    print("  • Move test files to tests/")
    print("  • Move unused files to archive/")
    print("  • Move documentation to docs/")
    print("  • Delete empty folders")
    print("  • Update .gitignore")
    print("")
    
    print("\n1️⃣ Creating directories...")
    create_directories()
    
    print("\n2️⃣ Moving test files to tests/...")
    move_tests_to_tests_folder()
    
    print("\n3️⃣ Moving unused files to archive/...")
    move_to_archive()
    
    print("\n4️⃣ Moving markdown files to docs/...")
    move_to_docs()
    
    print("\n5️⃣ Deleting empty folders...")
    delete_empty_folders()
    
    print("\n6️⃣ Updating .gitignore...")
    create_gitignore_entries()
    
    print_summary()
    
    print("\n🎉 CLEANUP COMPLETE! Repository is organized and ready for deployment prep.")


