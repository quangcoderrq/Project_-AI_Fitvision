
import mediapipe as mp
print(f"MediaPipe version: {mp.__version__}")
print(f"Dir(mp): {dir(mp)}")

try:
    import mediapipe.solutions.pose as pose
    print("Import 'mediapipe.solutions.pose' SUCCESS")
except ImportError as e:
    print(f"Import 'mediapipe.solutions.pose' FAIL: {e}")

try:
    from mediapipe.python.solutions import pose
    print("Import 'mediapipe.python.solutions' SUCCESS")
except ImportError as e:
    print(f"Import 'mediapipe.python.solutions' FAIL: {e}")

try:
    import mediapipe.tasks.python.vision as vision
    print("Import 'mediapipe.tasks.python.vision' SUCCESS")
except ImportError as e:
    print(f"Import 'mediapipe.tasks.python.vision' FAIL: {e}")
