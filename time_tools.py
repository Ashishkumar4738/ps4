
from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_datetime(location: str = "India") -> str:
    """
    Get the current date and time for a supported location.
    """

    timezones = {
        "india": "Asia/Kolkata",
        "uk": "Europe/London",
        "london": "Europe/London",
        "usa": "America/New_York",
        "new york": "America/New_York",
        "utc": "UTC",
    }

    key = location.strip().lower()
    timezone_name = timezones.get(key)

    if timezone_name is None:
        return (
            f"Unsupported location: {location}. "
            f"Supported locations: India, UK, London, USA, "
            f"New York, UTC."
        )

    now = datetime.now(ZoneInfo(timezone_name))

    return (
        f"Location: {location}\n"
        f"Date: {now.strftime('%A, %d %B %Y')}\n"
        f"Time: {now.strftime('%I:%M:%S %p')}\n"
        f"Timezone: {now.tzname()}\n"
        f"UTC offset: {now.strftime('%z')}"
    )