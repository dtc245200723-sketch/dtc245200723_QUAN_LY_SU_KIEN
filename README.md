# Hệ thống Quản lý Sự kiện

Dự án triển khai website quản lý sự kiện bằng Django, PostgreSQL, Nginx, Prometheus, Grafana, Loki và Promtail. Các dịch vụ được cấu hình để chạy bằng Docker Compose.

## Tổng quan

Hệ thống bao gồm:

- Ứng dụng Django cho phép xem sự kiện, đăng ký tham dự, quản lý vé và quản trị website.
- PostgreSQL làm cơ sở dữ liệu.
- pgAdmin để quản trị PostgreSQL.
- Nginx làm reverse proxy, sử dụng chứng thư TLS tự ký cho môi trường thử nghiệm.
- Prometheus và Grafana để thu thập, hiển thị metrics.
- Metrics từ Django và PostgreSQL được cung cấp cho Prometheus.
- Loki và Promtail để tập trung log.
- Các mạng Docker `frontend` và `backend` để phân tách kết nối dịch vụ.

## Yêu cầu trước khi chạy

- Docker Desktop hoặc Docker Engine có hỗ trợ Docker Compose V2.
- OpenSSL để tạo chứng thư TLS cục bộ.
- Mở Docker Desktop và chờ Docker Engine ở trạng thái đang chạy.

## Cài đặt và khởi chạy

1. Tạo tệp môi trường trong PowerShell:

```powershell
Copy-Item .env.example .env
```

Nếu đã có `.env`, giữ lại tệp hiện tại thay vì ghi đè. Thay các mật khẩu mẫu và Django secret bằng giá trị mạnh, riêng biệt. Không chia sẻ hoặc commit `.env` lên Git.

2. Tạo chứng thư tự ký trong thư mục gốc dự án:

```powershell
New-Item -ItemType Directory -Force nginx\certs
openssl req -x509 -nodes -newkey rsa:2048 -keyout nginx\certs\server.key -out nginx\certs\server.crt -days 365 -subj "/CN=localhost"
```

3. Kiểm tra cấu hình rồi khởi chạy các dịch vụ:

```powershell
docker compose config -q
docker compose up --build -d
```

4. Áp dụng migration và nạp sự kiện minh họa (lệnh nạp có thể chạy lặp lại):

```powershell
docker compose exec web python manage.py migrate
docker compose exec web python manage.py load_sample_data
```

Lệnh tạo bốn sự kiện theo nội dung mẫu cùng các lượt đăng ký và vé minh họa. Tài khoản khách mẫu dùng email `example.invalid`, mật khẩu đăng nhập bị vô hiệu hóa và không thể dùng để đăng nhập. Các số liệu trên tổng quan được tính từ dữ liệu thực tế trong PostgreSQL, không gán cứng.

5. Kiểm tra trạng thái và log:

```powershell
docker compose ps
docker compose logs -f web db nginx
```

## Địa chỉ truy cập

