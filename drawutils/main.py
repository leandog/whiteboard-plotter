#!/usr/bin/env python

import zerorpc


def main():
    client = zerorpc.Client()
    client.connect("tcp://127.0.0.1:4242")
    lean_canvas(client)

def lean_canvas(rpc_client):
    rpc_client.home()
    rpc_client.pen_lift()

    # outline
    rpc_client.draw({ 'x': 0.0, 'y': 0.0, 'lift': False })
    rpc_client.draw({ 'x': 1.0, 'y': 0.0, 'lift': False })
    rpc_client.draw({ 'x': 1.0, 'y': 1.0, 'lift': False })
    rpc_client.draw({ 'x': 0.0, 'y': 1.0, 'lift': False })
    rpc_client.draw({ 'x': 0.0, 'y': 0.0, 'lift': False })

    rpc_client.pen_lift()

    rpc_client.draw({ 'x': 0.2, 'y': 0.0, 'lift': False })
    rpc_client.draw({ 'x': 0.2, 'y': 0.66, 'lift': False })
    rpc_client.pen_lift()

    rpc_client.draw({ 'x': 0.4, 'y': 0.0, 'lift': False })
    rpc_client.draw({ 'x': 0.4, 'y': 0.66, 'lift': False })
    rpc_client.pen_lift()

    rpc_client.draw({ 'x': 0.2, 'y': 0.33, 'lift': False })
    rpc_client.draw({ 'x': 0.4, 'y': 0.33, 'lift': False })
    rpc_client.pen_lift()

    rpc_client.draw({ 'x': 0.6, 'y': 0.0, 'lift': False })
    rpc_client.draw({ 'x': 0.6, 'y': 0.66, 'lift': False })
    rpc_client.pen_lift()

    rpc_client.draw({ 'x': 0.6, 'y': 0.33, 'lift': False })
    rpc_client.draw({ 'x': 0.8, 'y': 0.33, 'lift': False })
    rpc_client.pen_lift()

    rpc_client.draw({ 'x': 0.8, 'y': 0.0, 'lift': False })
    rpc_client.draw({ 'x': 0.8, 'y': 0.66, 'lift': False })
    rpc_client.pen_lift()

    rpc_client.draw({ 'x': 0.5, 'y': 0.66, 'lift': False })
    rpc_client.draw({ 'x': 0.5, 'y': 1.0, 'lift': False })
    rpc_client.pen_lift()

    rpc_client.draw({ 'x': 0.0, 'y': 0.66, 'lift': False })
    rpc_client.draw({ 'x': 1.0, 'y': 0.66, 'lift': False })
    rpc_client.pen_lift()

    rpc_client.home()

main()
