#!/usr/bin/env python3

from datetime import datetime, timezone

class Log:
    def __init__(self, filename: str, is_error: bool) -> None:
        self.file = open(filename, 'a')
        self.leading_newline = True
        if is_error:
            self.prefix = " [ERROR] "
        else:
            self.prefix = " [INFO] "
 
    def write(self, message: str) -> None:
        if self.leading_newline:
            timestamp = datetime.now(timezone.utc).astimezone().isoformat()
            message = timestamp + self.prefix + message
        self.file.write(message)
        self.leading_newline = (message[-1] == "\n")
        
    def flush(self) -> None:
        self.file.flush()

    def __del__(self) -> None:
        self.file.close()
