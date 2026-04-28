"""Stub Celery package for testing.

Provides a minimal Celery class and a dummy logger.
"""

class Conf:
    def __init__(self):
        pass
    def update(self, **kwargs):
        self.__dict__.update(kwargs)

class Celery:
    def __init__(self, *args, **kwargs):
        self.conf = Conf()
        self.tasks = {}

    def task(self, *args, **kwargs):
        # Support name argument for task registration
        task_name = kwargs.get('name')
        def decorator(func):
            name = task_name if task_name else func.__name__
            self.tasks[name] = func
            return func
        return decorator


# utils submodule
class _Log:
    @staticmethod
    def get_task_logger(name: str):
        class DummyLogger:
            def info(self, *args, **kwargs):
                pass
            def warning(self, *args, **kwargs):
                pass
            def error(self, *args, **kwargs):
                pass
        return DummyLogger()

# expose utils.log
class utils:
    log = _Log()
