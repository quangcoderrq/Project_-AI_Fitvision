# Hướng Dẫn Cài Đặt và Chạy Dự Án Body Size AI

Dự án này sử dụng Python (FastAPI cho Backend) và **React (Vite) cho Frontend**. Dự án đã được chuyển đổi hoàn toàn sang React với giao diện Glassmorphism hiện đại, hỗ trợ Dark/Light mode và tương thích tối đa với cả di động (sẵn sàng chuyển đổi sang React Native).

Dưới đây là các bước chi tiết để cài đặt và khởi chạy dự án trên máy tính của bạn.

---

## Bước 1: Yêu cầu hệ thống
- Máy tính cần cài đặt sẵn **Python** (phiên bản 3.8 trở lên). 
- (Bạn có thể kiểm tra bằng cách mở Terminal/Command Prompt và gõ `python --version`).

---

## Bước 2: Khởi tạo môi trường và cài đặt thư viện

Mở Terminal (hoặc PowerShell / Command Prompt) và di chuyển vào thư mục `backend` của dự án:

```bash
cd d:\chatbot\chat\body-size-ai\backend
```

### 1. Tạo môi trường ảo (Virtual Environment)
Việc tạo môi trường ảo giúp các thư viện của dự án này không bị xung đột với các dự án Python khác trên máy của bạn.

```bash
python -m venv venv
```

### 2. Kích hoạt môi trường ảo
Trên Windows:
```bash
venv\Scripts\activate
```
*(Nếu bạn dùng Mac/Linux, lệnh sẽ là: `source venv/bin/activate`)*

Sau khi kích hoạt, bạn sẽ thấy chữ `(venv)` hiện ở đầu dòng lệnh.

### 3. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

---

Dự án cần có model máy học (`.pkl` hoặc `.joblib`) để dự đoán size. Nếu trong thư mục `backend/models/` chưa có file model nào, bạn cần đảm bảo Terminal đang ở thư mục `backend` và chạy 2 lệnh sau để tạo dữ liệu giả lập (synthetic data) và train model:

```bash
# 1. Tạo dữ liệu giả lập (sẽ lưu vào backend/data/synthetic/)
python data/synthetic/generate_synthetic.py

# 2. Huấn luyện model (sẽ lưu vào backend/models/)
python -m src.models.train
```

Sau khi chạy xong, trong thư mục `models/` sẽ xuất hiện các file model (như `body_regressor.joblib` và `feature_scaler.joblib`).

---

Vẫn trong Terminal tại thư mục `backend` (đã kích hoạt `venv`), bạn chạy lệnh sau để bật Server FastAPI:

```bash
python -m uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000
```
- `--reload`: Giúp tự động cập nhật lại server mỗi khi bạn sửa code Python.

---

## Bước 5: Lựa chọn cách khởi chạy Frontend

Dự án hỗ trợ 2 cách chạy Frontend tùy thuộc vào nhu cầu phát triển hoặc triển khai thực tế:

