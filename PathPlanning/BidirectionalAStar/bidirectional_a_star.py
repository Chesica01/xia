"""

Bidirectional A* grid planning

author: Erwin Lejeune (@spida_rwin)

See Wikipedia article (https://en.wikipedia.org/wiki/Bidirectional_search)

"""

import math

import matplotlib.pyplot as plt

show_animation = True


class BidirectionalAStarPlanner:

    def __init__(self, ox, oy, reso, rr):
        """
        Initialize grid map for a star planning

        ox: x position list of Obstacles [m]
        oy: y position list of Obstacles [m]
        reso: grid resolution [m]
        rr: robot radius[m]
        """

        self.reso = reso
        self.rr = rr
        self.calc_obstacle_map(ox, oy)
        self.motion = self.get_motion_model()

    class Node:
        def __init__(self, x, y, cost, pind):
            self.x = x  # index of grid
            self.y = y  # index of grid
            self.cost = cost
            self.pind = pind

        def __str__(self):
            return str(self.x) + "," + str(self.y) + "," + str(
                self.cost) + "," + str(self.pind)

    def planning(self, sx, sy, gx, gy):
        """
        Bidirectional A star path search

        input:
            sx: start x position [m]
            sy: start y position [m]
            gx: goal x position [m]
            gy: goal y position [m]

        output:
            rx: x position list of the final path
            ry: y position list of the final path
        """

        nstart = self.Node(self.calc_xyindex(sx, self.minx),
                           self.calc_xyindex(sy, self.miny), 0.0, -1)
        ngoal = self.Node(self.calc_xyindex(gx, self.minx),
                          self.calc_xyindex(gy, self.miny), 0.0, -1)

        open_set_A, closed_set_A = dict(), dict()
        open_set_B, closed_set_B = dict(), dict()
        open_set_A[self.calc_grid_index(nstart)] = nstart
        open_set_B[self.calc_grid_index(ngoal)] = ngoal

        current_A = nstart
        current_B = ngoal

        while 1:
            if len(open_set_A) == 0:
                print("Open set A is empty..")
                break

            if len(open_set_B) == 0:
                print("Open set B is empty..")
                break

            c_id_A = min(
                open_set_A,
                key=lambda o: self.find_total_cost(open_set_A, o, current_B))

            current_A = open_set_A[c_id_A]

            c_id_B = min(
                open_set_B,
                key=lambda o: self.find_total_cost(open_set_B, o, current_A))

            current_B = open_set_B[c_id_B]

            # show graph
            if show_animation:  # pragma: no cover
                plt.plot(self.calc_grid_position(current_A.x, self.minx),
                         self.calc_grid_position(current_A.y, self.miny), "xc")
                plt.plot(self.calc_grid_position(current_B.x, self.minx),
                         self.calc_grid_position(current_B.y, self.miny), "xc")
                # for stopping simulation with the esc key.
                plt.gcf().canvas.mpl_connect('key_release_event',
                                             lambda event:
                                             [exit(0) if event.key == 'escape'
                                              else None])
                if len(closed_set_A.keys()) % 10 == 0:
                    plt.pause(0.001)

            if current_A.x == current_B.x and current_A.y == current_B.y:
                print("Found goal")
                meetpointA = current_A
                meetpointB = current_B
                break

            # Remove the item from the open set
            del open_set_A[c_id_A]
            del open_set_B[c_id_B]

            # Add it to the closed set
            closed_set_A[c_id_A] = current_A
            closed_set_B[c_id_B] = current_B

            # expand_grid search grid based on motion model
            for i, _ in enumerate(self.motion):

                c_nodes = [self.Node(current_A.x + self.motion[i][0],
                                     current_A.y + self.motion[i][1],
                                     current_A.cost + self.motion[i][2],
                                     c_id_A),
                           self.Node(current_B.x + self.motion[i][0],
                                     current_B.y + self.motion[i][1],
                                     current_B.cost + self.motion[i][2],
                                     c_id_B)]

                n_ids = [self.calc_grid_index(c_nodes[0]),
                         self.calc_grid_index(c_nodes[1])]

                # If the node is not safe, do nothing
                continue_ = self.check_nodes_and_sets(c_nodes, closed_set_A,
                                                      closed_set_B, n_ids)

                if not continue_[0]:
                    if n_ids[0] not in open_set_A:
                        # discovered a new node
                        open_set_A[n_ids[0]] = c_nodes[0]
                    else:
                        if open_set_A[n_ids[0]].cost > c_nodes[0].cost:
                            # This path is the best until now. record it
                            open_set_A[n_ids[0]] = c_nodes[0]

                if not continue_[1]:
                    if n_ids[1] not in open_set_B:
                        # discovered a new node
                        open_set_B[n_ids[1]] = c_nodes[1]
                    else:
                        if open_set_B[n_ids[1]].cost > c_nodes[1].cost:
                            # This path is the best until now. record it
                            open_set_B[n_ids[1]] = c_nodes[1]

        rx, ry = self.calc_final_bidirectional_path(
            meetpointA, meetpointB, closed_set_A, closed_set_B)

        return rx, ry

    # takes two sets and two meeting nodes and return the optimal path
    def calc_final_bidirectional_path(self, n1, n2, setA, setB):
        rx_A, ry_A = self.calc_final_path(n1, setA)
        rx_B, ry_B = self.calc_final_path(n2, setB)

        rx_A.reverse()
        ry_A.reverse()

        rx = rx_A + rx_B
        ry = ry_A + ry_B

        return rx, ry

    def calc_final_path(self, ngoal, closedset):
        # generate final course
        rx, ry = [self.calc_grid_position(ngoal.x, self.minx)], [
            self.calc_grid_position(ngoal.y, self.miny)]
        pind = ngoal.parent_index
        while pind != -1:
            n = closedset[pind]
            rx.append(self.calc_grid_position(n.x, self.minx))
            ry.append(self.calc_grid_position(n.y, self.miny))
            pind = n.parent_index

        return rx, ry

    def check_nodes_and_sets(self, c_nodes, closedSet_A, closedSet_B, n_ids):
        continue_ = [False, False]
        if not self.verify_node(c_nodes[0]) or n_ids[0] in closedSet_A:
            continue_[0] = True

        if not self.verify_node(c_nodes[1]) or n_ids[1] in closedSet_B:
            continue_[1] = True

        return continue_

    @staticmethod
    def calc_heuristic(n1, n2):
        w = 1.0  # weight of heuristic
        d = w * math.hypot(n1.x - n2.x, n1.y - n2.y)
        return d

    def find_total_cost(self, open_set, lambda_, n1):
        g_cost = open_set[lambda_].cost
        h_cost = self.calc_heuristic(n1, open_set[lambda_])
        f_cost = g_cost + h_cost
        return f_cost

    def calc_grid_position(self, index, minp):
        """
        calc grid position

        :param index:
        :param minp:
        :return:
        """
        pos = index * self.reso + minp
        return pos

    def calc_xyindex(self, position, min_pos):
        return round((position - min_pos) / self.reso)

    def calc_grid_index(self, node):
        return (node.y - self.miny) * self.xwidth + (node.x - self.minx)

    def verify_node(self, node):
        px = self.calc_grid_position(node.x, self.minx)
        py = self.calc_grid_position(node.y, self.miny)

        if px < self.minx:
            return False
        elif py < self.miny:
            return False
        elif px >= self.maxx:
            return False
        elif py >= self.maxy:
            return False

        # collision check
        if self.obmap[node.x][node.y]:
            return False

        return True

    def calc_obstacle_map(self, ox, oy):

        self.minx = round(min(ox))
        self.miny = round(min(oy))
        self.maxx = round(max(ox))
        self.maxy = round(max(oy))
        print("minx:", self.minx)
        print("miny:", self.miny)
        print("maxx:", self.maxx)
        print("maxy:", self.maxy)

        self.xwidth = round((self.maxx - self.minx) / self.reso)
        self.ywidth = round((self.maxy - self.miny) / self.reso)
        print("xwidth:", self.xwidth)
        print("ywidth:", self.ywidth)

        # obstacle map generation
        self.obmap = [[False for _ in range(self.ywidth)]
                      for _ in range(self.xwidth)]
        for ix in range(self.xwidth):
            x = self.calc_grid_position(ix, self.minx)
            for iy in range(self.ywidth):
                y = self.calc_grid_position(iy, self.miny)
                for iox, ioy in zip(ox, oy):
                    d = math.hypot(iox - x, ioy - y)
                    if d <= self.rr:
                        self.obmap[ix][iy] = True
                        break

    @staticmethod
    def get_motion_model():
        # dx, dy, cost
        motion = [[1, 0, 1],
                  [0, 1, 1],
                  [-1, 0, 1],
                  [0, -1, 1],
                  [-1, -1, math.sqrt(2)],
                  [-1, 1, math.sqrt(2)],
                  [1, -1, math.sqrt(2)],
                  [1, 1, math.sqrt(2)]]

        return motion


