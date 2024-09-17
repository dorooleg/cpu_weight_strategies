#!/usr/bin/env python3

epsilon = 0.01


class ChartLine:
    def __init__(self, color, label, line_type):
        self.x = []
        self.y = []
        self.color = color
        self.label = label
        self.line_type = line_type


class Chart:
    def __init__(self, lines, title, xlabel, ylabel):
        self.lines = lines
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel


class ResourcePool:

    def __init__(self, limit, weight, desired_cpu_usage, enabled):
        assert 0 <= limit and limit <= 100
        assert 0 <= weight
        self.new_cpu_limit = limit
        self.cpu_limit = limit
        self.weight = weight
        self.real_cpu_usage = 0.0
        self.desired_cpu_usage = desired_cpu_usage
        self.cpu_guarantee = 0.0
        self.enabled = enabled

    def __str__(self):
        return "cpu_limit: {} new_cpu_limit {} weight: {} real_cpu_usage: {} desired_cpu_usage: {} cpu_guarantee: {}".format(self.cpu_limit,
                                                                                                                             self.new_cpu_limit,
                                                                                                                             self.weight,
                                                                                                                             self.real_cpu_usage,
                                                                                                                             self.desired_cpu_usage,
                                                                                                                             self.cpu_guarantee)

    def __repr__(self):
        return self.__str__()


class ScheduleWeightStrategy:

    def __init__(self, resource_pools):
        self.resource_pools = resource_pools

    def recalculate(self):
        self._clear_previous_calculations()
        self._calculate_cpu_guarantee()
        self._calculate_real_cpu_usage()

    def _clear_previous_calculations(self):
        for idx, pool in enumerate(self.resource_pools):
            pool.real_cpu_usage = 0.0
            pool.cpu_guarantee = 0.0
            self.resource_pools[idx] = pool

    def _calculate_cpu_guarantee(self):
        cpu = 100.0
        delta = 100.0
        while cpu > epsilon and delta > 0:
            total_weights = sum([pool.weight if pool.cpu_guarantee <
                                pool.cpu_limit and pool.enabled else 0 for pool in self.resource_pools])

            delta = 0.0
            for idx, pool in enumerate(self.resource_pools):
                if pool.cpu_guarantee >= pool.cpu_limit or not pool.enabled:
                    continue
                old_cpu = pool.cpu_guarantee
                pool.cpu_guarantee = min(pool.cpu_guarantee + cpu * pool.weight /
                                         total_weights, pool.cpu_limit)
                delta += pool.cpu_guarantee - old_cpu
                self.resource_pools[idx] = pool
            cpu -= delta

    def _calculate_real_cpu_usage(self):
        cpu = 100.0
        total_weights = sum([pool.weight if pool.real_cpu_usage < min(
            pool.cpu_limit, pool.desired_cpu_usage) and pool.enabled else 0 for pool in self.resource_pools])
        while cpu > epsilon and total_weights > epsilon:
            delta = 0.0
            for idx, pool in enumerate(self.resource_pools):
                if pool.real_cpu_usage >= min(pool.cpu_limit, pool.desired_cpu_usage) or not pool.enabled:
                    continue
                old_cpu = pool.real_cpu_usage
                pool.real_cpu_usage = min(pool.real_cpu_usage + cpu * pool.weight /
                                          total_weights, min(pool.cpu_limit, pool.desired_cpu_usage))
                delta += pool.real_cpu_usage - old_cpu
                self.resource_pools[idx] = pool
            cpu -= delta
            total_weights = sum([pool.weight if pool.real_cpu_usage < min(
                pool.cpu_limit, pool.desired_cpu_usage) and pool.enabled else 0 for pool in self.resource_pools])

    def get_charts(self, pool_idx):
        assert 0 <= pool_idx and pool_idx < len(self.resource_pools)
        pool_chart = Chart([ChartLine("blue", "CPU usage", "-"), ChartLine("green", "CPU guarantee", "^"), ChartLine(
            "green", "CPU limit", "v")], "ScheduleWeightStrategy for pool " + str(pool_idx), "desired CPU usage", "real CPU usage")
        total_chart = Chart([ChartLine("blue", "CPU usage", "-")],
                            "ScheduleWeightStrategy overall", "desired CPU usage", "real CPU usage")
        for desired_cpu_usage in range(0, 101):
            self.resource_pools[pool_idx].desired_cpu_usage = desired_cpu_usage
            self.recalculate()
            for idx, line in enumerate(pool_chart.lines):
                line.x.append(desired_cpu_usage)
                pool_chart.lines[idx] = line
            for idx, line in enumerate(total_chart.lines):
                line.x.append(
                    sum([pool.desired_cpu_usage if pool.enabled else 0 for pool in self.resource_pools]))
                total_chart.lines[idx] = line
            pool_chart.lines[0].y.append(
                self.resource_pools[pool_idx].real_cpu_usage)
            pool_chart.lines[1].y.append(
                self.resource_pools[pool_idx].cpu_guarantee)
            pool_chart.lines[2].y.append(
                self.resource_pools[pool_idx].cpu_limit)
            total_chart.lines[0].y.append(
                sum([pool.real_cpu_usage if pool.enabled else 0 for pool in self.resource_pools]))
        return [pool_chart, total_chart]


