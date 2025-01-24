from dynamic_reconfigure.client import Client
import rospy
from std_srvs.srv import Empty
import cv2
from ultralytics import YOLO
import time

# ROSノードの初期化
rospy.init_node('bicycle_detection_node')

# YOLOv8モデルの読み込み
model = YOLO("/home/shiozawa/yolov8n.pt")  # モデルのパスを指定

# dynamic_reconfigureのクライアント設定
client = Client("/move_base/local_costmap/inflation_layer", timeout=30)

# サービスを呼び出す関数（必要な場合）
def clear_costmaps():
    try:
        rospy.wait_for_service('/move_base/clear_costmaps', timeout=5)
        clear_costmaps_service = rospy.ServiceProxy('/move_base/clear_costmaps', Empty)
        clear_costmaps_service()
        rospy.loginfo("Costmaps cleared!")
    except rospy.ROSException as e:
        rospy.logwarn(f"Service call failed: {e}")

# USBカメラの設定
cap = cv2.VideoCapture(4)  # デフォルトのカメラを使用（USBカメラ）

if not cap.isOpened():
    print("カメラが開けませんでした。")
    exit()

# 画像のサイズを設定（任意）
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640/2/2)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480/2/2)

# フレームレートを制限するための変数（例えば、1秒に10フレーム）
frame_rate = 2 # 10 FPS
frame_interval = 1.0 / frame_rate  # 1フレームごとの間隔（秒）

# 最後に処理した時間を記録する変数
last_time = time.time()

# リアルタイムで画像を取得し、自転車の検出を行う
while not rospy.is_shutdown():
    current_time = time.time()
    
    # フレーム間隔が経過していれば、次のフレームを処理する
    if current_time - last_time >= frame_interval:
        ret, frame = cap.read()

        if not ret:
            print("画像の取得に失敗しました。")
            break

        # YOLOv8で物体検出
        detections = model(frame)  # 物体検出結果を取得

        # 自転車の検出数をカウント
        bicycle_count = sum([1 for detection in detections[0].boxes if detection.cls == 1])  # '1'が自転車のクラスID

        # 自転車が2台以上検出された場合、inflation_radiusを0に変更
        if bicycle_count >= 2:
            # inflation_radiusを0に設定
            client.update_configuration({"inflation_radius": 0.0})
            rospy.loginfo("Inflation radius set to 0.")
        else:
            client.update_configuration({"inflation_radius": 0.22})
            rospy.loginfo("Inflation radius set to 0.22")

        # 検出結果を画面に表示（オプション）


        # 画像を表示
        cv2.imshow('Bicycle Detection', frame)

        # 最後に処理した時間を更新
        last_time = current_time

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 後処理
cap.release()
cv2.destroyAllWindows()
