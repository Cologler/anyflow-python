# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import Callable, Any, List
from abc import ABC, abstractmethod

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

        next = Next(self, idx+1)
        factory = self._factorys[idx];
        middleware = factory(self._ctx);
        return middleware(self._ctx, next);


class Next:
    def __init__(self, invoker: MiddlewareInvoker, next_idx: int):
        super().__init__()
        self._invoker = invoker
        self._next_idx = next_idx
        self._retvals = None

    def __call__(self):
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
    def __init__(self):
        super().__init__()
        self._factorys = []

    def run(self, state: dict=None):
        ctx = FlowContext(state)
        return MiddlewareInvoker(self._factorys.copy(), ctx).invoke()

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

    def add_action(self, action: Callable[[FlowContext], Any]=None):
        '''
        add the action as a middleware, and auto call `next()` after the action executed.

        *this method can use as decorator.*
        '''
        def middleware(ctx, next):
            retval = action(ctx)
            if next.is_nop:
                return retval
            return next()
        return self.use(middleware)
