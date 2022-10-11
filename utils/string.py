class StringUtils:
    """String utilities."""

    @staticmethod
    def get_last_dot_chunk(string: str) -> str:
        """Return the last chunk of an input string in dot notation, or the entire string if no dot is found in the
        input string.
        """
        return string.split('.')[-1]
