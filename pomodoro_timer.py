from datetime import datetime, timedelta
from plyer import notification
import time
import threading

class PomodoroTimer:
    def __init__(self, work_minutes=25, break_minutes=5, long_break_minutes=15):
        self.work_duration = work_minutes * 60
        self.break_duration = break_minutes * 60
        self.long_break_duration = long_break_minutes * 60
        self.session_count = 0
        self.total_focus_time = 0
        self.daily_goal = 4  # Number of pomodoros to complete
        
        self.remaining_time = self.work_duration
        self.is_break = False
        self.is_running = False
        self.timer_thread = None
        self.callback = None

    def start(self, update_callback):
        self.callback = update_callback
        self.is_running = True
        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def pause(self):
        self.is_running = False

    def reset(self):
        self.is_running = False
        self.remaining_time = self.work_duration
        self.is_break = False
        if self.callback:
            self.callback(self.remaining_time, self.is_break)

    def _run_timer(self):
        while self.is_running and self.remaining_time > 0:
            time.sleep(1)
            self.remaining_time -= 1
            if not self.is_break:
                self.total_focus_time += 1
            if self.callback:
                self.callback(self.remaining_time, self.is_break)

        if self.is_running:
            self._send_notification()
            if not self.is_break:
                self.session_count += 1
                
            self.is_break = not self.is_break
            if self.is_break and self.session_count % 4 == 0:
                self.remaining_time = self.long_break_duration  # Long break after 4 sessions
            else:
                self.remaining_time = self.break_duration if self.is_break else self.work_duration
            self._run_timer()

    def _send_notification(self):
        message = "Time for a break!" if not self.is_break else "Break's over! Back to work!"
        notification.notify(
            title="Pomodoro Timer",
            message=message,
            timeout=10
        ) 