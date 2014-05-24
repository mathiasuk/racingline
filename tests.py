import json
import math
import unittest

from models import Point, Lap, Session, get_color_from_ratio


class TestPoint(unittest.TestCase):
    def setUp(self):
        self.point = Point(10, -100, 33)
        self.point.speed = 154
        self.point.gas = 0.98
        self.point.brake = 0.1
        self.point.clutch = 0.4

    def test_equal_coords(self):
        self.assertTrue(self.point.equal_coords(Point(10, -100, 33)))

    def test_dumps(self):
        result = self.point.dumps()
        self.assertEqual(result['x'], self.point.x)
        self.assertEqual(result['y'], self.point.y)
        self.assertEqual(result['z'], self.point.z)
        self.assertEqual(result['s'], self.point.speed)
        self.assertEqual(result['g'], self.point.gas)
        self.assertEqual(result['b'], self.point.brake)
        self.assertEqual(result['c'], self.point.clutch)


class TestLap(unittest.TestCase):
    def setUp(self):
        session = Session()
        session.app_size_x = 400
        session.app_size_y = 200
        self.lap = Lap(session, 0)
        self.lap.points.append(Point(10, 0, 10, 100, 0.9, 0, 0.2))
        self.lap.points.append(Point(13, 0, 10, 110, 1.0, 0, 0.0))
        self.lap.points.append(Point(15, 0, 13, 130, 1.0, 0, 0.0))
        self.lap.points.append(Point(17, 0, 15, 140, 0.1, 0.8, 0.9))

    def test_last_point(self):
        self.assertEqual(self.lap.last_point, self.lap.points[-1])

    def test_normalise(self):
        result = self.lap.normalise(self.lap.last_point, math.pi / 2)
        self.assertTrue(result[0].equal_coords(Point(205, 0, 93)))
        self.assertTrue(result[1].equal_coords(Point(205, 0, 96)))
        self.assertTrue(result[2].equal_coords(Point(202, 0, 98)))
        self.assertTrue(result[3].equal_coords(Point(200, 0, 100)))

    def test_normalise_zoomin(self):
        self.lap.session.zoom = 1.4
        result = self.lap.normalise(self.lap.last_point, math.pi / 2)
        self.assertTrue(result[0].equal_coords(Point(207, 0, 90.2)))
        self.assertTrue(result[1].equal_coords(Point(207, 0, 94.4)))
        self.assertTrue(result[2].equal_coords(Point(202.8, 0, 97.2)))
        self.assertTrue(result[3].equal_coords(Point(200, 0, 100)))

    def test_normalise_zoomout(self):
        self.lap.session.zoom = 0.5
        result = self.lap.normalise(self.lap.last_point, math.pi / 2)
        self.assertTrue(result[0].equal_coords(Point(202.5, 0, 96.5)))
        self.assertTrue(result[1].equal_coords(Point(202.5, 0, 98)))
        self.assertTrue(result[2].equal_coords(Point(201, 0, 99)))
        self.assertTrue(result[3].equal_coords(Point(200, 0, 100)))

    def test_json_dumps(self):
        session = Session()
        lap = Lap(session, 0)
        lap.json_loads(json.loads(self.lap.json_dumps()))
        self.assertEqual(lap.count, self.lap.count)
        self.assertEqual(lap.count, self.lap.invalid)
        self.assertEqual(lap.count, self.lap.laptime)
        for p1, p2 in zip(lap.points, self.lap.points):
            for key, dummy in p2.keys:
                self.assertEqual(getattr(p1, key), getattr(p2, key))

    def test_closest_point(self):
        point = Point(14, 0, 13)
        self.assertEqual(self.lap.closest_point(point), self.lap.points[2])


class TestSession(unittest.TestCase):
    def setUp(self):
        self.session = Session()

    def test_new_lap(self):
        self.assertEqual(self.session.current_lap, None)
        self.session.new_lap(0)
        self.session.current_lap.laptime = 6000

        # Check best_lap is set correctly:
        self.session.new_lap(1)
        self.assertEqual(self.session.best_lap.laptime, 6000)

        # Add slower lap
        self.session.current_lap.laptime = 8000
        self.session.new_lap(2)

        # Check best_lap is still correct
        self.assertEqual(self.session.best_lap.laptime, 6000)

        # Add faster lap
        self.session.current_lap.laptime = 5500
        self.session.new_lap(3)

        # Check best_lap has been updated
        self.assertEqual(self.session.best_lap.laptime, 5500)


class TestMisc(unittest.TestCase):
    def test_get_color_from_ratio(self):
        self.assertEqual(get_color_from_ratio(0, mode='gr'), (0, 1, 0, 1))
        self.assertEqual(get_color_from_ratio(0.25, mode='gr'), (0.5, 1, 0, 1))
        self.assertEqual(get_color_from_ratio(0.5, mode='gr'), (1, 1, 0, 1))
        self.assertEqual(get_color_from_ratio(0.75, mode='gr'), (1, 0.5, 0, 1))
        self.assertEqual(get_color_from_ratio(1, mode='gr'), (1, 0, 0, 1))
        self.assertEqual(get_color_from_ratio(3.5, mode='gr'), (1, 0, 0, 1))

        self.assertEqual(get_color_from_ratio(0), (1, 1, 0, 1))
        self.assertEqual(get_color_from_ratio(0.25), (1, 0.75, 0, 1))
        self.assertEqual(get_color_from_ratio(0.5), (1, 0.5, 0, 1))
        self.assertEqual(get_color_from_ratio(0.75), (1, 0.25, 0, 1))
        self.assertEqual(get_color_from_ratio(1), (1, 0, 0, 1))
        self.assertEqual(get_color_from_ratio(3.5), (1, 0, 0, 1))


if __name__ == '__main__':
    unittest.main()
