from unittest import TestCase

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) +
                "/../PathPlanning/Dijkstra/")
try:
    import dijkstra as m
except:
    raise

print(__file__)


class Test(TestCase):

    def test1(self):
        m.show_animation = True
        m.main()
