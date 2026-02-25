"""Parse and convert upload schedules from Notion to ISO 8601 format."""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

logger = logging.getLogger(__name__)


class ScheduleParser:
    """Parse schedule strings from Notion into ISO 8601 timestamps."""

    # Day name mappings
    DAYS = {
        'monday': MO, 'mon': MO,
        'tuesday': TU, 'tue': TU, 'tues': TU,
        'wednesday': WE, 'wed': WE,
        'thursday': TH, 'thu': TH, 'thur': TH, 'thurs': TH,
        'friday': FR, 'fri': FR,
        'saturday': SA, 'sat': SA,
        'sunday': SU, 'sun': SU,
    }

    # Common timezone mappings
    TIMEZONE_MAP = {
        'ET': 'America/New_York',
        'EST': 'America/New_York',
        'EDT': 'America/New_York',
        'CT': 'America/Chicago',
        'CST': 'America/Chicago',
        'CDT': 'America/Chicago',
        'MT': 'America/Denver',
        'MST': 'America/Denver',
        'MDT': 'America/Denver',
        'PT': 'America/Los_Angeles',
        'PST': 'America/Los_Angeles',
        'PDT': 'America/Los_Angeles',
        'UTC': 'UTC',
        'GMT': 'UTC',
    }

    def __init__(self, default_timezone: str = 'America/New_York'):
        """
        Initialize schedule parser.

        Args:
            default_timezone: Default timezone (IANA format)
        """
        self.default_timezone = ZoneInfo(default_timezone)

    def parse_schedule(self, schedule_string: str) -> Optional[str]:
        """
        Parse schedule string and return ISO 8601 timestamp.

        Supported formats:
        - "Wednesday @ 10 AM ET"
        - "Friday at 2:30 PM PT"
        - "2026-01-25 10:00"
        - "next Tuesday @ 9 AM"
        - "Jan 25 @ 10 AM ET"

        Args:
            schedule_string: Schedule string from Notion

        Returns:
            ISO 8601 timestamp string or None if parsing fails
        """
        if not schedule_string:
            return None

        schedule_string = schedule_string.strip()
        logger.debug(f"Parsing schedule: {schedule_string}")

        # Try to parse as ISO date first
        try:
            dt = dateutil_parser.parse(schedule_string)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=self.default_timezone)
            return dt.isoformat()
        except (ValueError, TypeError):
            pass

        # Parse day + time format (e.g., "Wednesday @ 10 AM ET")
        result = self._parse_day_time_format(schedule_string)
        if result:
            return result

        # Try generic date parsing
        try:
            dt = dateutil_parser.parse(schedule_string, fuzzy=True)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=self.default_timezone)

            # If date is in the past, move to next occurrence
            now = datetime.now(self.default_timezone)
            if dt < now:
                logger.warning(f"Parsed date {dt} is in the past")
                return None

            return dt.isoformat()

        except (ValueError, TypeError) as e:
            logger.error(f"Failed to parse schedule '{schedule_string}': {e}")
            return None

    def _parse_day_time_format(self, schedule_string: str) -> Optional[str]:
        """
        Parse "Day @ Time TZ" format.

        Args:
            schedule_string: e.g., "Wednesday @ 10 AM ET"

        Returns:
            ISO 8601 timestamp or None
        """
        # Pattern: Day (@ or "at") Time (AM/PM) (timezone)
        pattern = r'(?:next\s+)?(\w+)\s*(?:@|at)\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?\s*(\w+)?'
        match = re.match(pattern, schedule_string, re.IGNORECASE)

        if not match:
            return None

        day_str, hour_str, minute_str, ampm, tz_str = match.groups()

        # Parse day
        day_lower = day_str.lower()
        if day_lower not in self.DAYS:
            logger.debug(f"Unknown day: {day_str}")
            return None

        day_weekday = self.DAYS[day_lower]

        # Parse time
        hour = int(hour_str)
        minute = int(minute_str) if minute_str else 0

        # Handle AM/PM
        if ampm:
            if ampm.upper() == 'PM' and hour != 12:
                hour += 12
            elif ampm.upper() == 'AM' and hour == 12:
                hour = 0

        # Parse timezone
        tz = self.default_timezone
        if tz_str:
            tz_str_upper = tz_str.upper()
            if tz_str_upper in self.TIMEZONE_MAP:
                tz = ZoneInfo(self.TIMEZONE_MAP[tz_str_upper])
            else:
                try:
                    tz = ZoneInfo(tz_str)
                except Exception:
                    logger.warning(f"Unknown timezone: {tz_str}, using default")

        # Calculate next occurrence of this day
        now = datetime.now(tz)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Use relativedelta to find next occurrence
        target = target + relativedelta(weekday=day_weekday(+1))

        # If today is the target day but time has passed, go to next week
        if target <= now:
            target = target + relativedelta(weeks=1)

        return target.isoformat()

    def parse_schedule_from_notion(self, notion_metadata: dict) -> Optional[str]:
        """
        Extract and parse schedule from Notion metadata.

        Args:
            notion_metadata: Parsed Notion document metadata

        Returns:
            ISO 8601 timestamp or None
        """
        # Try different field names that might contain schedule
        schedule_fields = [
            'upload_schedule',
            'scheduled_date',
            'publish_date',
            'release_date',
        ]

        for field in schedule_fields:
            value = notion_metadata.get(field)
            if value:
                result = self.parse_schedule(value)
                if result:
                    return result

        return None

    def validate_schedule(self, iso_timestamp: str) -> tuple[bool, Optional[str]]:
        """
        Validate that schedule is in the future.

        Args:
            iso_timestamp: ISO 8601 timestamp string

        Returns:
            (is_valid, error_message)
        """
        try:
            dt = datetime.fromisoformat(iso_timestamp)
            now = datetime.now(dt.tzinfo or self.default_timezone)

            if dt <= now:
                return False, f"Schedule is in the past: {dt}"

            # YouTube requires at least 1 hour in the future for scheduling
            min_future = now + timedelta(hours=1)
            if dt < min_future:
                return False, f"Schedule must be at least 1 hour in the future"

            return True, None

        except (ValueError, TypeError) as e:
            return False, f"Invalid timestamp format: {e}"

    def format_for_display(self, iso_timestamp: str, timezone: str = None) -> str:
        """
        Format timestamp for human-readable display.

        Args:
            iso_timestamp: ISO 8601 timestamp
            timezone: Display timezone (uses default if None)

        Returns:
            Formatted string like "Wednesday, Jan 25 at 10:00 AM ET"
        """
        try:
            dt = datetime.fromisoformat(iso_timestamp)

            if timezone:
                tz = ZoneInfo(self.TIMEZONE_MAP.get(timezone.upper(), timezone))
                dt = dt.astimezone(tz)
            elif dt.tzinfo is None:
                dt = dt.replace(tzinfo=self.default_timezone)

            # Get timezone abbreviation
            tz_abbr = "ET"  # Default
            for abbr, iana in self.TIMEZONE_MAP.items():
                if str(dt.tzinfo) == iana or (hasattr(dt.tzinfo, 'key') and dt.tzinfo.key == iana):
                    tz_abbr = abbr
                    break

            return dt.strftime(f"%A, %b %d at %I:%M %p") + f" {tz_abbr}"

        except Exception as e:
            logger.error(f"Failed to format timestamp: {e}")
            return iso_timestamp
