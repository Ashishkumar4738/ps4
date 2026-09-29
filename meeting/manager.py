import os
import json
import threading
from datetime import datetime

from config import MEETING_FILE, MEETING_DIR


class MeetingManager:

    def __init__(self):
        os.makedirs(MEETING_DIR, exist_ok=True)

        meeting_start = datetime.now()

        self.meeting_data = {
            "meeting_id": meeting_start.strftime("%Y%m%d_%H%M%S"),
            "started_at": meeting_start.isoformat(),
            "segments": []
        }

        self.lock = threading.Lock()

        self.save()

    def add_segment(self, segment):
        with self.lock:
            self.meeting_data["segments"].append(segment)

            self.meeting_data["segments"].sort(
                key=lambda x: x["segment_id"]
            )

        self.save()

    def save(self):
        with self.lock:
            with open(
                MEETING_FILE,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    self.meeting_data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

    def finish(self):
        with self.lock:
            self.meeting_data["ended_at"] = (
                datetime.now().isoformat()
            )

        self.save()

    def get_segment_count(self):
        with self.lock:
            return len(self.meeting_data["segments"])

    @property
    def file_path(self):
        return MEETING_FILE