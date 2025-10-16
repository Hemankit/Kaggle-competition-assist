#!/bin/bash
cd ~/Kaggle-competition-assist
cp Kaggle_Fetcher/kaggle_api_client.py Kaggle_Fetcher/kaggle_api_client.py.clean_backup
sed -i "s/getattr(f, 'totalBytes'/getattr(f, 'total_bytes'/g" Kaggle_Fetcher/kaggle_api_client.py
sed -i "s/getattr(f, 'creationDate'/getattr(f, 'creation_date'/g" Kaggle_Fetcher/kaggle_api_client.py
echo "✅ Attributes fixed!"


