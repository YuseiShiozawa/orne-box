#!/usr/bin/env python3
import rospy
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry

class OdomAMCLPathPublisher:
    def __init__(self):
        rospy.init_node('odom_amcl_path_publisher', anonymous=True)

        # Path の Publisher
        self.odom_path_pub = rospy.Publisher("/odom_path", Path, queue_size=10)
        self.amcl_path_pub = rospy.Publisher("/amcl_path", Path, queue_size=10)

        # AMCL の補正後の位置情報を購読
        rospy.Subscriber("/amcl_pose", PoseWithCovarianceStamped, self.amcl_callback)
        # オドメトリ情報を購読
        rospy.Subscriber("/icart_mini/odom", Odometry, self.odom_callback)

        # 軌跡データ
        self.odom_path = Path()
        self.odom_path.header.frame_id = "odom"

        self.amcl_path = Path()
        self.amcl_path.header.frame_id = "map"

        rospy.loginfo("Odom & AMCL Path Publisher Initialized")

    def amcl_callback(self, msg):
        """ AMCL の位置データを Path に変換して記録 """
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose  # `PoseWithCovarianceStamped` から `PoseStamped` へ変換

        self.amcl_path.poses.append(pose)

        # 履歴を制限（過去500点まで）
        if len(self.amcl_path.poses) > 500:
            self.amcl_path.poses.pop(0)

        self.amcl_path.header.stamp = rospy.Time.now()
        self.amcl_path_pub.publish(self.amcl_path)

    def odom_callback(self, msg):
        """ オドメトリの位置データを Path に変換して記録 """
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose  # `Odometry` から `PoseStamped` へ変換

        self.odom_path.poses.append(pose)

        # 履歴を制限（過去500点まで）
#        if len(self.odom_path.poses) > 50000:
 #           self.odom_path.poses.pop(0)

        self.odom_path.header.stamp = rospy.Time.now()
        self.odom_path_pub.publish(self.odom_path)

if __name__ == '__main__':
    try:
        path_publisher = OdomAMCLPathPublisher()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

