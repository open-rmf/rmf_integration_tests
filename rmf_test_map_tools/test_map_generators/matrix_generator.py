#!/usr/bin/env python3

import argparse
import os
import yaml


class MatrixGenerator:
    def __init__(self, rows, cols, spacing, num_robots):
        self.rows = rows
        self.cols = cols
        self.spacing = spacing
        self.num_robots = num_robots

    def generate(self, output_filename):
        print('generate')

        vertices = [
            [0, -1, 0, 'dummy_0', {}],
            [1, -1, 0, 'dummy_1', {}],
        ]

        lane_names = []

        robot_idx = 0
        for row_idx in range(0, self.rows):
            for col_idx in range(0, self.cols):
                x = (col_idx + 1) * self.spacing
                y = (row_idx + 1) * self.spacing
                name = f'wp_{row_idx}_{col_idx}'
                params = {
                    'is_parking_spot': [4, True],
                    'is_holding_point': [4, True]
                }

                if robot_idx < self.num_robots:
                    params['spawn_robot_name'] = [1, f'tinyRobot{robot_idx}']
                    params['spawn_robot_type'] = [1, 'TinyRobot']
                    params['is_charger'] = [4, True]
                    robot_idx += 1

                vertices.append([x, y, 0, name, params])

                if row_idx > 0:
                    lane_names.append([f'wp_{row_idx-1}_{col_idx}', name])
                if col_idx > 0:
                    lane_names.append([f'wp_{row_idx}_{col_idx-1}', name])

        # walls (to make the simulation more visually comprehensible)
        wall_names = []

        # exterior walls
        ext_llx = 0.5 * self.spacing
        ext_lly = 0.5 * self.spacing
        ext_urx = (self.cols + 0.5) * self.spacing
        ext_ury = (self.rows + 0.5) * self.spacing
        vertices.append([ext_llx, ext_lly, 0, 'exterior_0', {}])
        vertices.append([ext_llx, ext_ury, 0, 'exterior_1', {}])
        vertices.append([ext_urx, ext_ury, 0, 'exterior_2', {}])
        vertices.append([ext_urx, ext_lly, 0, 'exterior_3', {}])
        wall_names.append(['exterior_0', 'exterior_1'])
        wall_names.append(['exterior_1', 'exterior_2'])
        wall_names.append(['exterior_2', 'exterior_3'])
        wall_names.append(['exterior_3', 'exterior_0'])

        # interior walls
        for row_idx in range(1, self.rows):
            for col_idx in range(1, self.cols):
                llx = (col_idx + 0.25) * self.spacing
                lly = (row_idx + 0.25) * self.spacing
                urx = (col_idx + 0.75) * self.spacing
                ury = (row_idx + 0.75) * self.spacing
                stem = f'box_{row_idx}_{col_idx}'
                vertices.append([llx, lly, 0, stem + '_0', {}])
                vertices.append([llx, ury, 0, stem + '_1', {}])
                vertices.append([urx, ury, 0, stem + '_2', {}])
                vertices.append([urx, lly, 0, stem + '_3', {}])
                wall_names.append([stem + '_0', stem + '_1'])
                wall_names.append([stem + '_1', stem + '_2'])
                wall_names.append([stem + '_2', stem + '_3'])
                wall_names.append([stem + '_3', stem + '_0'])

        vidx_lookup = {}
        for idx in range(len(vertices)):
            v = vertices[idx]
            vidx_lookup[v[3]] = idx

        lanes = []
        for lane in lane_names:
            lanes.append([
                vidx_lookup[lane[0]],
                vidx_lookup[lane[1]],
                {
                    'bidirectional': [4, True],
                    'speed_limit': [3, 0.5],
                    'graph_idx': [2, 0],
                }
            ])

        walls = []
        for wall in wall_names:
            walls.append([
                vidx_lookup[wall[0]],
                vidx_lookup[wall[1]],
                {
                }
            ])

        measurements = [
            [0, 1, {'distance': [3, 1.0]}]
        ]

        level_yaml = {
          'elevation': 0,
          'lanes': lanes,
          'layers': {},
          'measurements': measurements,
          'vertices': vertices,
          'walls': walls,
          'x_meters': (self.cols + 1) * self.spacing,
          'y_meters': (self.rows + 1) * self.spacing,
        }

        site_yaml = {}
        site_yaml['coordinate_system'] = 'cartesian_meters'
        site_yaml['name'] = 'matrix'
        site_yaml['graphs'] = {
            0: {
                'default_lane_width': 0.7,
                'name': 'delivery'
            }
        }

        site_yaml['levels'] = {}
        site_yaml['levels']['L1'] = level_yaml
        site_yaml['lifts'] = {}

        if not os.path.exists(os.path.dirname(output_filename)):
            os.makedirs(os.path.dirname(output_filename))

        with open(output_filename, 'w') as f:
            yaml.dump(site_yaml, f)
        print(f'wrote {output_filename}')


def main():
    parser = argparse.ArgumentParser(
        prog="matrix traffic map generator"
    )
    parser.add_argument("-r",
                        "--rows",
                        default=8,
                        type=int,
                        help="number of rows")
    parser.add_argument("-c",
                        "--cols",
                        default=8,
                        type=int,
                        help="number of columns")
    parser.add_argument("-n",
                        "--robots",
                        default=3,
                        type=int,
                        help="number of robots")
    parser.add_argument("-o",
                        "--output",
                        type=str,
                        default="matrix.building.yaml",
                        help="output filename")
    parser.add_argument("-s",
                        "--spacing",
                        default=4.0,
                        type=float,
                        help="row/col spacing")
    args = parser.parse_args()
    mg = MatrixGenerator(
        args.rows,
        args.cols,
        args.spacing,
        args.robots)
    mg.generate(args.output)
