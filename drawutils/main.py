#!/usr/bin/env python

import zerorpc


def main():
    client = zerorpc.Client()
    client.connect("tcp://127.0.0.1:4242")
    #lean_canvas(client)
    skills_matrix(client)

def skills_matrix(rpc_client):
    rpc_client.home()
    rpc_client.pen_lift()

    y_min = 0.3
    y_max = 1.0
    y_step = 0.1
    x_min = 0.0
    x_max = 1.0
    x_step = 0.05

    y = y_min
    while y < y_max:
        rpc_client.draw_full({ 'x': 0.0, 'y': y, 'lift': False })
        rpc_client.draw_full({ 'x': 1.0, 'y': y, 'lift': True })
        y += y_step
        rpc_client.draw_full({ 'x': 1.0, 'y': y, 'lift': False })
        rpc_client.draw_full({ 'x': 0.0, 'y': y, 'lift': True })
        y += y_step


    x = x_min
    while x < x_max:
        rpc_client.draw_full({ 'x': x, 'y': y_min, 'lift': False })
        rpc_client.draw_full({ 'x': x, 'y': y_max, 'lift': True })
        x += x_step
        rpc_client.draw_full({ 'x': x, 'y': y_max, 'lift': False })
        rpc_client.draw_full({ 'x': x, 'y': y_min, 'lift': True })
        x += x_step


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