class LimitWeightStrategy:

    def __init__(self, resource_pools):
        self.resource_pools = resource_pools

    def recalculate(self):
        self._clear_previouse_calculations()
        self._caluclate_new_cpu_limit()
        self._caluclate_real_usage()

    def _clear_previouse_calculations(self):
        for idx, pool in enumerate(self.resource_pools):
            pool.real_cpu_usage = 0.0
            pool.cpu_guarantee = 0.0
            pool.new_cpu_limit = 0.0
            self.resource_pools[idx] = pool

    def _caluclate_new_cpu_limit(self):
        total_weights = sum([pool.weight if pool.desired_cpu_usage >
                            0 and pool.enabled else 0 for pool in self.resource_pools])
        for idx, pool in enumerate(self.resource_pools):
            if pool.desired_cpu_usage <= 0 or not pool.enabled:
                continue
            pool.new_cpu_limit = min(
                pool.cpu_limit, 100 * pool.weight / total_weights)
            self.resource_pools[idx] = pool

    def _caluclate_real_usage(self):
        for idx, pool in enumerate(self.resource_pools):
            if pool.desired_cpu_usage <= 0 or not pool.enabled:
                continue
            pool.real_cpu_usage = min(
                pool.desired_cpu_usage, pool.new_cpu_limit)
            self.resource_pools[idx] = pool

    def get_charts(self, pool_idx):
        assert 0 <= pool_idx and pool_idx < len(self.resource_pools)
        pool_chart = Chart([ChartLine("blue", "CPU usage", "-"), ChartLine("green", "CPU limit", "v"), ChartLine(
            "green", "CPU limit (new)", "v")], "LimitWeightStrategy for pool " + str(pool_idx), "desired CPU usage", "real CPU usage")
        total_chart = Chart([ChartLine("blue", "CPU usage", "-")],
                            "LimitWeightStrategy overall", "desired CPU usage", "real CPU usage")
        cpu_usage = ChartLine("blue", "CPU usage", "-")
        cpu_limit = ChartLine("green", "CPU limit", "v")
        new_cpu_limit = ChartLine("green", "CPU limit (new)", "v")
        for desired_cpu_usage in range(0, 101):
            self.resource_pools[pool_idx].desired_cpu_usage = desired_cpu_usage
            self.recalculate()
            for idx, line in enumerate(pool_chart.lines):
                line.x.append(desired_cpu_usage)
                pool_chart.lines[idx] = line
            for idx, line in enumerate(total_chart.lines):
                line.x.append(
                    sum([pool.desired_cpu_usage if pool.enabled else 0 for pool in self.resource_pools]))
                total_chart.lines[idx] = line
            pool_chart.lines[0].y.append(
                self.resource_pools[pool_idx].real_cpu_usage)
            pool_chart.lines[1].y.append(
                self.resource_pools[pool_idx].cpu_limit)
            pool_chart.lines[2].y.append(
                self.resource_pools[pool_idx].new_cpu_limit)
            total_chart.lines[0].y.append(
                sum([pool.real_cpu_usage if pool.enabled else 0 for pool in self.resource_pools]))
        return [pool_chart, total_chart]
