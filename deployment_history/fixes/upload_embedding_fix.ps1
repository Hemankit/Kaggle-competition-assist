# Upload embedding dimension fix to EC2 and execute

$EC2_HOST = "ubuntu@18.219.148.57"
$KEY_PATH = "C:\Users\heman\Downloads\Key__2__Success.pem"
$PROJECT_DIR = "/home/ubuntu/Kaggle-competition-assist"

Write-Host "=========================================="
Write-Host "UPLOADING EMBEDDING DIMENSION FIX TO EC2"
Write-Host "=========================================="

# Upload fixed files
Write-Host ""
Write-Host "[1/5] Uploading minimal_backend.py..."
scp -i $KEY_PATH minimal_backend.py ${EC2_HOST}:${PROJECT_DIR}/

Write-Host ""
Write-Host "[2/5] Uploading RAG pipeline..."
scp -i $KEY_PATH RAG_pipeline_chromadb/rag_pipeline.py ${EC2_HOST}:${PROJECT_DIR}/RAG_pipeline_chromadb/

Write-Host ""
Write-Host "[3/5] Uploading populate script..."
scp -i $KEY_PATH populate_all_competition_data.py ${EC2_HOST}:${PROJECT_DIR}/

Write-Host ""
Write-Host "[4/5] Uploading fix script..."
scp -i $KEY_PATH fix_embedding_dimensions.sh ${EC2_HOST}:${PROJECT_DIR}/

# Make script executable and run it
Write-Host ""
Write-Host "[5/5] Running fix on EC2..."
ssh -i $KEY_PATH $EC2_HOST @"
cd $PROJECT_DIR
chmod +x fix_embedding_dimensions.sh
./fix_embedding_dimensions.sh
"@

Write-Host ""
Write-Host "=========================================="
Write-Host "DONE!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Your app is ready: http://18.219.148.57:8501"
Write-Host ""
Write-Host "Test data queries like:"
Write-Host "  - 'What data files are available?'"
Write-Host "  - 'Tell me about the train.csv file'"
Write-Host "  - 'What columns are in the data?'"



