from typing import TYPE_CHECKING, Iterable, Optional

from eth_utils import to_checksum_address

from evm_trace.enums import CallType

if TYPE_CHECKING:
    from evm_trace.base import CallTreeNode


class DisplayableCallTreeNode(object):
    _FILE_MIDDLE_PREFIX = "├──"
    _FILE_LAST_PREFIX = "└──"
    _PARENT_PREFIX_MIDDLE = "    "
    _PARENT_PREFIX_LAST = "│   "

    def __init__(
        self,
        call: "CallTreeNode",
        parent: Optional["DisplayableCallTreeNode"] = None,
        is_last: bool = False,
    ):
        self.call = call
        self.parent = parent
        self.is_last = is_last

    @property
    def depth(self) -> int:
        return self.call.depth

    @property
    def title(self) -> str:
        call_type = self.call.call_type.value.upper()
        call_mnemonic = "CALL" if self.call.call_type == CallType.MUTABLE else f"{call_type}CALL"
        address = to_checksum_address(self.call.address.hex())
        cost = self.call.gas_cost

        call_path = str(address)
        if self.call.calldata:
            call_path = f"{call_path}.<{self.call.calldata[:4].hex()}>"

        return f"{call_mnemonic}: {call_path} [{cost} gas]"

    @classmethod
    def make_tree(
        cls,
        root: "CallTreeNode",
        parent: Optional["DisplayableCallTreeNode"] = None,
        is_last: bool = False,
    ) -> Iterable["DisplayableCallTreeNode"]:
        displayable_root = cls(root, parent=parent, is_last=is_last)
        yield displayable_root

        count = 1
        for child_node in root.calls:
            is_last = count == len(root.calls)
            if child_node.calls:
                yield from cls.make_tree(child_node, parent=displayable_root, is_last=is_last)
            else:
                yield cls(child_node, parent=displayable_root, is_last=is_last)

            count += 1

    def __str__(self) -> str:
        if self.parent is None:
            return self.title

        _filename_prefix = self._FILE_LAST_PREFIX if self.is_last else self._FILE_MIDDLE_PREFIX

        parts = [f"{_filename_prefix} {self.title}"]
        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self._PARENT_PREFIX_MIDDLE if parent.is_last else self._PARENT_PREFIX_LAST)
            parent = parent.parent

        return "".join(reversed(parts))
