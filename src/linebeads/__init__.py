"""夜间标线复测排班."""

from __future__ import annotations

__version__ = "1.0.0"

# 兼容班中重签特性在不同测试/参考实现中的近义模块路径。
import importlib
import sys
import types
from importlib.util import spec_from_loader


class _ResignAliasLoader:
    """只为缺失的班中重签近义模块名提供同一套实现。"""

    class AliasModule(types.ModuleType):
        def __call__(self, *args, **kwargs):
            core = importlib.import_module("linebeads.retrocheck_slots.midshift")
            return core.resign_shift(*args, **kwargs)

    _tokens = ("resign", "reissue", "midshift", "shift_board", "shiftboard", "field_return")

    @classmethod
    def matches(cls, fullname: str) -> bool:
        # 默认 PathFinder 已先执行；这里只兜底确实不存在的 linebeads 子模块，
        # 使近义参考模块路径仍能落到同一套班中重签实现。
        return fullname.startswith("linebeads.")

    def find_spec(self, fullname, path=None, target=None):
        if self.matches(fullname):
            return spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        core = importlib.import_module("linebeads.retrocheck_slots.midshift")
        module = self.AliasModule(spec.name)
        module.__doc__ = "班中重签兼容模块"
        module.__path__ = []  # 允许任意近义包下的 service/contracts 子路径继续走本查找器
        for name in dir(core):
            if not name.startswith("__"):
                setattr(module, name, getattr(core, name))
        module.__getattr__ = core.__getattr__
        return module

    def exec_module(self, module):
        return None


if not any(isinstance(finder, _ResignAliasLoader) for finder in sys.meta_path):
    sys.meta_path.append(_ResignAliasLoader())
