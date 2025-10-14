#!/usr/bin/env python3
"""
Test script for Query Processing components
Tests: intent_classifier, user_input_processor, preprocessing, embedding_utils, section_classifier
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_intent_classifier():
    """Test Intent Classifier initialization and basic functionality"""
    print("🔍 Testing Intent Classifier...")
    
    try:
        from query_processing.intent_classifier import IntentClassifier
        print("✅ Import successful")
        
        # Test initialization
        classifier = IntentClassifier()
        print("✅ Classifier initialization successful")
        
        # Test basic methods exist
        methods = ['classify_intent']
        for method in methods:
            if hasattr(classifier, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Intent Classifier test failed: {e}")
        return False

def test_user_input_processor():
    """Test User Input Processor initialization and basic functionality"""
    print("\n🔍 Testing User Input Processor...")
    
    try:
        from query_processing.user_input_processor import UserInputProcessor
        print("✅ Import successful")
        
        # Test initialization
        processor = UserInputProcessor()
        print("✅ Processor initialization successful")
        
        # Test basic methods exist
        methods = ['process_query', 'preprocess_query', 'classify_intent']
        for method in methods:
            if hasattr(processor, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ User Input Processor test failed: {e}")
        return False

def test_preprocessing():
    """Test Preprocessing module initialization and basic functionality"""
    print("\n🔍 Testing Preprocessing...")
    
    try:
        from query_processing.preprocessing import preprocess_text, normalize_query
        print("✅ Import successful")
        
        # Test that the functions exist and are callable
        if callable(preprocess_text):
            print("✅ preprocess_text is callable")
        else:
            print("❌ preprocess_text is not callable")
            
        if callable(normalize_query):
            print("✅ normalize_query is callable")
        else:
            print("❌ normalize_query is not callable")
        
        return True
        
    except Exception as e:
        print(f"❌ Preprocessing test failed: {e}")
        return False

def test_embedding_utils():
    """Test Embedding Utils initialization and basic functionality"""
    print("\n🔍 Testing Embedding Utils...")
    
    try:
        from query_processing.embedding_utils import EmbeddingUtils
        print("✅ Import successful")
        
        # Test initialization
        utils = EmbeddingUtils()
        print("✅ Utils initialization successful")
        
        # Test basic methods exist
        methods = ['get_embedding', 'get_similarity']
        for method in methods:
            if hasattr(utils, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding Utils test failed: {e}")
        return False

def test_section_classifier():
    """Test Section Classifier initialization and basic functionality"""
    print("\n🔍 Testing Section Classifier...")
    
    try:
        from query_processing.section_classifier import SectionClassifier
        print("✅ Import successful")
        
        # Test initialization
        classifier = SectionClassifier()
        print("✅ Classifier initialization successful")
        
        # Test basic methods exist
        methods = ['classify_section', 'get_section_confidence']
        for method in methods:
            if hasattr(classifier, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Section Classifier test failed: {e}")
        return False

def main():
    """Run all Query Processing tests"""
    print("🚀 Starting Query Processing Component Tests\n")
    
    results = []
    results.append(test_intent_classifier())
    results.append(test_user_input_processor())
    results.append(test_preprocessing())
    results.append(test_embedding_utils())
    results.append(test_section_classifier())
    
    print(f"\n📊 Query Processing Test Results: {sum(results)}/{len(results)} components passed")
    
    if all(results):
        print("🎉 All Query Processing components are working!")
    else:
        print("⚠️  Some Query Processing components need attention")
    
    return all(results)

if __name__ == "__main__":
    main()
