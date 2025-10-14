#!/usr/bin/env python3
"""
Comprehensive Kaggle API Test
Tests what competitions and data are actually accessible
"""

from kaggle.api.kaggle_api_extended import KaggleApi
import json

def test_kaggle_api():
    print('=== KAGGLE API COMPREHENSIVE TEST ===')
    print()
    
    api = KaggleApi()
    api.authenticate()
    
    # Test 1: List all competitions
    print('1. Testing competitions_list():')
    try:
        comps = api.competitions_list()
        print(f'   ✅ Found {len(comps)} competitions')
        print('   📋 First 5 competitions:')
        for i, comp in enumerate(comps[:5]):
            print(f'      {i+1}. {comp.ref}: {comp.title}')
            print(f'         Category: {getattr(comp, "category", "N/A")}')
            print(f'         Deadline: {getattr(comp, "deadline", "N/A")}')
            print(f'         Prize: {getattr(comp, "prize", "N/A")}')
            print()
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    print('\n' + '='*50)
    
    # Test 2: Try to get detailed info for specific competitions
    print('2. Testing competition details access:')
    
    test_competitions = [
        'titanic',
        'house-prices-advanced-regression-techniques', 
        'arc-prize-2025',
        'nfl-big-data-bowl-2026-analytics',
        'nfl-big-data-bowl-2026-prediction'
    ]
    
    for comp_slug in test_competitions:
        print(f'\n   Testing: {comp_slug}')
        try:
            # Try different methods to get competition details
            comp_details = None
            
            # Method 1: Try to find in competitions list
            try:
                comps = api.competitions_list()
                for comp in comps:
                    if comp.ref == comp_slug or comp.ref.endswith(comp_slug):
                        comp_details = comp
                        print(f'      ✅ Found in competitions_list: {comp.title}')
                        break
            except Exception as e:
                print(f'      ❌ competitions_list method failed: {e}')
            
            # Method 2: Try competition_view if available
            if not comp_details:
                try:
                    if hasattr(api, 'competition_view'):
                        comp_details = api.competition_view(comp_slug)
                        print(f'      ✅ competition_view worked')
                    elif hasattr(api, 'competition'):
                        comp_details = api.competition(comp_slug)
                        print(f'      ✅ competition method worked')
                    else:
                        print(f'      ❌ No competition detail methods available')
                except Exception as e:
                    print(f'      ❌ competition_view failed: {e}')
            
            # Method 3: Try kernels_list for this competition
            try:
                kernels = api.kernels_list(competition=comp_slug, page=1, page_size=5)
                if kernels:
                    print(f'      ✅ Found {len(kernels)} notebooks via kernels_list')
                else:
                    print(f'      ⚠️  No notebooks found via kernels_list')
            except Exception as e:
                print(f'      ❌ kernels_list failed: {e}')
            
            # Method 4: Try datasets_list for this competition
            try:
                datasets = api.datasets_list(competition=comp_slug, page=1, page_size=5)
                if datasets:
                    print(f'      ✅ Found {len(datasets)} datasets via datasets_list')
                else:
                    print(f'      ⚠️  No datasets found via datasets_list')
            except Exception as e:
                print(f'      ❌ datasets_list failed: {e}')
                
        except Exception as e:
            print(f'      ❌ Overall test failed: {e}')
    
    print('\n' + '='*50)
    
    # Test 3: Check what methods are available on the API object
    print('3. Available API methods:')
    methods = [method for method in dir(api) if not method.startswith('_')]
    competition_methods = [method for method in methods if 'competition' in method.lower()]
    kernel_methods = [method for method in methods if 'kernel' in method.lower()]
    dataset_methods = [method for method in methods if 'dataset' in method.lower()]
    
    print(f'   Competition methods: {competition_methods}')
    print(f'   Kernel methods: {kernel_methods}')
    print(f'   Dataset methods: {dataset_methods}')
    
    print('\n' + '='*50)
    print('TEST COMPLETE')

if __name__ == "__main__":
    test_kaggle_api()

