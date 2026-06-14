# Body Size AI - Hệ thống đề xuất size quần áo bằng AI

Hệ thống sử dụng pose estimation và machine learning để phân tích hình ảnh người dùng, kết hợp với chiều cao và cân nặng để đề xuất size quần áo phù hợp.

## 🚀 Tính năng

- **Pose Estimation**: Sử dụng MediaPipe để phát hiện các điểm cơ thể
- **Feature Extraction**: Trích xuất vector đặc trưng từ keypoints
- **ML Prediction**: Dự đoán số đo cơ thể (chest, waist, hip)
- **Size Mapping**: Đề xuất size phù hợp theo từng brand

## 📁 Cấu trúc dự án

```
body-size-ai/
├── data/
│   ├── synthetic/          # Dữ liệu giả lập
│   └── size_chart/         # Bảng size theo brand
├── models/                 # Trained models
├── src/
│   ├── preprocessing/      # Xử lý ảnh đầu vào
│   ├── pose/              # Pose estimation
│   ├── features/          # Trích xuất đặc trưng
│   ├── models/            # ML models
│   ├── sizing/            # Size mapping
│   ├── utils/             # Utilities
│   └── api/               # FastAPI endpoints
└── tests/                 # Unit tests
```

## 🛠️ Cài đặt

```bash
# Clone project
cd body-size-ai

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

## 📊 Training Model

```bash
# Tạo synthetic data
python data/synthetic/generate_synthetic.py

# Train model
python -m src.models.train
```

## 🌐 Chạy API

```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

API sẽ chạy tại: http://localhost:8000

## 📝 API Endpoints

### POST /predict
Upload ảnh và thông tin để nhận đề xuất size.

**Request:**
```json
{
  "image": "base64_encoded_image",
  "height": 170,
  "weight": 65,
  "gender": "male",
  "brand": "uniqlo"
}
```

**Response:**
```json
{
  "success": true,
  "predicted_size": "M",
  "confidence": 0.85,
  "measurements": {
    "chest": 96,
    "waist": 78,
    "hip": 94
  },
  "alternative_sizes": ["S", "L"]
}
```

### GET /brands
Lấy danh sách brand được hỗ trợ.

### GET /health
Health check endpoint.

## 🔧 Yêu cầu ảnh đầu vào

- Ảnh chụp đứng thẳng, toàn thân
- Định dạng: JPG, PNG
- Kích thước tối thiểu: 640x480
- Trang phục vừa vặn (không quá rộng)

## 📈 Độ chính xác

- Pose detection: ~95% (với ảnh đạt yêu cầu)
- Size prediction: ~80-85% (với synthetic data)

## 📄 License

MIT License
