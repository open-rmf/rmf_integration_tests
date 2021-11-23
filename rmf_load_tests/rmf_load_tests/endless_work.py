#!/usr/bin/env python3

# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import uuid
import time
import argparse
import random

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rmf_task_msgs.srv import SubmitTask
from rmf_task_msgs.msg import TaskType, Loop, TaskSummary
from rmf_fleet_msgs.msg import FleetState, RobotMode

###############################################################################


class EndlessWorker:
    def __init__(self, argv=sys.argv):
        self.node = rclpy.create_node('endless_worker')
        self.submit_task_srv = self.node.create_client(
            SubmitTask,
            '/submit_task')

        self.node.set_parameters([
            Parameter('use_sim_time', Parameter.Type.BOOL, True)
        ])

        '''
        self.tasks_sub = self.node.create_subscription(
            TaskSummary,
            '/task_summaries',
            self.task_summaries_callback,
            50)
        '''

        self.is_robot_idle = {}

        # to avoid hammering the planner, we'll only issue tasks
        # once every 30 seconds to however many robots seem idle
        self.idle_robot_count = 0

        self.fleets_sub = self.node.create_subscription(
            FleetState,
            '/fleet_states',
            self.fleet_states_callback,
            50)
        
        # self.task_start_timer = self.node.create_timer(
        #     30.0,
        #     self.task_start_timer)

    def task_start_timer(self):
        print('task_start_timer()')
        for task_idx in range(0, self.idle_robot_count):
            loop = Loop()
            loop.num_loops = 1
            start_row = random.randint(0, 8)
            start_col = random.randint(0, 8)
            end_row = random.randint(0, 8)
            end_col = random.randint(0, 8)
            loop.start_name = f'wp_{start_row}_{start_col}'
            loop.finish_name = f'wp_{end_row}_{end_col}'

            print(f'submitting: {loop.start_name} -> {loop.finish_name}')

            req_msg = SubmitTask.Request()
            req_msg.description.task_type.type = TaskType.TYPE_LOOP
            req_msg.description.loop = loop

            try:
                future = self.submit_task_srv.call_async(req_msg)
                #print('spinning until future complete...')
                #rclpy.spin_until_future_complete(
                #    self.node, future, timeout_sec=1.0)
                #response = future.result()
                #print(f'response: {response}')
            except Exception as e:
                self.node.get_logger().error(f'task srv err: {e}')

        self.idle_robot_count = 0

    def fleet_states_callback(self, msg):
        self.idle_robot_count = 0
        for robot in msg.robots:
            # print(f'{robot.name} mode: {robot.mode.mode}')
            if robot.mode.mode == RobotMode.MODE_IDLE or \
                    robot.mode.mode == RobotMode.MODE_PAUSED:
                self.idle_robot_count += 1
        print(f'num_idle = {self.idle_robot_count}')

    '''
    def task_summaries_callback(self, msg):
        if msg.state == TaskSummary.STATE_QUEUED or \
                msg.state == TaskSummary.STATE_ACTIVE:
            print(f'task summary for robot {msg.robot_name} {msg.task_id}: {msg.status}')

        is_idle_task = 'waiting' in msg.task_id

        self.is_robot_idle = 'waiting' 
        if msg.robot_name not in self.idle_robots:
    '''

    def main(self):
        while rclpy.ok():
            rclpy.spin_once(self.node)

        # try:
        #     rclpy.spin(self.node)
        #     print('done spinning')
        # except KeyboardInterrupt as e:
        #     pass


def main(argv=sys.argv):
    rclpy.init(args=sys.argv)
    args_without_ros = rclpy.utilities.remove_ros_args(sys.argv)

    endless_worker = EndlessWorker(args_without_ros)
    endless_worker.main()
    rclpy.shutdown()


if __name__ == '__main__':
    main(sys.argv)
