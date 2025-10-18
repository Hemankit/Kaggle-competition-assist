"""
Manually populate Titanic data description (no scraping needed)
"""
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
import hashlib

def populate_titanic_data():
    """Add Titanic data description to ChromaDB."""
    
    print("[INFO] Connecting to ChromaDB...")
    rag_pipeline = ChromaDBRAGPipeline(collection_name="kaggle_competition_data")
    
    # Titanic data description sections
    sections = {
        "Overview": """The data has been split into two groups:

training set (train.csv) - should be used to build your machine learning models. For the training set, we provide the outcome (ground truth) for each passenger. Your model will be based on features like passengers' gender and class.

test set (test.csv) - should be used to see how well your model performs on unseen data. For the test set, we do not provide the ground truth for each passenger.""",
        
        "Data Dictionary": """Variable Definitions:
- survival: Survival (0 = No, 1 = Yes)
- pclass: Ticket class (1 = 1st, 2 = 2nd, 3 = 3rd)
- sex: Sex  
- Age: Age in years
- sibsp: # of siblings / spouses aboard the Titanic
- parch: # of parents / children aboard the Titanic
- ticket: Ticket number
- fare: Passenger fare
- cabin: Cabin number
- embarked: Port of Embarkation (C = Cherbourg, Q = Queenstown, S = Southampton)""",
        
        "Variable Notes": """pclass: A proxy for socio-economic status (SES)
- 1st = Upper
- 2nd = Middle
- 3rd = Lower

age: Age is fractional if less than 1. If the age is estimated, is it in the form of xx.5

sibsp: The dataset defines family relations in this way:
- Sibling = brother, sister, stepbrother, stepsister
- Spouse = husband, wife (mistresses and fiancés were ignored)

parch: The dataset defines family relations in this way:
- Parent = mother, father
- Child = daughter, son, stepdaughter, stepson

Some children travelled only with a nanny, therefore parch=0 for them."""
    }
    
    # Column info
    columns = [
        {"column": "survival", "description": "Survival (0 = No, 1 = Yes)"},
        {"column": "pclass", "description": "Ticket class (1 = 1st, 2 = 2nd, 3 = 3rd)"},
        {"column": "sex", "description": "Sex"},
        {"column": "Age", "description": "Age in years"},
        {"column": "sibsp", "description": "# of siblings / spouses aboard the Titanic"},
        {"column": "parch", "description": "# of parents / children aboard the Titanic"},
        {"column": "ticket", "description": "Ticket number"},
        {"column": "fare", "description": "Passenger fare"},
        {"column": "cabin", "description": "Cabin number"},
        {"column": "embarked", "description": "Port of Embarkation (C = Cherbourg, Q = Queenstown, S = Southampton)"}
    ]
    
    documents_to_add = []
    
    # Add sections
    for section_title, section_content in sections.items():
        content_hash = hashlib.md5(section_content.encode()).hexdigest()
        documents_to_add.append({
            "content": f"{section_title}\n\n{section_content}",
            "metadata": {
                "competition_slug": "titanic",
                "section": "data_description",
                "subsection": section_title.lower().replace(" ", "_"),
                "type": "section",
                "content_hash": content_hash
            }
        })
    
    # Add column info
    column_text = "Data Columns:\n\n"
    for col in columns:
        column_text += f"- **{col['column']}**: {col['description']}\n"
    
    content_hash = hashlib.md5(column_text.encode()).hexdigest()
    documents_to_add.append({
        "content": column_text,
        "metadata": {
            "competition_slug": "titanic",
            "section": "data_description",
            "subsection": "columns",
            "type": "column_info",
            "content_hash": content_hash
        }
    })
    
    # Index all documents
    print(f"[INFO] Adding {len(documents_to_add)} documents to ChromaDB...")
    success = rag_pipeline.indexer._index_chunks(documents_to_add)
    
    if success:
        print(f"[SUCCESS] Added {len(documents_to_add)} data description documents!")
        return True
    else:
        print("[ERROR] Failed to index documents")
        return False


if __name__ == "__main__":
    print("="*70)
    print("POPULATE TITANIC DATA DESCRIPTION")
    print("="*70)
    
    success = populate_titanic_data()
    
    if success:
        print("\n" + "="*70)
        print("SUCCESS - Titanic data description cached!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("FAILED")
        print("="*70)