def main():
    print(__file__ + " start!!")

    # start and goal position
    sx = 10.0  # [m]
    sy = 10.0  # [m]
    gx = 50.0  # [m]
    gy = 50.0  # [m]
    grid_size = 2.0  # [m]
    robot_radius = 1.0  # [m]

    # set obstacle positions
    ox, oy = [], []
    for i in range(-10, 60):
        ox.append(i)
        oy.append(-10.0)
    for i in range(-10, 60):
        ox.append(60.0)
        oy.append(i)
    for i in range(-10, 61):
        ox.append(i)
        oy.append(60.0)
    for i in range(-10, 61):
        ox.append(-10.0)
        oy.append(i)
    for i in range(-10, 40):
        ox.append(20.0)
        oy.append(i)
    for i in range(0, 40):
        ox.append(40.0)
        oy.append(60.0 - i)

    if show_animation:  # pragma: no cover
        plt.plot(ox, oy, ".k")
        plt.plot(sx, sy, "og")
        plt.plot(gx, gy, "ob")
        plt.grid(True)
        plt.axis("equal")

    bidir_a_star = BidirectionalAStarPlanner(ox, oy, grid_size, robot_radius)
    rx, ry = bidir_a_star.planning(sx, sy, gx, gy)

    if show_animation:  # pragma: no cover
        plt.plot(rx, ry, "-r")
        plt.pause(.0001)
        plt.show()


if __name__ == '__main__':
    main()
