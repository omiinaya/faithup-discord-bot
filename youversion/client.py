"""API client for YouVersion Verse of the Day."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from .auth import YouVersionAuthenticator

logger = logging.getLogger("red.cogfaithup.youversion")


class YouVersionClient:
    """Client for YouVersion API operations."""
    
    # API Endpoints
    VOTD_URL = "https://nodejs.bible.com/api/moments/votd/3.1"
    BIBLE_CHAPTER_URL = "https://bible.youversionapi.com/3.1/chapter.json"
    
    def __init__(self):
        """Initialize the YouVersion client."""
        self.authenticator = YouVersionAuthenticator()
        self._session = requests.Session()
        self._votd_cache = {}  # day -> (timestamp, data)
        self._cache_ttl = 86400  # 24 hours in seconds
    
    def get_verse_of_the_day(self, day: Optional[int] = None) -> Dict[str, Any]:
        """Get the verse of the day.
        
        Args:
            day: Specific day number (1-365/366). Defaults to current day.
            
        Returns:
            Dictionary containing verse data
            
        Raises:
            ValueError: If API request fails or verse not found
        """
        if day is None:
            day = datetime.now().timetuple().tm_yday
        
        try:
            # VOTD endpoint doesn't require authentication - matches original package
            headers = {
                "Referer": "http://android.youversionapi.com/",
                "X-YouVersion-App-Platform": "android",
                "X-YouVersion-App-Version": "17114",
                "X-YouVersion-Client": "youversion",
            }
            response = self._session.get(
                self.VOTD_URL,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise ValueError(
                    f"VOTD API request failed: {response.status_code}"
                )
            
            data = response.json()
            votd_data = data.get("votd", [])
            
            # Find verse for the requested day - matches original package logic
            for verse in votd_data:
                if verse.get("day") == day:
                    return verse
            
            # Always fallback to first when available - matches original package
            if votd_data:
                logger.warning(
                    f"Verse for day {day} not found, using first available"
                )
                return votd_data[0]
            
            # No data at all - matches original package
            day_value = day
            raise ValueError(f"No verse of the day found for day {day_value}")
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"VOTD API request failed: {e}")
    
    def get_verse_text(self, usfm_reference: str, version_id: int = 1) -> Dict[str, Any]:
        """Get the text for a Bible verse.
        
        Args:
            usfm_reference: USFM reference (e.g., "GEN.1.1")
            version_id: Bible version ID (default: 1 for KJV)
            
        Returns:
            Dictionary containing verse text and metadata
            
        Raises:
            ValueError: If API request fails
        """
        try:
            headers = self.authenticator.get_auth_headers()
            
            # Extract chapter reference from verse reference
            # Convert "JHN.10.11" to "JHN.10"
            parts = usfm_reference.split(".")
            if len(parts) >= 2:
                chapter_reference = f"{parts[0]}.{parts[1]}"
            else:
                chapter_reference = usfm_reference
            
            params = {
                "id": version_id,
                "reference": chapter_reference
            }
            
            response = self._session.get(
                self.BIBLE_CHAPTER_URL,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                # Log the response for debugging
                logger.debug("API Response: %s - %s", response.status_code, response.text)
                raise ValueError(
                    f"Bible chapter API request failed: {response.status_code}"
                )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Bible chapter API request failed: {e}")
    
    def get_formatted_verse_of_the_day(self, day: Optional[int] = None) -> Dict[str, Any]:
        """Get the verse of the day with formatted text.
        
        Args:
            day: Specific day number (1-365/366). Defaults to current day.
            
        Returns:
            Dictionary containing verse data with formatted text
            
        Raises:
            ValueError: If API requests fail
        """
        import time
        if day is None:
            day = datetime.now().timetuple().tm_yday
        
        # Check cache
        cached = self._votd_cache.get(day)
        if cached:
            timestamp, data = cached
            if time.time() - timestamp < self._cache_ttl:
                logger.debug("Returning cached VOTD for day %s", day)
                return data
        
        # Get the verse reference
        votd_data = self.get_verse_of_the_day(day)
        
        # Extract USFM reference
        usfm_refs = votd_data.get("usfm", [])
        if not usfm_refs:
            raise ValueError("No USFM reference found in VOTD data")
        
        # Use the first USFM reference
        usfm_ref = usfm_refs[0]
        
        # Get the verse text
        chapter_data = self.get_verse_text(usfm_ref)
        
        # Extract the specific verse
        verse_number = self._extract_verse_number(usfm_ref)
        verse_text = self._extract_verse_text(chapter_data, verse_number)
        
        result = {
            "day": votd_data.get("day"),
            "usfm": usfm_ref,
            "human_reference": self._usfm_to_human(usfm_ref),
            "verse_text": verse_text,
            "version_id": 1,  # Default to KJV
            "image_id": votd_data.get("image_id")
        }
        
        # Store in cache
        self._votd_cache[day] = (time.time(), result)
        logger.debug("Cached VOTD for day %s", day)
        
        return result
    
    def _extract_verse_number(self, usfm_ref: str) -> int:
        """Extract verse number from USFM reference.
        
        Args:
            usfm_ref: USFM reference (e.g., "GEN.1.1")
            
        Returns:
            Verse number
        """
        parts = usfm_ref.split(".")
        if len(parts) >= 3:
            try:
                return int(parts[2])
            except ValueError:
                pass
        return 1  # Default to first verse
    
    def _extract_verse_text(self, chapter_data: Dict[str, Any], verse_number: int) -> str:
        """Extract specific verse text from chapter data."""
        # The API returns verses embedded in HTML content under response.data
        content = chapter_data.get("response", {}).get("data", {}).get("content", "")
        
        # Parse HTML to find the specific verse
        import re
        
        # Look for the specific verse pattern in the HTML
        # The structure is: <span class="verse v{number}" ...><span class="label">{number}</span><span class="content">text</span>...</span>
        # Use a pattern that captures everything until the next verse starts
        verse_pattern = rf'<span class="verse v{verse_number}"[^>]*>(.*?)(?=<span class="verse v|\Z)'
        match = re.search(verse_pattern, content, re.DOTALL)
        
        if match:
            verse_content = match.group(1).strip()
            
            # Extract all content spans within the verse
            content_pattern = r'<span class="content">(.*?)</span>'
            content_matches = re.findall(content_pattern, verse_content, re.DOTALL)
            
            if content_matches:
                # Combine all content spans
                verse_text = ''.join(content_matches)
                # Clean up any remaining HTML tags and whitespace
                verse_text = re.sub(r'<[^>]+>', '', verse_text)
                verse_text = re.sub(r'\s+', ' ', verse_text).strip()
                
                if verse_text:
                    return verse_text
        
        # Alternative pattern: look for verse content after the label
        alt_pattern = rf'<span class="label">{verse_number}</span>.*?<span class="content">(.*?)</span>'
        alt_match = re.search(alt_pattern, content, re.DOTALL)
        
        if alt_match:
            verse_text = alt_match.group(1).strip()
            verse_text = re.sub(r'<[^>]+>', '', verse_text)
            verse_text = re.sub(r'\s+', ' ', verse_text).strip()
            
            if verse_text:
                return verse_text
        
        # Final fallback: extract all text within the verse span
        fallback_pattern = rf'<span class="verse v{verse_number}"[^>]*>(.*?)</span>'
        fallback_match = re.search(fallback_pattern, content, re.DOTALL)
        
        if fallback_match:
            verse_content = fallback_match.group(1).strip()
            # Remove all HTML tags but keep the text
            verse_text = re.sub(r'<[^>]+>', '', verse_content)
            verse_text = re.sub(r'\s+', ' ', verse_text).strip()
            
            if verse_text:
                return verse_text
        
        # If nothing works, raise an error
        raise ValueError(f"Verse {verse_number} not found in chapter data")
    
    def _usfm_to_human(self, usfm_ref: str) -> str:
        """Convert USFM reference to human-readable format.
        
        Args:
            usfm_ref: USFM reference (e.g., "GEN.1.1")
            
        Returns:
            Human-readable reference (e.g., "Genesis 1:1")
        """
        # Simple mapping for common books
        book_mapping = {
            "GEN": "Genesis", "EXO": "Exodus", "LEV": "Leviticus", 
            "NUM": "Numbers", "DEU": "Deuteronomy", "JOS": "Joshua",
            "JDG": "Judges", "RUT": "Ruth", "1SA": "1 Samuel",
            "2SA": "2 Samuel", "1KI": "1 Kings", "2KI": "2 Kings",
            "1CH": "1 Chronicles", "2CH": "2 Chronicles", "EZR": "Ezra",
            "NEH": "Nehemiah", "EST": "Esther", "JOB": "Job",
            "PSA": "Psalm", "PRO": "Proverbs", "ECC": "Ecclesiastes",
            "SNG": "Song of Solomon", "ISA": "Isaiah", "JER": "Jeremiah",
            "LAM": "Lamentations", "EZK": "Ezekiel", "DAN": "Daniel",
            "HOS": "Hosea", "JOL": "Joel", "AMO": "Amos",
            "OBA": "Obadiah", "JON": "Jonah", "MIC": "Micah",
            "NAM": "Nahum", "HAB": "Habakkuk", "ZEP": "Zephaniah",
            "HAG": "Haggai", "ZEC": "Zechariah", "MAL": "Malachi",
            "MAT": "Matthew", "MRK": "Mark", "LUK": "Luke",
            "JHN": "John", "ACT": "Acts", "ROM": "Romans",
            "1CO": "1 Corinthians", "2CO": "2 Corinthians", "GAL": "Galatians",
            "EPH": "Ephesians", "PHP": "Philippians", "COL": "Colossians",
            "1TH": "1 Thessalonians", "2TH": "2 Thessalonians",
            "1TI": "1 Timothy",
            "2TI": "2 Timothy", "TIT": "Titus", "PHM": "Philemon",
            "HEB": "Hebrews", "JAS": "James", "1PE": "1 Peter",
            "2PE": "2 Peter", "1JN": "1 John", "2JN": "2 John",
            "3JN": "3 John", "JUD": "Jude", "REV": "Revelation"
        }
        
        parts = usfm_ref.split(".")
        if len(parts) >= 3:
            book_abbr = parts[0]
            chapter = parts[1]
            verse = parts[2]
            
            book_name = book_mapping.get(book_abbr, book_abbr)
            return f"{book_name} {chapter}:{verse}"
        
        return usfm_ref  # Return original if parsing fails