import time
import cv2
from ultralytics import YOLO
import rospy
from std_srvs.srv import Empty

# ROSノードの初期化
rospy.init_node('bicycle_detection_node')

# YOLOv8モデルの読み込み（ダウンロードしたモデルのパスを指定）
model = YOLO("/home/shiozawa/yolov8n.pt")  # モデルのパスを指定

# サービスを呼び出す関数
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
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # 解像度を320x240に設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# リアルタイムで画像を取得し、自転車の検出を行う
while not rospy.is_shutdown():
    ret, frame = cap.read()
    
    if not ret:
        print("画像の取得に失敗しました。")
        break

    # 物体検出の実行（1秒に1回実行）
    start_time = time.time()

    # YOLOv8で物体検出
    detections = model(frame)  # 物体検出結果を取得
    
    # 自転車の検出数をカウント
    bicycle_count = sum([1 for detection in detections[0].boxes if detection.cls == 1])  # '1'が自転車のクラスID

    # 自転車が2台以上検出された場合、clear_costmapsを呼び出す
    if bicycle_count >= 1:
        clear_costmaps()

    # 検出結果を画面に表示
    # for detection in detections[0].boxes:
    #     if detection.cls == 1:  # '1'が自転車のクラスID
    #         x1, y1, x2, y2 = map(int, detection.xyxy)  # バウンディングボックス座標
    #         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #         cv2.putText(frame, "Bicycle", (x1, y1 - 10),
    #                      cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # 画像を表示
    cv2.imshow('Bicycle Detection', frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # フレーム処理時間に基づいて待機時間を計算
    frame_process_time = time.time() - start_time
    sleep_time = max(1.0 - frame_process_time, 0)  # 最低でも1秒待つようにする
    time.sleep(sleep_time)

# 後処理
cap.release()
cv2.destroyAllWindows()
