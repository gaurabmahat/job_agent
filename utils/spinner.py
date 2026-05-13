import sys
import time
import threading

class Spinner:
    """
    A CLI spinner that runs in a background thread while a
    long-running task executes.
    
    Usage:
        with Spinner("Loading Firefox..."):
            do_long_task()
    
    Or Manually:
        spinner = Spinner("Scraping page...")
        spinner.start()
        do_long_task()
        spinner.stop()
    """

    # Different spinner styles
    STYLES = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "hourglass": ["⏳", "⌛"],
        "clock": ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"],
        "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "bar": ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█", "▉", "▊", "▋", "▌", "▍", "▎"],
        "simple": ["-", "\\", "|", "/"],
    }

    def __init__(
            self,
            message: str = "Working...",
            style: str = "dots",
            speed: float = 0.1,
            done_message: str = "Done"
    ):
        self.message        = message
        self.frames         = self.STYLES.get(style, self.STYLES["dots"])
        self.speed          = speed
        self.done_message   = done_message
        self._running        = False
        self.thread         = None
    
    def _spin(self):
        idx = 0
        while self._running:
            frame = self.frames[idx % len(self.frames)]
            # \r returns to the start of the line so we overwrite it each tick
            sys.stdout.write(f"\r {frame} {self.message}")
            sys.stdout.flush()
            time.sleep(self.speed)
            idx += 1
        
    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self
    
    def stop(self, success: bool = True):
        self._running = False
        if self._thread:
            self._thread.join()
        
        # Calculate message length to clear
        message_length = len(self.message) + len(self.frames[0]) + 4 # message + frame + spcaes  

        icon = "✓" if success else "x"

        # Overwrite the entire message with spaces
        sys.stdout.write(f"\r{' ' * message_length}\r")
        # Write final message
        sys.stdout.write(f"\r {icon} {self.done_message}\n")
        sys.stdout.flush()
    
    # Content manager support - use with `with Spinner(...)`
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc, tb):
        success = exc_type is None # False if an exception occured
        self.stop(success=success)
        return False # Don't suppress exceptions