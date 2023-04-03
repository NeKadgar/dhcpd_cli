import re
from typing import Tuple, Iterable


class ConfParser:
    HOST_PATTERN = r"host\s\w+\s{"
    ETHERNET_PATTERN = r"ethernet\s[\w:]+;"
    FILENAME_PATTERN = r"filename\s\"[^\;]+"
    FIXED_ADDR_PATTERN = r"fixed-address\s[^;]+"
    DENY_BOOTING_PATTERN = r"deny\sbooting"

    @staticmethod
    def _is_all_brackets_closed(lines) -> bool:
        if len(lines) < 2:
            return False
        return lines.count("{") == lines.count("}")

    @classmethod
    def get_host_matches(cls, lines: str) -> Iterable[re.Match]:
        return re.finditer(cls.HOST_PATTERN, lines)

    @staticmethod
    def get_host_match(host_name: str, lines: str) -> re.Match:
        return re.search(f"host\s{host_name}\s{{", lines)

    @classmethod
    def get_host_boundaries(cls, host: re.Match, lines: str) -> Tuple[int, int]:
        start_brackets_pointer = host.end() - 1
        _pointer = start_brackets_pointer
        while True:
            end_brackets_pointer = lines.find("}", _pointer) + 1

            if end_brackets_pointer == -1 \
                    or cls._is_all_brackets_closed(lines[start_brackets_pointer:end_brackets_pointer]):
                break
            _pointer = end_brackets_pointer
        return start_brackets_pointer, end_brackets_pointer

    @classmethod
    def get_ethernet(cls, host_lines: str) -> str:
        return (
            re.search(cls.ETHERNET_PATTERN, host_lines)
            .group()
            .replace("ethernet", "", 1)
            .replace(";", "")
            .replace(" ", "")
        )

    @staticmethod
    def get_name(host: re.Match) -> str:
        return (
            "".join(
                host.group()
                .replace("host", "", 1)
                .rsplit("{", 1)
            )
            .replace(" ", "")
        )

    @classmethod
    def is_deny_booting(cls, host_lines: str) -> bool:
        return re.search(cls.DENY_BOOTING_PATTERN, host_lines) is not None

    @classmethod
    def get_filenames(cls, host_lines: str):
        re_filenames = re.finditer(cls.FILENAME_PATTERN, host_lines)
        condition_true_filename, condition_false_filename = [(
            re_filename.group()
            .replace("filename", "", 1)
            .replace("\"", "", 2)
            .replace(" ", "")
        ) for re_filename in re_filenames]
        return condition_true_filename, condition_false_filename

    @classmethod
    def get_fixed_addr(cls, host_lines: str):
        return (
            re.search(cls.FIXED_ADDR_PATTERN, host_lines)
            .group()
            .replace("fixed-address", "", 1)
            .replace(" ", "")
        )
