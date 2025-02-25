
class Config:
    DATABASE = {
        'dbname': 'authentication_python',
        'user': 'postgres',
        'password': 'thanhluan1303',  # Đổi thành mật khẩu đúng
        'host': 'localhost',
        'port': 5432  # Sửa thành 5432 nếu cần
    }
    JWT_SECRET_KEY = '74678234623879642398746283974623987642398746239874623987649823764923876492837649238764289736'  # Khóa từ code cũ