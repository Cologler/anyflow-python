# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import Callable, Any, List
from abc import ABC, abstractmethod

from .err import Abort
from .ctx import FlowContext

#Next = Callable[[], Any]


class MiddlewareInvoker:
    def __init__(self, factorys: list, ctx: FlowContext):
        super().__init__()
        self._factorys = factorys
        self._ctx = ctx

    def invoke(self) -> Any:
        return self.run_middleware(0)

    def run_middleware(self, idx) -> Any:
        if len(self._factorys) <= idx:
            return None

        factory = self._factorys[idx];
        middleware = factory(self._ctx);
        next = Next(self, idx+1)
        return middleware(self._ctx, next)

    def has_next(self, next_index: int):
        'return whether has the next middleware.'
        return len(self._factorys) > next_index


class Next:
    def __init__(self, invoker: MiddlewareInvoker, next_idx: int):
        super().__init__()
        self._invoker = invoker
        self._next_idx = next_idx
        self._retvals = None

    def __call__(self, or_value=None):
        if not self._invoker.has_next(self._next_idx):
            return or_value

        if self._retvals is None:
            retval = self._invoker.run_middleware(self._next_idx)
            self._retvals = (retval, )

        return self._retvals[0]

    @property
    def is_nop(self):
        return len(self._invoker._factorys) <= self._next_idx


Middleware = Callable[[FlowContext, Next], Any]
MiddlewareFactory = Callable[[FlowContext], Middleware]

class Flow:
    def __init__(self, *, ctx_cls=FlowContext, state: dict=None):
        super().__init__()
        if not issubclass(ctx_cls, FlowContext):
            raise TypeError(f'excepted subclass of FlowContext, got {ctx_cls}')
        self._ctx_cls = ctx_cls
        self._factorys = []
        self.suppress_abort = False
        self._state = dict(state or ()) # make a clone

    def run(self, state: dict=None):
        ctx_state = self._state.copy()
        ctx_state.update(state or ())
        ctx = self._ctx_cls(ctx_state)
        invoker = MiddlewareInvoker(self._factorys.copy(), ctx)
        try:
            return invoker.invoke()
        except Abort:
            if not self.suppress_abort:
                raise

    def use(self, middleware: Middleware=None):
        '''
        *this method can use as decorator.*
        '''
        if middleware is None:
            return lambda m: self.use(m)
        return self.use_factory(lambda _: middleware)

    def use_factory(self, middleware_factory: MiddlewareFactory=None):
        '''
        *this method can use as decorator.*
        '''
        if middleware_factory is None:
            return lambda mf: self.use_factory(mf)
        self._factorys.append(middleware_factory)
