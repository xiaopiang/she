from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta


# 電影模型
class Movie(models.Model):
    title = models.CharField(max_length=255)
    poster_url = models.CharField(max_length=500, null=True, blank=True)
    is_showing = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=0)  # 電影時長（分鐘）
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-is_showing', 'title']


# 影城模型
class Theater(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    total_seats = models.IntegerField(default=150)  # 設定預設值 150

    def __str__(self):
        return self.name


# 放映時間
class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='showtimes')
    start_time = models.DateTimeField()
    

    def __str__(self):
        return f"{self.movie.title} - {self.theater.name} - {self.start_time}"

    class Meta:
        ordering = ['start_time']


# 影城座位
class Seat(models.Model):
    ROW_CHOICES = [(chr(64+i), chr(64+i)) for i in range(1, 27)]  # A-Z
    
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=1, choices=ROW_CHOICES)
    number = models.IntegerField()

    class Meta:
        unique_together = ('theater', 'row', 'number')

    def __str__(self):
        return f"{self.row}{self.number} - {self.theater.name}"


# **訂單模型**
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=10,
        choices=[
            ("pending", "待付款"),
            ("paid", "已付款"),
            ("cancelled", "已取消")
        ],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    merchant_id = models.CharField(max_length=50,null=True,blank=True)        # 特店編號    (這些是會員支付後綠界回傳的交易資訊，管理帳戶可能會用到)
    merchant_tradeNo = models.CharField(max_length=50,null=True,blank=True)   # 特店交易編號    
    rtn_msg = models.CharField(max_length=20,null=True,blank=True)           # 交易訊息(成功或失敗)                             
    payment_date = models.DateTimeField(null=True,blank=True)                # 付款時間(yyyy/MM/dd HH:mm:ss)
    trade_date = models.DateTimeField(null=True,blank=True)                   # 特店選擇的付款方式     
    payment_type = models.CharField(max_length=50,null=True,blank=True)      # 訂單成立時間(yyyy/MM/dd HH:mm:ss)                
     

    def __str__(self):
        return f"訂單 #{self.id} - {self.user.username} ({self.status})"


# **座位預訂**
class SeatReservation(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name="reservations")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="reservations")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # ✅ 允許 NULL
    status = models.CharField(
        max_length=10,
        choices=[("available", "可選"), ("reserved", "已預訂"), ("sold", "已售出")],
        default="available"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("showtime", "seat")  # 確保同場次內座位不會被重複預訂

    def __str__(self):
        return f"{self.seat} - {self.showtime} ({'已預訂' if self.user else '可選'})"

# **退款申請**
class RefundRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refund_requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[
            ("pending", "待處理"),
            ("approved", "已批准"),
            ("rejected", "已拒絕")
        ],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"退款申請 #{self.id} - {self.user.username} ({self.status})"
  
# **帳號模型**      
class Members(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    idNumber = models.CharField(max_length=20, unique=True, verbose_name="身分證字號")
    birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    # mail = models.EmailField(unique=True)
    # password = models.CharField(max_length=128)  # 密碼儲存（可之後使用 hash）
    # is_verified = models.BooleanField(default=False)  # 信箱驗證欄位（可選）

    def __str__(self):
        return f"{self.user} - ({self.name})"