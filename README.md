<h2 align ="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align ="center">  
   JUNGLE DASH – GAME 2D HÀNH ĐỘNG PHIÊU LƯU
</h2>

<div align ="center">
    <p align ="center">
        <img src="https://github.com/tiennq004/LTM_he_thong_canh_bao_thoi_gian_thuc/blob/main/docs/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="https://github.com/tiennq004/LTM_he_thong_canh_bao_thoi_gian_thuc/blob/main/docs/fitdnu_logo.png" alt="FIT DNU Logo" width="180"/>
        <img src="https://github.com/tiennq004/LTM_he_thong_canh_bao_thoi_gian_thuc/blob/main/docs/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)
</div>

---

📖 1. Giới thiệu game

- Jungle Dash là một trò chơi 2D thuộc thể loại hành động – chạy vô tận (Endless Runner) nơi người chơi điều khiển nhân vật chính Kael Shadowstride vượt qua khu rừng cổ đại đầy nguy hiểm.

- Mục tiêu của trò chơi là giúp nhân vật sống sót càng lâu càng tốt bằng cách né tránh chướng ngại vật, vượt qua cạm bẫy và phản ứng nhanh với các tình huống bất ngờ.

- Game được xây dựng với mục đích:

    - Áp dụng kiến thức về lập trình game 2D
    
    - Tìm hiểu về xử lý ảnh / nhận diện cử chỉ (nếu có tích hợp)
    
    - Phát triển kỹ năng thiết kế giao diện và logic game

- 🎮 Gameplay

    - Người chơi sẽ điều khiển nhân vật Kael Shadowstride thực hiện các hành động:

- 🏃‍♂️ Chạy liên tục trong môi trường rừng

    - ⬆️ Nhảy để né chướng ngại vật

    - ⚡ Né bẫy và tránh kẻ thù

    - 🎯 Tăng điểm theo thời gian sống sót

- 🔥 Đặc điểm nổi bật:

    - Tốc độ game tăng dần → độ khó tăng theo thời gian

    - Gameplay đơn giản nhưng gây nghiện

    - Có thể tích hợp điều khiển bằng cử chỉ (AI / MediaPipe)

    - Hệ thống điểm số và kỷ lục

- 🧑Nhân vật chính

    - ⚔️ Anh Liêm

        - Là một nhà thám hiểm trẻ dũng cảm
    
        - Nhiệm vụ: khám phá khu rừng và sống sót

      - Kỹ năng:

        - Dash (lướt nhanh)
    
        - Nhảy / Nhảy đôi
    
        - Né tránh linh hoạt

- 🖥️Cấu trúc hệ thống

     - Game gồm các thành phần chính:

- 🎨Giao diện (UI)

    - Hiển thị nhân vật, background, chướng ngại vật

    - Hiển thị điểm số, trạng thái game

- 🧠 Game Logic

    - Xử lý va chạm (collision detection)

    - Sinh chướng ngại vật ngẫu nhiên

    - Tăng tốc độ theo thời gian

- 🎮 Điều khiển

    - Bàn phím (Space, Arrow keys)

    - Camera nhận diện cử chỉ

## 🔧 2. Công nghệ & Công cụ sử dụng

- Ngôn ngữ lập trình:![Python Logo](https://www.python.org/static/community_logos/python-logo.png)

- Thư viện chính:

    - Pygame (xây dựng game 2D)

    - OpenCV (xử lý camera)

    - MediaPipe (nhận diện cử chỉ)

    - IDE: VS Code / PyCharm

    - Hệ điều hành: Windows 10/11

## 🚀 3. Hình ảnh các chức năng chính

<p align="center">
  <img src="https://github.com/tiennq004/LTM_he_thong_canh_bao_thoi_gian_thuc/blob/main/docs/giao_dien_server.png" alt="Ảnh 1" width="800"/>
</p> 
<p align="center">
  <em>Hình 1: Giao diện của Server  </em>
</p>

## 📂 4. Các bước cài đặt 

- Bước 1: Chuẩn bị môi trường

  Trước khi chạy game, cần cài đặt các công cụ sau:

    Python 3.9 trở lên

    pip (trình quản lý thư viện Python)

👉 Kiểm tra Python đã cài chưa:

      python --version

- Bước 2: Tải mã nguồn

    Clone project từ GitHub:

      git clone https://github.com/tiennq004/JungleDash.git

    Hoặc tải file .zip và giải nén.

- Bước 3: Di chuyển vào thư mục project

cd JungleDash

- Bước 4: Tạo môi trường ảo (khuyến khích)

👉 Giúp tránh lỗi xung đột thư viện

      python -m venv venv

- Kích hoạt môi trường:

  Windows:

      venv\Scripts\activate

      Mac/Linux:

      source venv/bin/activate

- Bước 5: Cài đặt thư viện

  Cài các thư viện cần thiết:

      pip install pygame opencv-python mediapipe numpy

👉 Nếu project có file requirements.txt:

      pip install -r requirements.txt

🔹 Bước 6: Chạy game

      python main.py

## 🧑‍💻 5. Người thực hiện
- Sinh viên: **Nguyễn Quang Tiến** (MSSV: 1671020318)  
- Lớp: CNTT 16-03 – Đại học Đại Nam  
- Học phần: Lập trình mạng  

© 2025 AIoTLab, Faculty of Information Technology, DaiNam University. All rights reserved.
