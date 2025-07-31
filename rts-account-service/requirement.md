✅ Chức năng chính của profiles service

    Lưu trữ và truy xuất thông tin hồ sơ người dùng:

        Họ tên, email, ảnh đại diện, địa chỉ, số điện thoại, ngày sinh,...

        Thông tin cá nhân có thể hiển thị công khai hoặc riêng tư.

    Cập nhật hồ sơ:

        Cho phép người dùng chỉnh sửa thông tin cá nhân.

        Cập nhật avatar, đổi địa chỉ, cập nhật mô tả bản thân,...

    Tích hợp với dịch vụ Auth (Authentication & Authorization):

        Nhận thông tin userID từ Auth service sau khi đăng nhập.

        Không xử lý đăng nhập / đăng ký trực tiếp, mà dùng ID đã xác thực để truy xuất dữ liệu.

    Lưu lịch sử hoạt động, trạng thái người dùng:

        Trạng thái hoạt động (online, offline, banned,...)

        Log các lần cập nhật hồ sơ.

    Phân quyền hiển thị dữ liệu:

        Ai được xem thông tin nào (ví dụ: bạn bè thấy đầy đủ, người lạ chỉ thấy tên & avatar).

    Quản lý người dùng trong hệ thống phân vai (admin, user, seller,... nếu có):

        Gán vai trò hoặc thông tin chuyên biệt theo vai trò.

📦 Ví dụ thực tế
Tình huống	Vai trò của profiles service
Ứng dụng mạng xã hội	Quản lý bio, ảnh đại diện, liên hệ, follower
E-commerce	Lưu thông tin người mua, người bán, địa chỉ giao hàng
Sàn giao dịch tài chính	Quản lý thông tin xác thực (KYC), hồ sơ tài chính