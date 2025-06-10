from typing import Any, List, Tuple


class FilterBuilder:
    @staticmethod
    def _auto_type(val: str) -> Any:
        try:
            if '.' in val:
                return float(val)
            else:
                return int(val)
        except (ValueError, TypeError):
            return val

    @classmethod
    def build(cls, args) -> List[Tuple[str, str, Any]]:
        filters: List[Tuple[str, str, Any]] = []
        for key, value in args.items():
            if key in {"limit", "offset", "order_by", "fields"}:
                continue
            elif key.endswith("_gte"):
                filters.append((key[:-4], ">=", cls._auto_type(value)))
            elif key.endswith("_lte"):
                filters.append((key[:-4], "<=", cls._auto_type(value)))
            elif key.endswith("_gt"):
                filters.append((key[:-3], ">", cls._auto_type(value)))
            elif key.endswith("_lt"):
                filters.append((key[:-3], "<", cls._auto_type(value)))
            elif key.endswith("_in"):
                filters.append((key[:-3], "in", [cls._auto_type(x) for x in value.split(',')]))
            else:
                filters.append((key, "==", cls._auto_type(value)))
        return filters
