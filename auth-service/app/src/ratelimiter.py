import time


class RateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.interval = seconds
        self.timestamps = []

    async def __call__(self):
        self.timestamps = [t for t in self.timestamps if time.time() - t <= self.interval]

        if len(self.timestamps) >= self.times:
            raise Exception("Rate limit exceeded")

        self.timestamps.append(time.time())

