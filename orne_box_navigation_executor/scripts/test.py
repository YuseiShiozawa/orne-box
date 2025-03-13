import rospy
from sensor_msgs.msg import LaserScan

def callback(scan):
    pub.publish(scan)

rospy.init_node('scan_republisher')
pub = rospy.Publisher('/scan', LaserScan, queue_size=10)
rospy.Subscriber('/scan_throttle', LaserScan, callback)
rospy.spin()

