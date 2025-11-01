from agents.base_rag_retrieval_agent import BaseRAGRetrievalAgent

overview_prompt = """
You are a Kaggle competition information retrieval agent. Your role is to provide FACTUAL, CONTEXTUAL information about the competition - NOT strategic advice or recommendations.

Competition Information:
-----------------
{section_content}

Your task: Extract and present the KEY FACTS clearly and concisely:

1. **Core Information**: What is this competition about? What's the objective?
2. **Data Context**: What kind of data? How much? What features?
3. **Evaluation Details**: What metric? How is success measured?
4. **Competition Type**: Binary classification? Regression? Structured/unstructured data?
5. **Key Constraints**: Deadlines, submission format, special rules

BE FACTUAL, not advisory. Provide context and information that reasoning agents can use to formulate recommendations.

DO NOT:
- Give strategic advice ("you should try X model")
- Recommend specific approaches
- Provide step-by-step guides

DO:
- Present facts clearly
- Give context about the competition
- Explain what the data/metric means
- Note important constraints

Competition: {competition}
User Level: {user_level}
Tone: {tone}

Response (factual retrieval, not strategic advice):
"""

evaluation_prompt = """
You are a Kaggle evaluation metric expert. Your role is to help competitors understand HOW their submissions will be scored and WHY the metric matters.

Metric Information:
------------------
Metric Name: {metric}
Competition: {competition}
Details: {details}

Provide a PRACTICAL explanation covering these 3 key areas:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ GOAL CLARIFICATION - What does this metric actually measure?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Explain clearly in 2-3 sentences:
- What behavior does this metric reward?
- Is it penalizing large errors more? Equal errors?
- Classification, regression, ranking, or something else?

Example frameworks:
- Accuracy: Rewards equal correct predictions on all classes
- RMSE: Penalizes large errors more heavily than small ones
- F1: Balances precision and recall for imbalanced data
- AUC: Evaluates ranking quality, not threshold choice

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2️⃣ OPTIMIZATION STRATEGY - How should competitors train/validate?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide 2-3 Python code snippets showing:
- Correct cross-validation approach (must match Kaggle's metric)
- What scoring parameter to use
- What NOT to use (common mistakes)

Examples:

FOR ACCURACY:
```python
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier()
# CORRECT: Use 'accuracy' - matches Kaggle metric
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"CV Accuracy: {{scores.mean():.4f}}")

# WRONG: Don't use these for pure accuracy metric
# scores = cross_val_score(model, X, y, cv=5, scoring='f1')  # ✗ Wrong metric
# scores = cross_val_score(model, X, y, cv=5, scoring='auc') # ✗ Wrong metric
```

FOR RMSE (Regression):
```python
from sklearn.metrics import mean_squared_error
import numpy as np

# CORRECT: Calculate RMSE the way Kaggle does
predictions = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
print(f"RMSE: {{rmse:.4f}}")

# COMMON MISTAKE: Using MAE instead of RMSE
# mae = mean_absolute_error(y_test, predictions)  # ✗ Wrong metric
```

FOR F1 (Imbalanced Classification):
```python
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_score

model = LogisticRegression()
# CORRECT: Use 'f1' for imbalanced classification
scores = cross_val_score(model, X, y, cv=5, scoring='f1')
print(f"CV F1: {{scores.mean():.4f}}")

# Single evaluation:
f1 = f1_score(y_test, model.predict(X_test))
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3️⃣ DATA PREPROCESSING IMPLICATIONS - How does this metric shape preprocessing?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide 3-4 practical tips specific to THIS metric:

FOR ACCURACY (balanced metric):
- ✓ No need for class weighting or oversampling
- ✓ Missing values matter equally across both classes
- ✓ Focus on feature quality, not class balancing
- ⚠️ Watch baseline: if 70% are class 0, random guessing = 70% accuracy

FOR RMSE (regression, penalizes large errors):
- ✓ Outlier handling is CRITICAL - RMSE penalizes large errors heavily
- ✓ Consider robust scaling or outlier capping
- ✓ Log-transform if targets are right-skewed
- ⚠️ A few bad predictions will heavily damage your score

FOR F1 (imbalanced classification):
- ✓ Must handle class imbalance (oversampling, undersampling, or weighting)
- ✓ Focus on minority class precision AND recall equally
- ✓ Don't just maximize accuracy at expense of recall
- ⚠️ Tuning threshold is often crucial for F1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 KEY TAKEAWAY:
Train your model using THE SAME metric Kaggle uses for scoring. Mismatched metrics 
are one of the most common reasons competitors underperform despite good models.

User Level: {user_level}
Tone: {tone}
"""

