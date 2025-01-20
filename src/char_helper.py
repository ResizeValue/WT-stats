class CharHelper:
    @staticmethod
    # If unicode number is 0-31 or 127, then it is a control unicode.
    # Because pynput only registers/only fails to convert the alphabet, this will not return True for the other six control codes.
    def is_ctrl_unicode(code: str) -> bool:
        """Check if the unicode is a control character."""
        if not code or len(code) != 1:  # Ensure code is not None and has length 1
            return False
        return 0 < ord(code) < 26

    @staticmethod
    # param: char
    def get_unicode_order_from_char(char: str) -> int:
        if char is None or type(char) is not str:
            return -1

        if not char:
            return -1

        if len(char) != 1:
            return -1

        return ord(char)

    @staticmethod
    # Returns the character from control + character unicode.
    # Example: ctrl + A -> (pynput) -> \u0001 -> (This method) -> a
    # There are 32 ctrl combinations, but pynput does not r1egister/struggle the non-alphabetic codes, so they will not be considered.
    def character_from_ctrl_unicode(order: int) -> str:
        if not 0 < order < 26:
            return
        pool = "abcdefghijklmnopqrstuvwxyz"
        assert len(pool) == 26
        return pool[order - 1]