- Website qua HTTPS: [https://localhost:8443](https://localhost:8443)
- Tổng quan hệ thống: [https://localhost:8443/dashboard/](https://localhost:8443/dashboard/)
- Danh sách sự kiện: [https://localhost:8443/#events](https://localhost:8443/#events)
- Đăng ký tài khoản: [https://localhost:8443/signup/](https://localhost:8443/signup/)
- Đăng nhập website: [https://localhost:8443/login/](https://localhost:8443/login/)
- Đăng nhập quản trị Django: [https://localhost:8443/admin/](https://localhost:8443/admin/)
- pgAdmin: [http://localhost:5050](http://localhost:5050)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3000](http://localhost:3000)
- Loki API (kiểm tra cục bộ): [http://localhost:3100](http://localhost:3100)

Trình duyệt sẽ cảnh báo chứng thư vì đây là TLS tự ký. Chỉ chấp nhận cảnh báo này cho môi trường thử nghiệm cục bộ.

Cổng HTTPS mặc định của website là `8443`; cổng HTTP `80` sẽ chuyển hướng đến `https://localhost:8443`. Nếu thay đổi cổng HTTPS, cập nhật đồng bộ `NGINX_HTTPS_PORT` và `DJANGO_CSRF_TRUSTED_ORIGINS` trong `.env`, đồng thời sửa cổng chuyển hướng trong `nginx/nginx.conf`.

## Hướng dẫn đăng nhập và sử dụng website

### Đăng ký và đăng nhập tài khoản

1. Mở [trang tạo tài khoản](https://localhost:8443/signup/), nhập tên đăng nhập, họ tên, email và mật khẩu, sau đó chọn **Tạo tài khoản**. Mật khẩu cần đáp ứng quy tắc của Django (ít nhất 8 ký tự, không quá phổ biến hoặc chỉ gồm chữ số).
2. Website tự đăng nhập sau khi đăng ký thành công. Nếu đã có tài khoản, mở [trang đăng nhập](https://localhost:8443/login/), nhập tên đăng nhập và mật khẩu rồi chọn **Đăng nhập**.
3. Dùng nút **Đăng xuất** trên thanh điều hướng để kết thúc phiên làm việc. Nếu không đăng nhập được ở `/admin/`, hãy đặt lại mật khẩu theo hướng dẫn bên dưới; mật khẩu của tài khoản website và tài khoản dịch vụ không nhất thiết giống nhau.

### Xem, tìm kiếm và đăng ký sự kiện

1. Mở [danh sách sự kiện](https://localhost:8443/#events), nhập từ khóa theo tên, mã sự kiện, địa điểm hoặc thể loại rồi chọn **Tìm kiếm**.
2. Chọn **Xem chi tiết** trên thẻ sự kiện để xem thời gian, địa điểm, sức chứa và hạn đăng ký.
3. Đăng nhập hoặc tạo tài khoản, sau đó chọn **Đăng ký tham dự** và điền thông tin người tham dự. Email lấy từ tài khoản. Khi đăng ký thành công, hệ thống tạo vé điện tử và hiển thị mã vé.
4. Mở **Đăng ký tham dự** để xem lịch sử đăng ký; mở **Vé của tôi** để xem mã vé hoặc chọn **In vé**. Trang **Cài đặt** cho phép cập nhật họ tên và email.

### Tạo và quản lý sự kiện (staff)

Chỉ tài khoản có quyền **staff** trở lên mới tạo, sửa hoặc xóa sự kiện. Đăng nhập tài khoản staff trên website:

1. Chọn **Tạo sự kiện** trên thanh điều hướng hoặc mở `/event/create/`.
2. Điền tên sự kiện, mô tả, thể loại, ngày giờ bắt đầu, địa điểm và sức chứa. Có thể nhập mã sự kiện; nếu để trống, hệ thống tự tạo mã. Ngày giờ kết thúc và hạn đăng ký có thể để trống nếu không cần đặt.
3. Chọn **Lưu sự kiện**. Từ trang chi tiết sự kiện, staff có thể chọn **Chỉnh sửa** hoặc **Xóa**. Xóa sự kiện là thao tác không thể hoàn tác và cũng xóa các lượt đăng ký/vé liên quan.
4. Mục **Quản lý đăng ký** cho phép lọc theo sự kiện/trạng thái hoặc tìm theo tên người tham dự, email, tên sự kiện và mã vé. Mục **Báo cáo** hiển thị số liệu đăng ký và tỷ lệ lấp đầy.

### Tài khoản đăng nhập và phân quyền

Tài khoản khách tự đăng ký qua `/signup/`. Để tạo tài khoản quản trị Django trong container web, chạy tại thư mục gốc dự án:

```powershell
docker compose exec web python manage.py createsuperuser
```

Đăng nhập Django Admin tại [https://localhost:8443/admin/](https://localhost:8443/admin/) bằng **tên đăng nhập** và mật khẩu quản trị (không đăng nhập bằng email). Tài khoản staff có thể quản lý sự kiện và đăng ký trên website; superuser cũng có quyền truy cập Django Admin.

Muốn cấp quyền staff cho tài khoản đã tạo: đăng nhập Django Admin bằng superuser, mở **Authentication and Authorization → Users**, chọn người dùng, bật **Staff status**, rồi lưu. Chỉ bật quyền này cho người cần quản trị nội dung.

Nếu quên mật khẩu của một tài khoản Django, đặt lại từ PowerShell:

```powershell
docker compose exec web python manage.py changepassword admin
```

Thay `admin` bằng tên đăng nhập cần đặt lại. Nhập mật khẩu mới hai lần theo lời nhắc. Không ghi mật khẩu vào README, không gửi mật khẩu qua chat và không đưa thông tin trong `.env` lên Git.

### Đăng nhập các dịch vụ giám sát

- **pgAdmin** (`http://localhost:5050`): đăng nhập bằng `PGADMIN_DEFAULT_EMAIL` và `PGADMIN_DEFAULT_PASSWORD` trong `.env`. Khi tạo kết nối tới PostgreSQL trong Docker, dùng host `db`, cổng `5432` và thông tin `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` trong cùng tệp.
- **Prometheus** (`http://localhost:9090`): giao diện truy vấn metrics không yêu cầu đăng nhập trong cấu hình cục bộ. Mở **Status → Targets** để kiểm tra trạng thái thu thập dữ liệu.
- **Grafana** (`http://localhost:3000`): đăng nhập bằng `GRAFANA_ADMIN_USER` và `GRAFANA_ADMIN_PASSWORD` trong `.env`. Mở **Dashboards → Event Monitoring Dashboard** để xem biểu đồ; chọn **Explore** và datasource Loki để truy vấn log.
- **Loki API** (`http://localhost:3100`): endpoint phục vụ kiểm tra API cục bộ, không phải giao diện đăng nhập hay trang xem log. Xem log thuận tiện qua Grafana Explore.

## Chức năng chính

- Xem danh sách và thông tin chi tiết sự kiện.
- Tìm kiếm sự kiện theo tên, mã, địa điểm hoặc thể loại.
- Xem dashboard thống kê từ dữ liệu thật trong PostgreSQL.
- Đăng ký, đăng nhập và đăng xuất.
- Nhân viên (staff) tạo, sửa và xóa sự kiện.
- Người dùng đăng ký tham dự và nhận mã vé.
- Xem lịch sử đăng ký, chi tiết/in vé và cập nhật thông tin tài khoản.
- Nhân viên quản lý, tìm kiếm và lọc đăng ký; xem báo cáo sự kiện.
- Quản trị dữ liệu qua Django Admin.

## Kiểm tra giám sát

- Mở [Prometheus Targets](http://localhost:9090/targets) và kiểm tra các job `prometheus`, `node-exporter`, `cadvisor`, `postgres-exporter`, `nginx-exporter` và `django-web` ở trạng thái `UP`.
- Grafana tự động cấu hình datasource Prometheus và Loki.
- Dashboard **Event Monitoring Dashboard** có các panel CPU, bộ nhớ, lưu lượng Nginx, kết nối PostgreSQL, tốc độ request Django và trạng thái scrape.
- Prometheus lấy metrics Django tại `/metrics` qua mạng nội bộ Docker; endpoint này không được proxy ra bên ngoài qua Nginx.
- Nginx exporter lấy metrics từ `stub_status` trên cổng container nội bộ `8081`.

## Kiểm tra log bằng LogQL

Trong Grafana, mở **Explore**, chọn datasource Loki và chạy các truy vấn sau:

```logql
{compose_service="web"}
{compose_service="web"} |= "ERROR"
{compose_service="nginx"} |~ "\" 5[0-9][0-9] "
sum by (compose_service) (count_over_time({compose_service=~".+"}[5m]))
```

Truy vấn cuối đếm số dòng log trong 5 phút gần nhất, nhóm theo dịch vụ. Các truy vấn chỉ trả kết quả khi Promtail thu thập được log từ container.

## Kiểm thử tự động và kiểm tra cấu hình

Chạy sau khi khởi động các dịch vụ:

```powershell
docker compose exec web python manage.py test events
docker compose exec nginx nginx -t
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml
curl.exe -k https://localhost:8443/health/
```

Kết quả mong đợi: Django test thành công, Nginx báo cấu hình hợp lệ, Prometheus xác nhận cấu hình đúng và health endpoint trả HTTP 200.

## Các biện pháp hardening

- Django chạy bằng tài khoản không phải root trong container.
- Thông tin nhạy cảm được cấu hình qua `.env`; tệp này bị loại khỏi Git.
- Mạng `backend` tách PostgreSQL, pgAdmin, exporters và dịch vụ logging khỏi đường truy cập web bên ngoài; mạng `frontend` chỉ kết nối các dịch vụ cần phục vụ hoặc giám sát web.
- Chỉ tài khoản staff được tạo, sửa hoặc xóa sự kiện.
- Nginx là điểm truy cập web qua HTTP/HTTPS.
- Nginx thiết lập các security headers.
- Các cổng host của PostgreSQL, pgAdmin, Prometheus, Grafana, Loki và exporters được bind vào loopback nếu có publish.
- Endpoint metrics trạng thái Nginx chỉ truy cập được trong mạng Docker nội bộ.
- Chứng thư tự ký chỉ dành cho thử nghiệm cục bộ.

## Báo cáo và ảnh minh chứng

Bản dự thảo báo cáo tiếng Việt nằm tại [docs/Bao_cao_de_tai_26_quan_ly_su_kien.docx](docs/Bao_cao_de_tai_26_quan_ly_su_kien.docx), kèm sơ đồ kiến trúc. Báo cáo có các vị trí chờ chèn ảnh chụp; cần thay bằng ảnh thực tế sau khi khởi chạy và kiểm thử hệ thống.

Nên chụp ảnh website, pgAdmin đã kết nối PostgreSQL, các Prometheus target ở trạng thái UP, dashboard Grafana, ít nhất ba truy vấn LogQL có kết quả và security headers của Nginx. Không để lộ `.env`, mật khẩu hoặc khóa riêng trong ảnh hay trên GitHub.

## Xử lý sự cố

- PostgreSQL chưa sẵn sàng: kiểm tra `docker compose ps` và chờ service `db` chuyển sang healthy.
- Ứng dụng không khởi động: xem log bằng `docker compose logs web`.
- Grafana chưa có dữ liệu: kiểm tra Prometheus Targets và chờ Prometheus scrape metrics.
- Loki không có log: kiểm tra log Promtail, kết nối tới Loki và nhãn `compose_service`.
- Lỗi HTTPS: xác nhận đã tạo `nginx\certs\server.crt` và `nginx\certs\server.key`.
- Docker không chạy: mở Docker Desktop, chờ Docker Engine báo đang chạy, rồi kiểm tra bằng `docker info`.

## Repository GitHub

Tên repository dự kiến: `dtc245200723_QUAN_LY_SU_KIEN`.