class CompetitionSummaryAgent(BaseRAGRetrievalAgent):
    """
    Comprehensive agent for competition information.
    Handles overview, evaluation metrics, and other competition details.
    Uses evaluation_prompt when the query is about evaluation metrics,
    otherwise uses the standard overview_prompt.
    """
    def __init__(self, retriever=None, llm=None, query_type="overview"):
        # Always use overview as default - we'll detect evaluation queries dynamically
        super().__init__(
            agent_name="CompetitionSummaryAgent",
            prompt_template=overview_prompt,
            section="overview",
            retriever=retriever,
            llm=llm
        )
        self.evaluation_prompt = evaluation_prompt
        self.overview_prompt = overview_prompt
    
    def run(self, structured_query: dict) -> dict:
        """Override run to detect evaluation queries and use appropriate prompt"""
        query = structured_query.get("cleaned_query", "").lower()
        
        # Detect if query is about evaluation metrics
        eval_keywords = ['evaluation', 'metric', 'score', 'scoring', 'measure', 'performance', 'leaderboard']
        is_eval_query = any(keyword in query for keyword in eval_keywords)
        
        if is_eval_query:
            # Fetch documents first to extract metric information
            metadata = structured_query.get("metadata", {})
            chunks = self.fetch_sections(structured_query)
            
            # Extract metric name from content
            combined_content = "\n".join([chunk.get("content", "") for chunk in chunks])
            metric_name = self._extract_metric_name(combined_content)
            
            # Update metadata with extracted metric info
            metadata["metric"] = metric_name
            metadata["details"] = combined_content[:500]  # First 500 chars as details
            metadata["competition"] = metadata.get("competition_slug", metadata.get("competition", "this competition"))
            
            # Temporarily switch to evaluation prompt
            original_template = self.chain.prompt.template if self.chain else None
            if self.chain:
                from langchain_core.prompts import PromptTemplate
                from langchain.chains import LLMChain
                self.chain = LLMChain(llm=self.llm, prompt=PromptTemplate.from_template(self.evaluation_prompt))
            
            # Generate response with evaluation prompt
            final_response = self.summarize_sections(chunks, metadata)
            
            # Restore original template
            if original_template and self.chain:
                self.chain = LLMChain(llm=self.llm, prompt=PromptTemplate.from_template(original_template))
            
            return {"agent_name": self.name, "response": final_response}
        else:
            return super().run(structured_query)
    
    def _extract_metric_name(self, content: str) -> str:
        """Extract metric name from content using simple keyword matching"""
        content_lower = content.lower()
        
        # Common metrics to look for
        metrics = {
            'accuracy': 'Accuracy',
            'rmse': 'RMSE (Root Mean Squared Error)',
            'mae': 'MAE (Mean Absolute Error)',
            'f1': 'F1-Score',
            'auc': 'AUC (Area Under the Curve)',
            'logloss': 'LogLoss',
            'r2': 'R² Score',
            'precision': 'Precision',
            'recall': 'Recall'
        }
        
        for key, name in metrics.items():
            if key in content_lower:
                return name
        
        return "the evaluation metric"


# Backwards compatibility alias
CompetitionOverviewAgent = CompetitionSummaryAgent
