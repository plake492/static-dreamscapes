"""Notion API integration and parser."""

import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import logging

from notion_client import Client
from notion_client.errors import APIResponseError

from ..core.models import NotionTrackMetadata, NotionArc, NotionPrompt
from ..core.config import get_config

logger = logging.getLogger(__name__)


class NotionParser:
    """Parse Notion track documents into structured metadata."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Notion client.

        Args:
            api_token: Notion API token (if None, loads from config)
        """
        if api_token is None:
            config = get_config()
            api_token = config.notion_api_token

        if not api_token:
            raise ValueError("Notion API token not provided. Set NOTION_API_TOKEN environment variable.")

        self.client = Client(auth=api_token)
        self.cache_dir = Path("./data/cache/notion_docs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def parse_notion_doc(self, notion_url: str) -> NotionTrackMetadata:
        """
        Parse complete Notion track document.

        Args:
            notion_url: URL to Notion page

        Returns:
            NotionTrackMetadata with all parsed data
        """
        logger.info(f"Parsing Notion doc: {notion_url}")

        # Extract page ID from URL
        page_id = self._extract_page_id(notion_url)

        # Fetch content
        page = self._fetch_page(page_id)
        blocks = self._fetch_blocks(page_id)

        # Convert to markdown for easier parsing
        markdown = self._blocks_to_markdown(blocks)

        # Cache raw content
        self._cache_content(page_id, markdown)

        # Parse sections
        overview = self._parse_track_overview(markdown)
        seo = self._parse_seo_section(markdown)
        music = self._parse_music_arc_structure(markdown)

        # Extract description
        description = self._extract_description(markdown)

        # Infer overall theme
        overall_theme = self._infer_theme(
            overview.get('title', ''),
            description,
            seo.get('visible_hashtags', [])
        )

        # Build NotionArc objects
        notion_arcs = []
        for arc_data in music['arcs']:
            prompts = [
                NotionPrompt(**prompt_data)
                for prompt_data in arc_data['prompts']
            ]

            notion_arc = NotionArc(
                arc_number=arc_data['arc_number'],
                arc_name=arc_data['arc_name'],
                description=arc_data.get('description'),
                prompts=prompts,
                target_duration_minutes=overview['duration_target_minutes'] // 4
            )
            notion_arcs.append(notion_arc)

        # Build final metadata object
        metadata = NotionTrackMetadata(
            notion_url=notion_url,
            title=overview['title'],
            output_filename=overview['output_filename'],
            upload_schedule=overview.get('upload_schedule'),
            duration_target_minutes=overview['duration_target_minutes'],
            overall_theme=overall_theme,
            mood_arc=overview.get('mood_arc'),
            vibe_description=description,
            visible_hashtags=seo['visible_hashtags'],
            hidden_tags=seo['hidden_tags'],
            ctr_target=overview.get('ctr_target'),
            retention_target=overview.get('retention_target'),
            arcs=notion_arcs,
            raw_notion_content={'markdown': markdown}
        )

        logger.info(f"Successfully parsed Notion doc: {metadata.title}")
        return metadata

    def _extract_page_id(self, notion_url: str) -> str:
        """Extract page ID from Notion URL."""
        # URL formats:
        # https://www.notion.so/Page-Title-abc123def456
        # https://notion.so/workspace/abc123def456?v=...

        # Extract the UUID (32 hex chars with optional hyphens)
        match = re.search(r'([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', notion_url, re.IGNORECASE)

        if not match:
            raise ValueError(f"Could not extract page ID from URL: {notion_url}")

        page_id = match.group(1).replace('-', '')
        logger.debug(f"Extracted page ID: {page_id}")
        return page_id

    def _fetch_page(self, page_id: str) -> Dict:
        """Fetch page metadata from Notion API."""
        try:
            return self.client.pages.retrieve(page_id=page_id)
        except APIResponseError as e:
            logger.error(f"Error fetching page: {e}")
            raise

    def _fetch_blocks(self, page_id: str) -> List[Dict]:
        """Fetch page blocks from Notion API."""
        try:
            blocks = []
            has_more = True
            start_cursor = None

            while has_more:
                response = self.client.blocks.children.list(
                    block_id=page_id,
                    start_cursor=start_cursor
                )
                blocks.extend(response['results'])
                has_more = response['has_more']
                start_cursor = response.get('next_cursor')

            return blocks
        except APIResponseError as e:
            logger.error(f"Error fetching blocks: {e}")
            raise

    def _blocks_to_markdown(self, blocks: List[Dict]) -> str:
        """Convert Notion blocks to markdown text."""
        markdown_lines = []

        for block in blocks:
            block_type = block['type']

            if block_type == 'heading_1':
                text = self._extract_text(block['heading_1'])
                markdown_lines.append(f"# {text}")

            elif block_type == 'heading_2':
                text = self._extract_text(block['heading_2'])
                markdown_lines.append(f"## {text}")

            elif block_type == 'heading_3':
                text = self._extract_text(block['heading_3'])
                markdown_lines.append(f"### {text}")

            elif block_type == 'bulleted_list_item':
                text = self._extract_text(block['bulleted_list_item'])
                markdown_lines.append(f"- {text}")

            elif block_type == 'to_do':
                text = self._extract_text(block['to_do'])
                checked = block['to_do'].get('checked', False)
                checkbox = "[x]" if checked else "[ ]"
                markdown_lines.append(f"- {checkbox} {text}")

            elif block_type == 'paragraph':
                text = self._extract_text(block['paragraph'])
                markdown_lines.append(text)

        return "\n".join(markdown_lines)

    def _extract_text(self, rich_text_block: Dict) -> str:
        """Extract plain text from Notion rich text object."""
        rich_text = rich_text_block.get('rich_text', [])
        return "".join([text_obj.get('plain_text', '') for text_obj in rich_text])

    def _parse_track_overview(self, markdown: str) -> Dict:
        """Parse the TRACK OVERVIEW section."""
        result = {}

        # Title - try multiple formats
        # Format 1: **Title:** **title**
        title_match = re.search(r'\*\*Title:\*\*\s*\*\*(.*?)\*\*', markdown, re.IGNORECASE)
        if not title_match:
            # Format 2: ✅ SEO Title: title
            title_match = re.search(r'(?:✅|☑)\s*SEO Title:\s*(.+?)(?:\n|$)', markdown, re.IGNORECASE)
        result['title'] = title_match.group(1).strip() if title_match else "Untitled Track"

        # Filename - try multiple formats
        # Format 1: **Filename:** filename.mp4
        filename_match = re.search(r'\*\*Filename:\*\*\s*(.+?)\.mp4', markdown, re.IGNORECASE)
        if not filename_match:
            # Format 2: ✅ Filename: filename.mp4
            filename_match = re.search(r'(?:✅|☑)\s*Filename:\s*(.+?)\.mp4', markdown, re.IGNORECASE)
        result['output_filename'] = filename_match.group(1).strip() + ".mp4" if filename_match else "output.mp4"

        # Upload schedule
        schedule_match = re.search(r'\*\*Upload Schedule:\*\*\s*\*\*(.+?)\*\*', markdown, re.IGNORECASE)
        result['upload_schedule'] = schedule_match.group(1).strip() if schedule_match else None

        # Duration
        duration_match = re.search(r'\*\*Duration:\*\*\s*(\d+)\s*hour', markdown, re.IGNORECASE)
        duration_hours = int(duration_match.group(1)) if duration_match else 3
        result['duration_target_minutes'] = duration_hours * 60

        # Mood arc
        mood_match = re.search(r'\*\*Mood Arc:\*\*\s*(.+?)(?:\n|$)', markdown, re.IGNORECASE)
        result['mood_arc'] = mood_match.group(1).strip() if mood_match else None

        # CTR target
        ctr_match = re.search(r'\*\*CTR Target:\*\*\s*(.+?)(?:\n|$)', markdown, re.IGNORECASE)
        result['ctr_target'] = ctr_match.group(1).strip() if ctr_match else None

        # Retention target
        retention_match = re.search(r'\*\*Retention Target:\*\*\s*(.+?)(?:\n|$)', markdown, re.IGNORECASE)
        result['retention_target'] = retention_match.group(1).strip() if retention_match else None

        return result

    def _parse_seo_section(self, markdown: str) -> Dict:
        """Parse hashtags and tags."""
        result = {'visible_hashtags': [], 'hidden_tags': []}

        # Visible hashtags
        hashtags_match = re.search(r'\*\*Visible Hashtags:\*\*\s*(.+?)(?:\n|$)', markdown, re.IGNORECASE)
        if hashtags_match:
            hashtags_text = hashtags_match.group(1)
            tags = [tag.strip() for tag in hashtags_text.split('#') if tag.strip()]
            result['visible_hashtags'] = [f"#{tag}" for tag in tags]

        # Hidden tags
        hidden_match = re.search(r'\*\*Hidden Tags.*?:\*\*\s*(.+?)(?:\n|###)', markdown, re.IGNORECASE | re.DOTALL)
        if hidden_match:
            tags_text = hidden_match.group(1)
            tags = [tag.strip() for tag in tags_text.replace('\n', '').split(',') if tag.strip()]
            result['hidden_tags'] = tags

        return result

    def _parse_music_arc_structure(self, markdown: str) -> Dict:
        """Parse the MUSIC ARC STRUCTURE section."""
        # Extract anchor phrase (optional)
        anchor_match = re.search(r'\*\*⭐ Anchor Phrase:\*\*\s*`(.+?)`', markdown, re.IGNORECASE)
        anchor_phrase = anchor_match.group(1).strip() if anchor_match else ""

        # Find all arc sections - flexible pattern to match various formats
        # Format 1: "### PHASE 1 – Arc Name (Description)"
        # Format 2: "### Phase 1 - Arc Name (3 Prompts)"
        # Format 3: "### 🌅 Phase 1 – Arc Name"
        arc_pattern = r'### (?:🌅|💫|🌤|🌙|⭐)?\s*(?:PHASE|Phase) (\d+) [–—-] (.+?)(?:\((.+?)\))?$'
        arc_matches = list(re.finditer(arc_pattern, markdown, re.IGNORECASE | re.MULTILINE))

        arcs = []

        for i, match in enumerate(arc_matches):
            arc_number = int(match.group(1))
            arc_name = match.group(2).strip()

            # Find section bounds
            start_pos = match.end()
            end_pos = arc_matches[i + 1].start() if i + 1 < len(arc_matches) else len(markdown)
            arc_section = markdown[start_pos:end_pos]

            # Debug: show what section we're parsing
            logger.debug(f"Arc {arc_number} section (first 300 chars):\n{arc_section[:300]}")

            # Parse prompts
            prompts = self._parse_prompts_from_section(arc_section, anchor_phrase)

            arcs.append({
                'arc_number': arc_number,
                'arc_name': arc_name,
                'prompts': prompts
            })

        return {'anchor_phrase': anchor_phrase, 'arcs': arcs}

    def _parse_prompts_from_section(self, section: str, anchor_phrase: str) -> List[Dict]:
        """Parse individual prompts from an arc section."""
        prompts = []

        # Debug logging
        logger.debug(f"Parsing section (first 200 chars): {section[:200]}")
        logger.debug(f"Anchor phrase: '{anchor_phrase}'")

        # Try multiple patterns to support different Notion formats

        # Pattern 1: New format - "X 1. text..." or "✓ 1. text..."
        # Captures everything on the line, then strips quotes later
        pattern1 = r'^\s*[X✓x]\s+(\d+)\.\s*(.+?)$'
        matches1 = list(re.finditer(pattern1, section, re.IGNORECASE | re.MULTILINE))
        logger.debug(f"Pattern1 found {len(matches1)} matches")

        # Pattern 2: Format with checkbox and number - "- [x] 1. text"
        pattern2 = r'^\s*-\s*\[([ xX])\]\s*(\d+)\.\s*(.+?)$'
        matches2 = list(re.finditer(pattern2, section, re.IGNORECASE | re.MULTILINE))
        logger.debug(f"Pattern2 found {len(matches2)} matches")

        # Pattern 3: Old format - "- [x] text anchor_phrase" (no number)
        if anchor_phrase:
            pattern3 = r'-\s*\[([ xX])\]\s*(.+?)' + re.escape(anchor_phrase)
        else:
            pattern3 = r'-\s*\[([ xX])\]\s*(.+?)(?:\n|$)'
        matches3 = list(re.finditer(pattern3, section, re.IGNORECASE | re.MULTILINE))
        logger.debug(f"Pattern3 found {len(matches3)} matches")

        # Use whichever pattern found matches
        if matches1:
            for match in matches1:
                prompt_num = int(match.group(1))
                prompt_text = match.group(2).strip()

                # Strip quotes (both regular and smart quotes)
                prompt_text = prompt_text.strip('""\'"\'')

                # Clean up markdown formatting
                prompt_text = re.sub(r'\*\*', '', prompt_text)
                prompt_text = prompt_text.strip()

                # Extract characteristics
                tempo_hints = self._extract_tempo_hints(prompt_text)
                instrument_hints = self._extract_instrument_hints(prompt_text)
                vibe_hints = self._extract_vibe_hints(prompt_text)

                prompts.append({
                    'prompt_number': prompt_num,
                    'prompt_text': prompt_text,
                    'anchor_phrase': anchor_phrase,
                    'completed': True,  # X or ✓ means completed
                    'tempo_hints': tempo_hints,
                    'instrument_hints': instrument_hints,
                    'vibe_hints': vibe_hints
                })

        elif matches2:
            # Pattern 2: "- [x] 1. text"
            for match in matches2:
                checked = match.group(1).strip().lower() == 'x'
                prompt_num = int(match.group(2))
                prompt_text = match.group(3).strip()

                # Strip quotes
                prompt_text = prompt_text.strip('""\'"\'')

                # Clean up markdown formatting
                prompt_text = re.sub(r'\*\*', '', prompt_text)
                prompt_text = prompt_text.strip()

                # Extract characteristics
                tempo_hints = self._extract_tempo_hints(prompt_text)
                instrument_hints = self._extract_instrument_hints(prompt_text)
                vibe_hints = self._extract_vibe_hints(prompt_text)

                prompts.append({
                    'prompt_number': prompt_num,
                    'prompt_text': prompt_text,
                    'anchor_phrase': anchor_phrase,
                    'completed': checked,
                    'tempo_hints': tempo_hints,
                    'instrument_hints': instrument_hints,
                    'vibe_hints': vibe_hints
                })

        elif matches3:
            # Pattern 3: "- [x] text" (no number)
            prompt_number = 1
            for match in matches3:
                checked = match.group(1).strip().lower() == 'x'
                prompt_text = match.group(2).strip()

                # Strip quotes
                prompt_text = prompt_text.strip('""\'"\'')

                # Clean up markdown formatting
                prompt_text = re.sub(r'\*\*', '', prompt_text)
                prompt_text = prompt_text.strip()

                # Extract characteristics
                tempo_hints = self._extract_tempo_hints(prompt_text)
                instrument_hints = self._extract_instrument_hints(prompt_text)
                vibe_hints = self._extract_vibe_hints(prompt_text)

                prompts.append({
                    'prompt_number': prompt_number,
                    'prompt_text': prompt_text,
                    'anchor_phrase': anchor_phrase,
                    'completed': checked,
                    'tempo_hints': tempo_hints,
                    'instrument_hints': instrument_hints,
                    'vibe_hints': vibe_hints
                })

                prompt_number += 1

        return prompts

    def _extract_tempo_hints(self, text: str) -> List[str]:
        """Extract tempo-related keywords."""
        hints = []
        text_lower = text.lower()

        tempo_map = {
            'very slow': 'very_slow',
            'extremely slow': 'very_slow',
            'slow tempo': 'slow',
            'slow': 'slow',
            'downtempo': 'slow',
            'mid-tempo': 'mid_tempo',
            'mid tempo': 'mid_tempo',
            'moderate': 'mid_tempo',
            'upbeat': 'upbeat',
            'energetic': 'upbeat',
            'fast': 'fast',
            'rapid': 'fast'
        }

        for keyword, category in tempo_map.items():
            if keyword in text_lower:
                if category not in hints:
                    hints.append(category)

        return hints

    def _extract_instrument_hints(self, text: str) -> List[str]:
        """Extract instrument/sound keywords."""
        instruments = [
            'synth', 'synthesizer', 'piano', 'guitar', 'bass',
            'drum machine', 'percussion', 'drums', 'hi-hat', 'hihat',
            'pad', 'arp', 'arpeggiat', 'organ', 'strings',
            'tape', 'vinyl', 'analog', 'analogue', 'digital'
        ]

        hints = []
        text_lower = text.lower()

        for instrument in instruments:
            if instrument in text_lower:
                hints.append(instrument)

        return list(set(hints))

    def _extract_vibe_hints(self, text: str) -> List[str]:
        """Extract vibe/mood keywords."""
        vibes = [
            'ambient', 'atmospheric', 'nostalgic', 'dreamy',
            'focused', 'focus', 'calm', 'relaxing', 'energetic',
            'melancholic', 'uplifting', 'dark', 'bright',
            'hazy', 'clear', 'minimal', 'rhythmic',
            'hypnotic', 'smooth', 'warm', 'cold', 'static'
        ]

        hints = []
        text_lower = text.lower()

        for vibe in vibes:
            if vibe in text_lower:
                hints.append(vibe)

        return hints

    def _extract_description(self, markdown: str) -> Optional[str]:
        """Extract description section."""
        desc_match = re.search(
            r'### 📝 3\. DESCRIPTION.*?\n\n(.+?)(?:\n### |$)',
            markdown,
            re.IGNORECASE | re.DOTALL
        )
        return desc_match.group(1).strip() if desc_match else None

    def _infer_theme(self, title: str, description: Optional[str], hashtags: List[str]) -> str:
        """Infer overall theme from available text."""
        parts = [title]
        if description:
            parts.append(description[:200])
        parts.extend(hashtags)

        combined = " ".join(parts).lower()

        if any(word in combined for word in ['vaporwave', 'vapor', 'aesthetic']):
            if 'lofi' in combined or 'lo-fi' in combined:
                return "Vaporwave/LoFi fusion"
            return "Vaporwave"

        if 'lofi' in combined or 'lo-fi' in combined:
            if 'study' in combined:
                return "LoFi Study"
            if 'chill' in combined or 'relax' in combined:
                return "LoFi Chill"
            if 'rain' in combined:
                return "LoFi Rainy"
            return "LoFi"

        if 'synthwave' in combined or 'retrowave' in combined:
            return "Synthwave/Retrowave"

        return title.split('|')[0].strip()

    def _cache_content(self, page_id: str, content: str):
        """Cache parsed content to file."""
        cache_file = self.cache_dir / f"{page_id}.md"
        cache_file.write_text(content, encoding='utf-8')
        logger.debug(f"Cached content to {cache_file}")


def parse_notion_doc(notion_url: str, api_token: Optional[str] = None) -> NotionTrackMetadata:
    """Convenience function to parse Notion document."""
    parser = NotionParser(api_token)
    return parser.parse_notion_doc(notion_url)
