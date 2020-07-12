# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from .err import Abort

class FlowContext:
    def __init__(self, state: dict=None):
        super().__init__()
        self._state = dict(state or ()) # make a clone

    @property
    def state(self) -> dict:
        'get the state dict.'
        return self._state

    def abort(self, reason):
        'abort the flow by raise a `Abort`.'
        raise Abort(reason=reason)
