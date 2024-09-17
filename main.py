#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import functools
from weight_strategies import ResourcePool, ScheduleWeightStrategy, LimitWeightStrategy
from matplotlib.widgets import Button, Slider, CheckButtons, RadioButtons


resource_pools = [
    ResourcePool(100, 100, 1, True),
    ResourcePool(100, 500, 100, True),
    ResourcePool(50, 500, 1, False),
    ResourcePool(50, 500, 1, False),
    ResourcePool(50, 500, 1, False)
]

schedule_weight_strategy = ScheduleWeightStrategy(resource_pools)

limit_weight_strategy = LimitWeightStrategy(resource_pools)
limit_weight_strategy.recalculate()

active = 0
# drawing logic
schedule_weight_charts = schedule_weight_strategy.get_charts(active)
limit_weight_charts = limit_weight_strategy.get_charts(active)
fig, ax = plt.subplots(len(schedule_weight_charts) + len(limit_weight_charts))


def draw(schedule_weight_charts, limit_weight_charts):
    for i in range(len(schedule_weight_charts) + len(limit_weight_charts)):
        ax[i].cla()
    for idx, chart in enumerate(schedule_weight_charts):
        ax[idx].set_title(chart.title)
        ax[idx].set(xlabel=chart.xlabel, ylabel=chart.ylabel)
        ax[idx].set_ylim([0, 110])
        for line in chart.lines:
            ax[idx].plot(np.array(line.x), np.array(line.y), line.line_type,
                         lw=2, color=line.color, label=line.label)

    for idx, chart in enumerate(limit_weight_charts):
        idx += len(schedule_weight_charts)
        ax[idx].set_title(chart.title)
        ax[idx].set(xlabel=chart.xlabel, ylabel=chart.ylabel)
        ax[idx].set_ylim([0, 110])
        for line in chart.lines:
            ax[idx].plot(np.array(line.x), np.array(line.y), line.line_type,
                         lw=2, color=line.color, label=line.label)


draw(schedule_weight_charts, limit_weight_charts)


def update_cpu_limit(idx, val):
    resource_pools[idx].cpu_limit = val
    schedule_weight_charts = schedule_weight_strategy.get_charts(active)
    limit_weight_charts = limit_weight_strategy.get_charts(active)
    draw(schedule_weight_charts, limit_weight_charts)
    fig.canvas.draw_idle()


def update_desired_cpu_usage(idx, val):
    resource_pools[idx].desired_cpu_usage = val
    schedule_weight_charts = schedule_weight_strategy.get_charts(active)
    limit_weight_charts = limit_weight_strategy.get_charts(active)
    draw(schedule_weight_charts, limit_weight_charts)
    fig.canvas.draw_idle()


def update_cpu_weight(idx, val):
    resource_pools[idx].weight = val
    schedule_weight_charts = schedule_weight_strategy.get_charts(active)
    limit_weight_charts = limit_weight_strategy.get_charts(active)
    draw(schedule_weight_charts, limit_weight_charts)
    fig.canvas.draw_idle()


def update_enabled(idx, checkbox, val):
    updated_states = checkbox.get_status()
    resource_pools[idx].enabled = updated_states[0]
    schedule_weight_charts = schedule_weight_strategy.get_charts(active)
    limit_weight_charts = limit_weight_strategy.get_charts(active)
    draw(schedule_weight_charts, limit_weight_charts)
    fig.canvas.draw_idle()


def update_active_chart(val):
    global active
    active = int(val)
    schedule_weight_charts = schedule_weight_strategy.get_charts(active)
    limit_weight_charts = limit_weight_strategy.get_charts(active)
    draw(schedule_weight_charts, limit_weight_charts)
    fig.canvas.draw_idle()


items = []
for i, pool in enumerate(resource_pools):
    axamp = fig.add_axes([0.1, 0.9 - 0.15 * i, 0.12, 0.01])
    fig.text(0.12, 0.9 - 0.15 * i + 0.02, 'Resource Pool # ' + str(i),
             verticalalignment='bottom', horizontalalignment='right',
             color='black', fontsize=15)
    cpu_limit_slider = Slider(
        ax=axamp,
        label="CPU limit ",
        valmin=0,
        valmax=100,
        valinit=pool.cpu_limit,
        orientation="horizontal"
    )
    cpu_limit_slider.on_changed(functools.partial(update_cpu_limit, i))

    axamp = fig.add_axes([0.1, 0.875 - 0.15 * i, 0.12, 0.01])
    desired_cpu_usage = Slider(
        ax=axamp,
        label="CPU desired usage ",
        valmin=0,
        valmax=100,
        valinit=pool.desired_cpu_usage,
        orientation="horizontal"
    )
    desired_cpu_usage.on_changed(
        functools.partial(update_desired_cpu_usage, i))

    axamp = fig.add_axes([0.1, 0.85 - 0.15 * i, 0.12, 0.01])
    cpu_weight = Slider(
        ax=axamp,
        label="CPU weight ",
        valmin=0,
        valmax=500,
        valinit=pool.weight,
        orientation="horizontal"
    )
    cpu_weight.on_changed(functools.partial(update_cpu_weight, i))

    axamp = fig.add_axes([0.1, 0.825 - 0.15 * i, 0.12, 0.015])
    enabled_checkbox = CheckButtons(
        ax=axamp,
        labels=["enabled"],
        actives=["enabled"] if pool.enabled else None
    )
    enabled_checkbox.on_clicked(functools.partial(
        update_enabled, i, enabled_checkbox))

    items.extend([cpu_limit_slider, desired_cpu_usage,
                 cpu_weight, enabled_checkbox])

axamp = fig.add_axes([0.1, 0.7 - 0.15 * i, 0.12, 0.1])
radio = RadioButtons(axamp, ('0', '1', '2', '3', '4'))
radio.on_clicked(update_active_chart)

fig.subplots_adjust(left=0.3, hspace=0.5)
plt.show()
