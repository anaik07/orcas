#!/usr/bin/env python
import sys
import rospy
from std_msgs.msg import Header, ColorRGBA
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Vector3, Pose, Point, Quaternion
from visualization_msgs.msg import Marker
from tf.transformations import quaternion_from_euler
# path plan in python
import math


class PathPlanner(object):
    """ ROS node to plan a path for the Pathfinder Boat """
    def __init__(self):
        super(PathPlanner, self).__init__()
        rospy.init_node('path_planner')
        self.scan_sub = rospy.Subscriber("structured_light_scan", LaserScan, self.on_scan)
        self.path_pub = rospy.Publisher("path_plan", Marker, queue_size=10)

    def on_scan(self, laser_scan):
        gap_center, gap_width = path_location(laser_scan.ranges)
        sys.stderr.write("{} {}\n".format(gap_center, gap_width))
        self.path_pub.publish(
            header=Header(
                stamp=rospy.Time.now(),
                frame_id='webcam_frame'
            ),
            type=Marker.ARROW,
            pose=self.get_pose(gap_center * laser_scan.angle_increment + laser_scan.angle_min),
            scale=Vector3(0.1, 0.01, 0.01),
            color=ColorRGBA(0.0, 0.0, 1.0, 0.4)
        )

    def get_pose(self, angle):
        orientation_tuple = quaternion_from_euler(
            0,
            0,
            angle
        )

        return Pose(
            position=Point(x=0, y=0, z=0),
            orientation=Quaternion(
                x=orientation_tuple[0],
                y=orientation_tuple[1],
                z=orientation_tuple[2],
                w=orientation_tuple[3]
            )
        )


def path_location(range_array):
    count = 0
    longest_pos = -1
    threshold = 1.0
    location_range = [0, 0]  # indices
    length = len(range_array)
    for i in range(length):
        if range_array[i] >= threshold or math.isnan(range_array[i]):
            count += 1
            if longest_pos < count:
                longest_pos = count
                location_range[0] = i - longest_pos + 1
                location_range[1] = i
        else:
            count = 0
        i += 1
    center_point = (location_range[0] + location_range[1]) / 2.0

    return center_point, length


def rudder_pos(gap_center, range_length):
    '''
    normalized values:
    r = 30, l = -30, s = 0
    not normalized values:
    r = 120, l = 60, s = 90
    '''
    slope = 30 / (range_length / 2.0)
    intercept = -30.0
    position = ((slope * gap_center) + intercept) + 90.0

    return int(position)

if __name__ == '__main__':
    # test = [70, 60, 50, 10, 70, 60, 50, 50, 50, 70]
    # gap_center, range_length = path_location(test)
    # print(rudder_pos(gap_center, range_length))
    path_planner = PathPlanner()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")