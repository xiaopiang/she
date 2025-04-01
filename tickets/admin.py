from django.contrib import admin
from .models import Movie, Showtime, Seat, Order, RefundRequest,Theater
#from .utils import send_refund_email  # 確保這個函數在 utils.py 中

# 🎬 電影管理
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "duration", "is_showing")  # 顯示欄位
    search_fields = ("title",)  # 可搜尋電影名稱
    list_filter = ("is_showing",)  # 篩選是否上映

# 🎟️ 放映場次管理
@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "theater", "start_time")  # 顯示欄位
    search_fields = ("movie__title",)  # 可搜尋電影名稱
    list_filter = ("theater", "start_time")  # 篩選影廳與時間

# 🪑 座位管理
@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("id", "theater", "row", "number")  # 顯示欄位
    search_fields = ("theater__name", "row", "number")  # 可搜尋影廳、座位
    list_filter = ("theater",)  # 依影廳篩選

# 🛒 訂單管理
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "showtime", "total_price", "status", "created_at")
    list_filter = ("status",)  # 訂單狀態篩選
    search_fields = ("user__username",)  # 可搜尋用戶名稱
    actions = ["mark_as_paid", "mark_as_cancelled"]

    @admin.action(description="標記為已付款")
    def mark_as_paid(self, request, queryset):
        queryset.update(status="paid")

    @admin.action(description="標記為已取消")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status="cancelled")

# 💰 退款管理
@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "status", "created_at")
    list_filter = ("status",)  # 退款狀態篩選
    search_fields = ("user__username", "order__id")  # 搜尋用戶或訂單
    actions = ["approve_refund", "reject_refund"]  # 添加管理操作

    @admin.action(description="批准退款")
    def approve_refund(self, request, queryset):
        for refund in queryset:
            refund.status = "approved"
            refund.order.status = "refunded"  # 讓訂單狀態同步變更
            refund.order.save()
            refund.save()
            #send_refund_email(refund.user.email, refund.order.id, "已批准")

    @admin.action(description="拒絕退款")
    def reject_refund(self, request, queryset):
        for refund in queryset:
            refund.status = "rejected"
            refund.save()
            #send_refund_email(refund.user.email, refund.order.id, "已拒絕")
            

admin.site.register(Theater)