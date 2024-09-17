import unittest
from weight_strategies import ResourcePool, ScheduleWeightStrategy


class TestScheduleWeightStrategy(unittest.TestCase):
    def test_single_resource_pool(self):
        resource_pools = [
            ResourcePool(100, 100, 1, True)
        ]
        schedule_weight_strategy = ScheduleWeightStrategy(resource_pools)
        schedule_weight_strategy.recalculate()
        self.assertEqual(resource_pools[0].cpu_limit, 100)
        self.assertEqual(resource_pools[0].weight, 100)      
        self.assertEqual(resource_pools[0].desired_cpu_usage, 1)      
        self.assertEqual(resource_pools[0].real_cpu_usage, 1)         
