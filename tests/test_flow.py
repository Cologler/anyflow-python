# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from pytest import raises
from anyflow import Flow, FlowContext, Abort

def test_use():
    flow = Flow()
    a = 1
    def m(ctx, next):
        nonlocal a
        a = 2
        return 10
    flow.use(m)
    assert flow.run() == 10
    assert a == 2

def test_use_as_decorator():
    flow = Flow()
    a = 1
    @flow.use()
    def m(ctx, next):
        nonlocal a
        a = 2
        return 10
    assert flow.run() == 10
    assert a == 2

def test_use_factory():
    flow = Flow()
    a = 1
    def f(ctx):
        def m(ctx, next):
            nonlocal a
            a = 2
            return 10
        return m
    flow.use_factory(f)
    assert flow.run() == 10
    assert a == 2

def test_use_factory_as_decorator():
    flow = Flow()
    a = 1
    @flow.use_factory()
    def f(ctx):
        nonlocal a
        a = 2
        return lambda c, n: 10
    assert flow.run() == 10
    assert a == 2

def test_use_factory_create_behavior():
    flow = Flow()
    a = 1
    @flow.use_factory()
    def f(ctx):
        nonlocal a
        a += 1
        return lambda c, n: 10
    assert flow.run() == 10
    assert a == 2
    assert flow.run() == 10
    assert a == 3

def test_not_raise_when_flow_empty():
    flow = Flow()
    assert flow.run() is None

def test_call_next():
    flow = Flow()
    vals = []
    @flow.use()
    def m1(c, n):
        vals.append(1)
        return n()
    @flow.use()
    def m2(c, n):
        vals.append(2)
    @flow.use()
    def m3(c, n):
        # wont call this
        vals.append(3)
    flow.run()
    assert vals == [1, 2]

def test_call_next_multi_times_should_only_called_once():
    flow = Flow()
    vals = []

    @flow.use()
    def _(c, n):
        vals.append('start')
        n()
        n()
        n()
        vals.append('end')

    @flow.use()
    def _(c, n):
        vals.append('val')

    flow.run()
    assert vals == ['start', 'val', 'end']

def test_call_next_with_default_value():
    flow = Flow()

    @flow.use()
    def _(c, n):
        return n()

    @flow.use()
    def _(c, n):
        return n(1)

    assert flow.run() == 1

def test_call_next_multi_times_with_default_value_1():
    flow = Flow()

    @flow.use()
    def _(c, n):
        return n()

    @flow.use()
    def _(c, n):
        n(0)
        n(1)
        return n(2)

    assert flow.run() == 0

def test_call_next_multi_times_with_default_value_2():
    flow = Flow()

    @flow.use()
    def _(c, n):
        return n()

    @flow.use()
    def _(c, n):
        n()
        n(1)
        return n(2)

    assert flow.run() is None

def test_raise_errors():
    flow = Flow()
    @flow.use()
    def m1(c, n):
        raise ValueError('123')
    with raises(ValueError):
        flow.run()

def test_create_flow_with_state():
    flow = Flow(state={'a': 1})
    @flow.use()
    def m1(c: FlowContext, n):
        assert c.state['a'] == 1
    flow.run()

def test_run_with_state():
    flow = Flow()
    @flow.use()
    def m1(c: FlowContext, n):
        assert c.state['a'] == 1
    flow.run({
        'a': 1
    })

def test_run_with_state_override_default_state():
    flow = Flow(state={'a': 1})
    @flow.use()
    def m1(c: FlowContext, n):
        assert c.state['a'] == 2
    flow.run({
        'a': 2
    })

def test_use_state():
    flow = Flow()
    @flow.use()
    def m1(c: FlowContext, n):
        c.state['a'] = 1
        return n()
    @flow.use()
    def m2(c: FlowContext, n):
        return c.state['a']
    assert flow.run() == 1

def test_next_props():
    flow = Flow()
    @flow.use()
    def m1(c, n):
        assert not n.is_nop
        return n()
    @flow.use()
    def m2(c, n):
        assert n.is_nop
    flow.run()

def test_async_middlewares():
    import asyncio
    flow = Flow()
    @flow.use()
    def _(c, n): # without async keyword
        return n()
    @flow.use()
    async def _(c, n): # with async keyword
        return await n()
    @flow.use()
    async def _(c, n): # with return value
        await asyncio.sleep(0.001)
        return 2
    assert asyncio.run(flow.run()) == 2

def test_abort():
    flow = Flow()
    @flow.use()
    def _(c, n):
        c.abort(None)
        return 2
    with raises(Abort):
        flow.run()

def test_abort_suppressed():
    flow = Flow()
    flow.suppress_abort = True
    @flow.use()
    def _(c, n):
        c.abort(None)
        return 2
    assert flow.run() is None
