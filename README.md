# anyflow

a simplest common middleware framework for python.

## HOW-TO-USE

``` py
from anyflow import Flow

flow = Flow()

@flow.use()
def middleware_1(ctx, next):
    ctx.state['value'] = 1
    # call the next middleware (middleware_2):
    return next()

@flow.use()
def middleware_2(ctx, next):
    print(ctx.state['value'])
    # next middleware does not exists, call nothing:
    return next()

flow.run()
```
