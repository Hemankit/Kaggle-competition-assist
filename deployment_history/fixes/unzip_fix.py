#!/usr/bin/env python3
import zipfile
import shutil

zipfile.ZipFile('kaggle_api_client.zip').extractall()
shutil.move('kaggle_api_client_temp.py', 'Kaggle_Fetcher/kaggle_api_client.py')
print('✅ File restored successfully!')


