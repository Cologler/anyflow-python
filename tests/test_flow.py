# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from pytest import raises
from anyflow import Flow, FlowContext

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

def test_call_next_only_once():
    flow = Flow()
    vals = []

    @flow.use()
    def m1(c, n):
        vals.append('start')
        n()
        n()
        n()
        vals.append('end')

    @flow.use()
    def m2(c, n):
        vals.append('val')

    flow.run()
    assert vals == ['start', 'val', 'end']

def test_raise_errors():
    flow = Flow()
    @flow.use()
    def m1(c, n):
        raise ValueError('123')
    with raises(ValueError):
        flow.run()

def test_run_with_state():
    flow = Flow()
    @flow.use()
    def m1(c: FlowContext, n):
        assert c.state['a'] == 1
    flow.run({
        'a': 1
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
    async def m1(c, n):
        assert not n.is_nop
        return await n()
    @flow.use()
    async def m2(c, n):
        await asyncio.sleep(1)
        return 2
    assert asyncio.run(flow.run()) == 2
