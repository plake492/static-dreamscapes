#!/usr/bin/env python3
"""Fetch and display track data from Notion"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.notion_service import NotionService
from dotenv import load_dotenv

load_dotenv()

def main():
    notion_token = os.getenv('NOTION_TOKEN')
    if not notion_token:
        print('Error: NOTION_TOKEN not found in .env')
        sys.exit(1)

    service = NotionService(notion_token)

    # Track 999
    print('=== TRACK 999 (MASTER) ===')
    track_999 = service.fetch_track_data('https://www.notion.so/Track-999-MASTER-ARC-01-NEON-RAIN-NIGHT-CODING-2cb433e57885801a89cafc2b195862e7')
    print(f'Title: {track_999.title}')
    print(f'Number of Arcs: {len(track_999.arcs)}')
    for arc in track_999.arcs:
        print(f'\nArc {arc.arc_number}: {arc.mood_description}')
        print(f'Prompts ({len(arc.prompts)}):')
        for prompt in arc.prompts:
            print(f'  {prompt.prompt_number}. {prompt.text[:100]}{"..." if len(prompt.text) > 100 else ""}')

    print('\n\n=== TRACK 26 ===')
    track_26 = service.fetch_track_data('https://www.notion.so/Track-26-Pre-Dawn-Coding-Desk-3HR-LoFi-Synthwave-Mix-Calm-Focus-Before-Sunrise-Royalty-Free-2cd433e5788580d6b4dbfe24378a71b6')
    print(f'Title: {track_26.title}')
    print(f'Number of Arcs: {len(track_26.arcs)}')
    for arc in track_26.arcs:
        print(f'\nArc {arc.arc_number}: {arc.mood_description}')
        print(f'Prompts ({len(arc.prompts)}):')
        for prompt in arc.prompts:
            print(f'  {prompt.prompt_number}. {prompt.text[:100]}{"..." if len(prompt.text) > 100 else ""}')

if __name__ == '__main__':
    main()