### Cách 1: Chạy Frontend ở chế độ Phát triển (Development Mode) - KHUYÊN DÙNG khi sửa code
Mở một **Terminal mới**, di chuyển vào thư mục `frontend-react` và khởi động React dev server:
```bash
cd frontend-react
npm run dev
```
- Server React sẽ khởi động và cung cấp link truy cập: 👉 **[http://localhost:5173](http://localhost:5173)**
- Cách này cho phép **Hot Reload** (tự động cập nhật giao diện ngay lập tức khi bạn lưu code React).

### Cách 2: Chạy trực tiếp qua Backend FastAPI (Production Mode)
Nếu bạn muốn chạy toàn bộ ứng dụng (cả Backend lẫn Frontend) trên cùng một cổng duy nhất (8000), bạn hãy build dự án React:
1. Di chuyển vào thư mục `frontend-react` và thực hiện build:
   ```bash
   cd d:\chatbot\chat\body-size-ai\frontend-react
   npm run build
   ```
   *Lệnh này sẽ biên dịch mã nguồn React thành các file tĩnh được tối ưu hóa trong thư mục `frontend-react/dist`.*

2. Khởi chạy Backend FastAPI (phải đứng ở thư mục `backend` như ở Bước 4):
   ```bash
   cd d:\chatbot\chat\body-size-ai\backend
   python -m uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000
   ```

3. Mở trình duyệt và truy cập trực tiếp địa chỉ: 👉 **[http://localhost:8000](http://localhost:8000)**
   *FastAPI sẽ tự động phát hiện mã nguồn React đã được build tại `frontend-react/dist` và phục vụ trực tiếp giao diện React cho bạn.*

---

## Bước 6: Sử dụng ứng dụng trên trình duyệt & Tích hợp (Third-Party Integration)

Dự án này là một **Widget Độc Lập**, được thiết kế để nhúng vào các trang bán hàng của đối tác (ví dụ qua thẻ `<iframe>`).

### Cách 1: Sử dụng giao diện Widget thuần túy
Truy cập vào **[http://localhost:5173](http://localhost:5173)** (nếu chạy Cách 1) hoặc **[http://localhost:8000](http://localhost:8000)** (nếu chạy Cách 2). Tại đây bạn có thể:
1. Chọn chuyển đổi Light/Dark Mode ở góc trên bên phải.
2. Theo dõi **Hướng dẫn động** tự thay đổi tùy theo loại sản phẩm.
3. Tải lên ảnh, nhập thông tin cá nhân và test chức năng nhận diện.

### Cách 2: Test giả lập Tích Hợp (Khuyên dùng để thấy bức tranh toàn cảnh)
Để xem cách một Shop thời trang bên thứ 3 nhúng ứng dụng của bạn vào trang web của họ:
1. Đảm bảo Backend (FastAPI ở port 8000) đang chạy.
2. Mở thư mục chứa mã nguồn dự án: `d:\chatbot\chat\body-size-ai\`
3. Click đúp chuột để mở file `embed-demo.html` bằng trình duyệt (Chrome/Edge/Firefox).
4. File Demo này mô phỏng một trang bán hàng, chứa một nút **"✨ Không biết chọn size? Hỏi AI ngay!"**.
5. Khi bạn bấm vào, Widget AI sẽ bật lên dưới dạng iframe, phân tích ảnh, đưa ra kết quả, và **tự động bắn kết quả ra ngoài (thông qua postMessage)** để Shop áp dụng thẳng size vào Giỏ hàng của họ!

---

## Bước 7: Hướng Dẫn Chạy & Thử Nghiệm Trên Ứng Dụng Di Động (React Native - Expo)

Chúng ta đã xây dựng một bộ thư viện độc lập SDK di động (`BodySizeWidget.tsx`) cùng một trang bán hàng giả lập cực kỳ sang trọng tại thư mục `mobile-app` sử dụng **React Native (Expo)**. Bạn có thể dễ dàng chạy và thử nghiệm trực tiếp tính năng AI đo size trên điện thoại thật của mình!

### 1. Chuẩn bị trên Điện thoại di động
*   Lên kho ứng dụng tải và cài đặt ứng dụng miễn phí **Expo Go** (có sẵn trên cả App Store của iOS và Google Play Store của Android).
*   **QUAN TRỌNG:** Đảm bảo điện thoại di động và máy tính chạy server của bạn đang kết nối **chung một mạng Wi-Fi**.

### 2. Khởi chạy Backend FastAPI (Hỗ trợ truy cập mạng nội bộ)
Thông thường, khi chạy server nội bộ để test web, ta dùng `--host 127.0.0.1`. Tuy nhiên, để điện thoại thật trong mạng Wi-Fi có thể kết nối được máy tính của bạn, bạn cần chạy FastAPI lắng nghe trên toàn mạng bằng host `0.0.0.0`:
1. Mở Terminal tại thư mục `backend` và đã kích hoạt `(venv)`.
2. Chạy lệnh:
   ```bash
   python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
   ```

### 3. Tìm địa chỉ IP máy tính của bạn
1. Mở một Command Prompt (cmd) hoặc PowerShell mới trên máy tính.
2. Gõ lệnh `ipconfig` và nhấn Enter.
3. Tìm dòng **IPv4 Address** trong phần card mạng Wi-Fi đang kết nối (ví dụ: `192.168.1.15`). Đây chính là địa chỉ IP máy tính của bạn.

### 4. Khởi chạy Ứng Dụng Di Động Expo
1. Mở một Terminal mới độc lập.
2. Di chuyển vào thư mục `mobile-app`:
   ```bash
   cd d:\chatbot\chat\body-size-ai\mobile-app
   ```
3. Chạy lệnh để khởi động Expo Dev Server:
   ```bash
   npm start
   ```
4. Sau vài giây, màn hình Terminal sẽ hiển thị một **Mã QR Code** rất lớn kèm các tùy chọn.

### 5. Quét mã QR để trải nghiệm trên điện thoại thật
*   **Android:** Mở ứng dụng **Expo Go** đã cài đặt, chọn mục "Scan QR Code" và đưa camera quét mã QR trên màn hình máy tính.
*   **iOS (iPhone):** Chỉ cần mở ứng dụng **Camera mặc định** của iPhone, quét mã QR, click vào đường dẫn mở bằng **Expo Go**.
*   Ứng dụng sẽ tự động tải các tài nguyên và khởi chạy trang bán hàng thời trang cao cấp trên điện thoại của bạn!

### 6. Kết nối ứng dụng di động tới Máy chủ AI
1. Khi app thời trang mở lên, click vào **Biểu tượng răng cưa Cài đặt (Settings)** ở góc trên bên phải màn hình.
2. Tại trường **Kết nối Máy chủ AI**, hãy nhập địa chỉ IP máy tính của bạn với cổng 8000 (Ví dụ: `http://192.168.1.15:8000` - thay thế `192.168.1.15` bằng IP thực tế bạn vừa tìm ở mục 3).
3. Đóng cài đặt, chọn nút **"✨ Chọn Size bằng AI"** bên cạnh phần chọn size sản phẩm, và bắt đầu trải nghiệm chụp ảnh thật, gửi AI đo lường cực kỳ mượt mà!

---

## 🛠️ Tính Năng SaaS & Backend Thực Tế (Nâng Cấp)
Hệ thống đã được nâng cấp từ Mock-data lên **Backend thật** tích hợp cơ sở dữ liệu SQLite:
1. **Database SQLite (`fitvision.db`)**: Tự động khởi tạo cấu trúc bảng (`users`, `api_tokens`, `prediction_logs`) khi chạy server FastAPI.
2. **Xác thực JWT (JSON Web Token)**: Cho phép chủ shop đăng ký mới, đăng nhập tài khoản doanh nghiệp. Mật khẩu được mã hóa an toàn bằng thuật toán `pbkdf2_sha256`.
3. **Quản lý API Token**: Mỗi shop có 1 token riêng (`fv_live_...`), có thể tạo lại token mới bất kỳ lúc nào trên Dashboard.
4. **Bảo vệ API `/predict`**: Chặn các request không hợp lệ (trả về lỗi `401 Unauthorized`). Demo công cộng sử dụng một guest token đặc biệt để hoạt động an toàn.
5. **Lịch sử & Thống kê log thật**: Hiển thị bảng danh sách các lượt quét size AI của khách hàng thực tế và sơ đồ băng thông API trực tiếp từ database.

### Chạy thử nghiệm tự động (API Integration Tests)
Để kiểm tra tính ổn định của cơ sở dữ liệu và các API bảo mật, bạn hãy di chuyển vào thư mục `backend` và chạy file script:
```bash
venv\Scripts\python test_db_api.py
```
Script sẽ tự động đăng ký user mới, đăng nhập lấy JWT, kiểm tra bảo mật API prediction và hiển thị kết quả log trực tiếp!

---

## 🛑 Cách tắt Server
Để dừng ứng dụng web hoặc mobile app, bạn quay lại màn hình Terminal tương ứng đang chạy và nhấn tổ hợp phím **`Ctrl + C`**.

Để thoát khỏi môi trường ảo ở Terminal Backend, gõ lệnh:
```bash
deactivate
```

