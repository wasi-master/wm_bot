import inspect
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Type, TypeVar
from types import FrameType


__all__ = ("Frame", "Report")
T = TypeVar("T", bound="Report")

@dataclass
class Frame:
    """A dataclass for traceback frames

    https://docs.python.org/3/reference/datamodel.html#frame-objects
    """
    file: str
    line: int
    locals: Dict[str, Any]
    code: List[str]


class Report:
    """A class for reporting tracebacks"""
    def __init__(self, timestamp: int, exception: Exception, traceback: List[str]):
        self.timestamp = timestamp
        self.exception = exception
        self.traceback = traceback

    @staticmethod
    def __collect_frame(frame: FrameType, line: int=None) -> Frame:
        try:
            code = inspect.getsourcelines(frame)
        except OSError:
            code = ["Used in Exec or Eval therefore no code"]
        return Frame(
            file=inspect.getfile(frame),
            line=line or frame.f_lineno,
            locals=frame.f_locals,
            code=code,
        )

    @classmethod
    def from_exception(cls: Type[T], exception: Exception) -> T:
        """Generates a report from the given exception

        Parameters
        ----------
        exception : Exception
            The exception to generate a report for

        Returns
        -------
        Report
            The report for the given exception
        """
        tracebacks = []

        if hasattr(exception, "__traceback__"):
            traceback = exception.__traceback__
        else:
            traceback = sys.exc_info()[1]

        while traceback:
            frame = traceback.tb_frame
            line = traceback.tb_lineno
            tracebacks.append(cls.__collect_frame(frame, line=line))
            traceback = traceback.tb_next

        return cls(
            timestamp=time.time(),
            exception=exception,
            traceback=tracebacks,
        )
