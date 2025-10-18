#!/usr/bin/env python3
from routing.intent_router import parse_user_intent
from routing.capability_scoring import find_agents_by_subintent

queries = [
    'Give me some starter ideas',
    'Help me create a timeline',
    'How am I doing?',
    'I am stuck at 0.75'
]

for query in queries:
    print(f'\n==== Query: {query} ====')
    parsed = parse_user_intent(query)
    print(f'Parsed intent: {parsed}')
    
    subintents = parsed.get('sub_intents', [])
    reasoning_style = parsed.get('reasoning_style')
    
    print(f'Subintents: {subintents}')
    print(f'Reasoning style: {reasoning_style}')
    
    for subintent in subintents:
        matches = find_agents_by_subintent(subintent, reasoning_style)
        print(f'  Subintent "{subintent}" matches: {[m["agent"] for m in matches]}')

