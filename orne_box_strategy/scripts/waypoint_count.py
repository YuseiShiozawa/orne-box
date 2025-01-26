#!/usr/bin/env python3

import rospy
from std_msgs.msg import Bool

class GoalReachedCounter:
    def __init__(self):
        # カウンターの初期化
        self.goal_reached_count = 0

        # `is_reached_goal` トピックをサブスクライブ
        rospy.Subscriber("/waypoint_manager/waypoint/is_reached", Bool, self.is_reached_goal_callback)

        # ログ出力用の定期的なタイマー
        self.timer = rospy.Timer(rospy.Duration(1.0), self.print_goal_reached_count)

    def is_reached_goal_callback(self, msg):
        # `is_reached_goal` が True ならカウントを増やす
        if msg.data:
            self.goal_reached_count += 1

    def print_goal_reached_count(self, event):
        # 現在のカウントをログに出力
        rospy.loginfo("Goal reached count: %d", self.goal_reached_count - 1)

if __name__ == '__main__':
    try:
        # ノードの初期化
        rospy.init_node('goal_reached_counter_node')

        # GoalReachedCounter クラスのインスタンスを作成
        counter = GoalReachedCounter()

        # ノードが終了しないようにスピン
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

