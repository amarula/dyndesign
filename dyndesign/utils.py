import inspect
from typing import Any, Optional

DEFAULT_BACK_LEVEL = 2


def back_frame(back_level: Optional[int] = None) -> Any:
    """Retrieve the frame that is N frames back from the current frame.

    :param back_level: number N of frames back to inspect.
    :return: frame retrieved.
    """
    current_frame = inspect.currentframe()
    for _ in range(back_level or DEFAULT_BACK_LEVEL):
        current_frame = current_frame.f_back # type: ignore
    return current_frame
