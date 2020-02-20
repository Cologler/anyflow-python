# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

class FlowContext:
    def __init__(self, state: dict=None):
        super().__init__()
        self._state = {}
        if state is not None:
            self._state.update(state)

    @property
    def state(self):
        return self._state
