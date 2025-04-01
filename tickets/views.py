from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.utils.html import strip_tags
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from datetime import timedelta, datetime
import random
import json
import requests
import os
from bs4 import BeautifulSoup

from .models import (
    Movie, Showtime, Seat, SeatReservation, Order, Theater, Members
)
from .forms import RegisterForm, SetPasswordForm
"""""
def sendEmail(request, username):
    try:
        user = User.objects.get(username=username)
        token = str(random.randint(1000, 9999))  # 生成隨機驗證 Token  
        uid = str(user.pk)
        request.session["verify_token"] = token 
        request.session["verify_uid"] = uid         
        verificationLink = f"http://127.0.0.1:8000/tickets/verify/{token}/"  # 生成驗證連結
        print(verificationLink)
        
        subject = "Spotix Cinemas Account Verification"
        message = f"Dear member,\n\nPlease click the link below to verify your account:\n{verificationLink}\nThis link will expire in 30 minutes. Please request another verification if it expires."


        subject = smart_str(subject, encoding='utf-8')
        message = smart_str(message, encoding='utf-8')
        # 發送郵件（不使用 HTML 格式）
        send_mail(subject, message, "your-email@gmail.com", [user.email], fail_silently=False)
        
        return f"A verification email has been sent to {user.email}. Please complete the verification."
        
    except User.DoesNotExist:
        return "User not found, please check the ID number."
    """
def sendEmail(request, username):
    try:
        user = User.objects.get(username=username)
        token = str(random.randint(1000, 9999))  # 生成隨機驗證 Token  
        uid = str(user.pk)
        request.session["verify_token"] = token 
        request.session["verify_uid"] = uid         
        
        # 生成驗證連結
        verificationLink = f"http://127.0.0.1:8000/tickets/verify/{token}/"
        
        # 返回驗證連結
        return f"請點擊以下連結完成驗證：\n{verificationLink}\n此連結將在30分鐘後過期，請盡快完成驗證。"
        
    except User.DoesNotExist:
        return "找不到用戶，請檢查您的帳號信息。"
    
def verifyEmail(request,token):
    session_token = request.session.get("verify_token")
    session_uid = request.session.get("verify_uid")
    
    if "expireTime" in request.COOKIES:        
        expireTime = request.COOKIES["expireTime"]             # 取出存在 cookie 的有效時間，並轉成 datetime 型式 
        expireTime = datetime.strptime(expireTime[:-7],"%Y-%m-%d %H:%M:%S")
        
        if (datetime.now() - expireTime).seconds < 1800 :      # 帳戶驗證連結小於30分鐘(以秒為單位)，皆有效
            if session_token == token:                         # 驗證 Token 是否相同 
                user = User.objects.get(pk=session_uid)
                user.is_active = True                          # 啟用帳戶
                user.save()                             
                messages.success(request,"您的會員網路帳號啟用成功")
                return render(request,"tickets/passwordResetComplete.html")                
                                                
        else:
            messages.error(request,"驗證帳號有效時間已逾時，請重新申請。")
            return render(request,"tickets/passwordResetComplete.html")                
    
    messages.error(request,"驗證帳號有效時間已逾時，請重新申請。")
    return render(request,"tickets/passwordResetComplete.html")
    
        
def resendVerify(request):
    if request.method == "POST":
        mail = request.POST.get("mail")
        try:
            user = User.objects.get(email=mail)
            if user.is_active:  # 如果帳戶已驗證
                messages.error(request,"您的帳號已啟用，請直接登入")
                return render(request,"tickets/login.html")
            
            else:                   
                username = user.username
                res = sendEmail(request,username)
                messages.success(request,"驗證信已寄出!請至信箱點擊驗證後，再登入!")                
                response = render(request,"tickets/resendVerify.html",locals())
                response.set_cookie("expireTime",datetime.now())         
                return response
                
        except User.DoesNotExist:
            messages.error(request,"查無此帳號，請確認帳號是否輸入正確")
            return render(request,"tickets/resendVerify.html")
    return render(request,"tickets/resendVerify.html")

def forgetPassword(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        idNumber = request.POST.get('idNumber')           
        try:
            member = Members.objects.get(idNumber=idNumber)  
            request.session["user_id"] = member.user_id          
            if  name==member.name and phone==member.phone:
                return redirect("tickets:reset_password")            
            elif name!=member.name:                
                messages.error(request,"姓名錯誤!")
            else:
                messages.error(request,"手機號碼錯誤!")
            return render(request,"tickets/forgetPassword.html",locals())
        except Members.DoesNotExist:            
            messages.error(request,"身分證字號錯誤!")
            return render(request,"tickets/forgetPassword.html",locals())            
    return render(request,"tickets/forgetPassword.html")


def reset_password(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("tickets:forgetPassword")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request,"用戶不存在!")
        
    if request.method == "POST":
        form = SetPasswordForm(request.POST)
        if form.is_valid():               
            newPassword = form.cleaned_data.get("newPassword")        
            confirmPassword = form.cleaned_data.get("confirmPassword")     
            user.set_password(newPassword)                 
            user.save()         
            messages.success(request,"密碼變更成功!請重新登入")                       
            return render(request,"tickets/reset_password.html")
        else:            
            return render(request,"tickets/reset_password.html",{"form":form})
    
    form = SetPasswordForm()
    return render(request,"tickets/reset_password.html",{"form":form})

@login_required
def member_data(request):
    user = request.user 
    member = Members.objects.get(user_id=user.id)
    print(member)
    if request.method =="POST":
        newname = request.POST["newname"]
        newphone = request.POST["newphone"]
        orignal_mail = request.POST["orignal_mail"]
        new_mail = request.POST["new_mail"]
        
        if not (newname or newphone or orignal_mail or new_mail):
            return JsonResponse({"status":"error","message":"請輸入欲更改資料!"})
        if orignal_mail and new_mail:
            if orignal_mail != request.user.email:
                return JsonResponse({"status":"error","message":"原始帳號輸入錯誤，請再次確認!"})       
            else:
                request.user.email = new_mail
                request.user.save()
        elif orignal_mail or new_mail:
            return JsonResponse({"status":"error","message":"請輸入完整的原始帳號和新帳號!"})
                
        if newname:
            request.user.username = newname
            request.user.save()
        if newphone:
            member.phone = newphone                    
            member.save()
        send_mail(
        "票點影城【會員資料修改通知信】",
        f"親愛的會員 您好:\n於{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 透過會員資料修改服務更新了您的會員資料",
        "cat073117@gmail.com",  # ✅ 寄件人 email 字串
    [user.email],
    fail_silently=False
        return JsonResponse({"status":"success","message":"會員資料更新成功!"})
          
    return render(request,"tickets/member_data.html",locals())
 

@login_required  
def change_password(request):
    user = request.user 
    if request.method =="POST":
        password = request.POST.get("newPassword")
        confirmPassword = request.POST.get("confirmPassword")  
        if password != confirmPassword:                
            return JsonResponse({"status":"success","message":"輸入密碼不一致，請再次確認"})
            
        elif not (password or confirmPassword):
            return JsonResponse({"status":"error","message":"請輸入密碼!"})
            
        else:
            user.set_password(password)                 
            user.save()  
            login(request,user)       
            send_mail(
                "票點影城【變更密碼確認信】",
                f"親愛的會員 您好:\n於{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 透過密碼修改服務已成功變更",
                "cat073117@gmail.com",  # ✅ 正確寄件人 email 字串
                [user.email],
                fail_silently=False
            )                        
            return JsonResponse({"status":"success","message":"密碼已成功變更"})  
    return render(request,"tickets/change_password.html")



def register_view(request):
    if request.method == "POST":   
        form = RegisterForm(request.POST)
        if form.is_valid():            
            name = form.cleaned_data.get("name")
            username = form.cleaned_data.get("nickname")
            idNumber = form.cleaned_data.get("idNumber")
            birth = form.cleaned_data.get("birth")
            phone = form.cleaned_data.get("phone")
            mail = form.cleaned_data.get("mail")
            password = form.cleaned_data.get("password")        
            
            user  = User.objects.create_user(username=username,email=mail,password=password)            
            user.is_staff = False
            user.is_active = False
            user.save()
            
            password = user.password
            member=Members(user=user,name = name,idNumber=idNumber,birth=birth,phone=phone)                  
            member.save()             
            
            res = sendEmail(request,username)            
            response = render(request,'tickets/login.html',locals())
            response.set_cookie("expireTime",datetime.now())          # 設置驗證連結有效時間的初始值            
            request.session["user_id"] = member.user_id 
            return response
                        
        else:           
            return render(request,"tickets/register.html",{"form":form})   
                 
    return render(request,"tickets/register.html")

def login_view(request):
    if request.method == "POST":    
        mail = request.POST['mail']
        password = request.POST['password']
        try:
            user = User.objects.get(email=mail)
            if user.is_active == False:
                messages.error(request,"帳號未啟用，請先至信箱驗證")
                return render(request,"tickets/login.html",locals())
            
            user = authenticate(request,username=user.username,password=password) 
            if user:
                login(request,user)
                next_url = request.POST.get("next")
                if next_url:
                    return redirect(next_url)                
                return redirect("tickets:member_index")
                
            else:
                messages.error(request,"登入失敗:請確認密碼是否正確!")
                response = render(request,"tickets/login.html",locals())                
                return response
            
        except User.DoesNotExist:
            messages.error(request,"查無此帳號，請先註冊")
            return render(request,"tickets/login.html")       
    return render(request,"tickets/login.html")

def logout_view(request):    
    logout(request)
    response=redirect("tickets:movie_list")                 
    response.delete_cookie("expireTime")          
    return response

def open_note(request):
    return render(request, 'tickets/openNote.html')

def open_info(request):
    return render(request, 'tickets/openInfo.html')

#電影名稱
def fetch_vieshow_movies():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    url = "https://www.vscinemas.com.tw/vsweb/film/index.aspx"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    movies = []
    for item in soup.select('.movieList li'):
        title = item.select_one('.infoArea h2').text.strip()
        link = item.select_one('a')['href']
        movies.append({
            'title': title,
            'link': f"https://www.vscinemas.com.tw{link}",
        })
    return movies

def select_tickets(request, showtime_id):
    try:
        showtime = Showtime.objects.get(id=showtime_id)
        return render(request, "tickets/select_tickets.html", {"showtime": showtime})
    except Showtime.DoesNotExist:
        return render(request, "tickets/error.html", {"message": "場次不存在"}, status=404)

def movie_list(request):
    """顯示正在上映的電影列表(主頁面)"""
    movies = Movie.objects.filter(is_showing=True)
    return render(request, 'tickets/base.html', {'movies': movies})

def get_movies_json(request):
    """提供電影列表的API接口，用於動態更新下拉選單"""
    movies = Movie.objects.filter(is_showing=True)
    movie_list = []
    
    for movie in movies:
        movie_list.append({
            'id': movie.movie_id,
            'title': movie.title
        })
    
    return JsonResponse({'movies': movie_list})
    
# Stripe設置
# stripe.api_key = settings.STRIPE_SECRET_KEY


# 放映場次列表
def showtimes_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    showtimes = Showtime.objects.filter(
        movie=movie,
        start_time__gte=timezone.now()
    ).order_by('start_time')
    
    return render(request, 'tickets/select_tickets.html', {
        'movie': movie,
        'showtimes': showtimes
    })

    
# 座位選擇
# @login_required
def select_seats(request, showtime_id):
    try:
        showtime = Showtime.objects.get(id=showtime_id)

        # 取得該場次的所有座位（該影廳）
        theater_seats = Seat.objects.filter(theater=showtime.theater)

        # 建立座位行列表
        seat_rows = {}
        available_count = 0  # 剩餘可選座位

        for seat in theater_seats:
            if seat.row not in seat_rows:
                seat_rows[seat.row] = []

            # 檢查該場次該座位是否已被預訂/售出
            reservation = SeatReservation.objects.filter(showtime=showtime, seat=seat).first()
            if reservation:
                status = reservation.status  # 'reserved' 或 'sold'
            else:
                status = 'available'
                available_count += 1  # 計入可選座位

            seat_rows[seat.row].append({
                'id': seat.id,
                'row': seat.row,
                'number': seat.number,
                'status': status
            })

        # 按照行號排序
        sorted_seat_rows = sorted(seat_rows.items(), key=lambda x: x[0])

        return render(request, 'tickets/select_seats.html', {
            'showtime': showtime,
            'seat_rows': sorted_seat_rows,
            'user_reserved_seats': [],
            'available_count': available_count,
            'total_price': request.GET.get("total_price", 0),
            'is_logged_in': request.user.is_authenticated
        })

    except Showtime.DoesNotExist:
        return HttpResponse("找不到指定的場次", status=404)
    except Exception as e:
        return HttpResponse(f"顯示座位時發生錯誤：{str(e)}", status=500)
# 訂單確認
# @login_required
def order_confirmation(request):
    showtime_id = request.GET.get('showtime_id')
    showtime = get_object_or_404(Showtime, id=showtime_id)
    
    # 獲取用戶的座位預訂
    user_reservations = SeatReservation.objects.filter(
        user=request.user,
        showtime=showtime,
        expires_at__gt=timezone.now()
    ).select_related('seat')
    
    if not user_reservations:
        return redirect('tickets:select_seats', showtime_id=showtime_id)
    
    # 計算總價
    seat_count = user_reservations.count()
    total_price = showtime.price * seat_count
    
    # 獲取座位資訊
    seats = [reservation.seat for reservation in user_reservations]
    
    return render(request, 'tickets/select_seats.html', {
        'showtime': showtime,
        'seats': seats,
        'seat_count': seat_count,
        'total_price': total_price,
        'payment_methods': Order.PAYMENT_METHOD_CHOICES,
    })

# 創建訂單
# @login_required
def create_order(request):
    if request.method == 'POST':
        showtime_id = request.POST.get('showtime_id')
        payment_method = request.POST.get('payment_method')
        
        showtime = get_object_or_404(Showtime, id=showtime_id)
        
        # 獲取用戶的座位預訂
        user_reservations = SeatReservation.objects.filter(
            user=request.user,
            showtime=showtime,
            expires_at__gt=timezone.now()
        ).select_related('seat')
        
        if not user_reservations:
            return redirect('tickets:select_seats', showtime_id=showtime_id)
        
        # 計算總價
        seat_count = user_reservations.count()
        total_price = showtime.price * seat_count
        
        try:
            with transaction.atomic():
                # 創建訂單
                order = Order(
                    user=request.user,
                    showtime=showtime,
                    total_price=total_price,
                    status='pending',
                    payment_method=payment_method
                )
                order.save()
                
                # 添加座位到訂單
                for reservation in user_reservations:
                    OrderSeat.objects.create(
                        order=order,
                        seat=reservation.seat
                    )
                
                # 刪除預訂
                user_reservations.delete()
                
                # 重定向到付款頁面
                return redirect('tickets:payment', order_id=1)
        except Exception as e:
            # 處理錯誤
            return render(request, 'tickets/error.html', {
                'message': f'創建訂單時出錯: {str(e)}'
            })
    
    return redirect('tickets:movie_list')

# 訂單詳情
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_type:
        payment_type="信用卡"
    else:
        payment_type=""
    seats = Seat.objects.filter(orderseat__order=order)
    return render(request, 'tickets/order_detail.html', {
        'order': order,
        "payment_type":payment_type,
        'seats': seats,
    })
    


# 用戶訂單列表
@login_required
@csrf_exempt 
def my_orders(request):    
    if request.method == "POST":
        try:           
            merchant_id =  request.POST.get("MerchantID")            # 特店編號
            merchant_tradeNo = request.POST.get("MerchantTradeNo")   # 特店交易編號            
            rtn_msg = request.POST.get("RtnMsg")                     # 交易訊息(成功或失敗)                            
            payment_date = request.POST.get("PaymentDate")           # 付款時間(yyyy/MM/dd HH:mm:ss)
            payment_type = request.POST.get("PaymentType")           # 特店選擇的付款方式             
            trade_date = request.POST.get("TradeDate")               # 訂單成立時間(yyyy/MM/dd HH:mm:ss)
            
            payment_date = datetime.strptime(payment_date,"%Y/%m/%d %H:%M:%S")                            
            trade_date = datetime.strptime(trade_date,"%Y/%m/%d %H:%M:%S")            
            
            # (這些是會員支付後綠界回傳的交易資訊，管理帳戶可能會用到)
            order = Order.objects.get(id=1)                                        
            order.merchant_id=merchant_id
            order.merchant_tradeNo=merchant_tradeNo
            order.rtn_msg=rtn_msg                    
            order.payment_date=payment_date
            order.payment_type=payment_type
            order.trade_date=trade_date            
            order.save()
            return render(request, 'tickets/my_orders.html',{'order_id': 1})  # 先模擬訂單編號 1        
                    
        except:
            return render(request,"tickets/create_order.html",{"messages":"資料輸入錯誤，請稍後再試!"})  
    try:    
        orders = Order.objects.get(user=request.user).order_by('-order_date')                
        return render(request, 'tickets/my_orders.html', {'orders': orders})
    except:
        return render(request, 'tickets/my_orders.html')
    
    
   

# 使用綠界模擬信用卡付款所需的檔案
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
sdk_path = os.path.join(BASE_DIR,"ecpay_payment_sdk.py")
spec = importlib.util.spec_from_file_location(
    "ecpay_payment_sdk",
    sdk_path
)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


''' 一般信用卡測試卡號 :
    4311-9511-1111-1111 安全碼 : 任意輸入三碼數字
    4311-9522-2222-2222 安全碼 : 任意輸入三碼數字
'''

@login_required
def payment(request,order_id):               
    order_params = {
    'MerchantTradeNo': datetime.now().strftime("NO%Y%m%d%H%M%S"),     
    'StoreID': '',
    'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    'PaymentType': 'aio',
    'TotalAmount': 540,      # 模擬資料 
    'TradeDesc': '訂單測試',
    'ItemName': '米奇17號',      # 模擬資料 
    'ReturnURL': 'https://www.ecpay.com.tw/return_url.php',
    'ChoosePayment': 'Credit',
    'ClientBackURL': 'http://127.0.0.1:8000/tickets/my_orders/',
    'ItemURL': 'https://www.ecpay.com.tw/item_url.php',
    'Remark': '交易備註',
    'ChooseSubPayment': '',
    'OrderResultURL': 'http://127.0.0.1:8000/tickets/my_orders/',
    'NeedExtraPaidInfo': 'Y',
    'DeviceSource': '',
    'IgnorePayment': '',
    'PlatformID': '',
    'InvoiceMark': 'N',
    'CustomField1': str(order_id),    # 存入訂單 ID ,後續可以對應查詢
    'CustomField2': '',
    'CustomField3': '',
    'CustomField4': '',
    'EncryptType': 1,
    }

    
    # 建立實體
    ecpay_payment_sdk = module.ECPayPaymentSdk(
        MerchantID='3002607',
        HashKey='pwFHCqoQZGmho4w6',
        HashIV='EkRm7iFT261dpevs'
    )
    
    try:
        # 產生綠界訂單所需參數
        final_order_params = ecpay_payment_sdk.create_order(order_params)

        # 產生 html 的 form 格式
        action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境，不會真付款
       
        html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
        print(html)
        return HttpResponse(html)
    except Exception as error:
        print('An exception happened: ' + str(error))



def get_seats_for_showtime(request, showtime_id):
    """
    根據場次 ID 回傳該場次的座位資訊（包含是否已售出）
    """
    showtime = Showtime.objects.get(id=showtime_id)
    seats = Seat.objects.filter(theater=showtime.theater)

    seat_data = []
    for seat in seats:
        is_sold = SeatReservation.objects.filter(showtime=showtime, seat=seat).exists()
        seat_data.append({
            "id": seat.id,
            "row": seat.row,
            "number": seat.number,
            "is_sold": is_sold  # 如果已售出則標記
        })

    return JsonResponse({"seats": seat_data})



@csrf_exempt
def reserve_seats(request):
    if request.method == "POST":
        data = json.loads(request.body)
        showtime_id = data.get("showtime_id")
        selected_seats = data.get("selected_seats")  # 例如 ["A1", "A2"]

        showtime = Showtime.objects.get(id=showtime_id)
        reserved_seats = []

        for seat_code in selected_seats:
            row, number = seat_code[0], int(seat_code[1:])  # 解析 "A1" 變成 Row: A, Number: 1
            seat = Seat.objects.get(theater=showtime.theater, row=row, number=number)

            # 確保座位沒被佔用
            if not SeatReservation.objects.filter(showtime=showtime, seat=seat, status="sold").exists():
                SeatReservation.objects.create(showtime=showtime, seat=seat, status="reserved")
                reserved_seats.append(seat_code)

        return JsonResponse({"reserved_seats": reserved_seats})


# 取得所有影城
def get_theaters(request):
    theaters = Theater.objects.all().values("id", "name")
    return JsonResponse({"theaters": list(theaters)})

# 取得影城內的電影
def get_movies(request, theater_id):
    movies = Movie.objects.filter(showtimes__theater_id=theater_id).distinct().values("id", "title")  
    return JsonResponse({"movies": list(movies)})
# 取得電影的可選日期
def get_dates(request, movie_id):
    dates = Showtime.objects.filter(movie_id=movie_id, start_time__gte=timezone.now()) \
        .distinct().values_list("start_time", flat=True)
    
    # 確保使用 localtime
    formatted_dates = sorted(set(localtime(date).date().isoformat() for date in dates))
    
    return JsonResponse({"dates": formatted_dates})
# 取得電影的可選場次
def get_sessions(request, theater_id, movie_id, date):
    try:
        # 確保 `date` 是 `datetime.date` 類型
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()

        # 查詢符合電影、影城與日期的場次
        sessions = Showtime.objects.filter(
            theater_id=theater_id,  # 限制為特定影城
            movie_id=movie_id,
            start_time__date=date_obj
        ).values("id", "start_time")

        # 格式化時間為 HH:MM
        formatted_sessions = [{"id": s["id"], "time": localtime(s["start_time"]).strftime("%H:%M")} for s in sessions]

        return JsonResponse({"sessions": formatted_sessions})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    

def order_summary(request):
    cart = request.session.get("cart", {})  # 取得購物車資訊

    return render(request, "tickets/order_summary.html", {
        "cart": cart  # 傳遞購物車資訊給前端
    })

@csrf_exempt
def select_seat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            showtime_id = data.get("showtime_id")
            seat_id = data.get("seat_id")
            action = data.get("action")

            showtime = Showtime.objects.get(id=showtime_id)
            seat = Seat.objects.get(id=seat_id)
            user = request.user if request.user.is_authenticated else None

            if action == "select":
                # 嘗試取得預約紀錄，若無則建立一筆
                reservation, created = SeatReservation.objects.get_or_create(
                    showtime=showtime,
                    seat=seat,
                    defaults={
                        "user": user,
                        "status": "reserved",
                        "expires_at": timezone.now() + timedelta(minutes=30)
                    }
                )

                # 如果已存在但是別人預約或售出，不允許
                if not created:
                    if reservation.status in ["reserved", "sold"] and reservation.user != user:
                        return JsonResponse({"success": False, "message": "此座位已被選取或售出"})

                    # 如果是自己的或無人持有 → 更新狀態
                    reservation.user = user
                    reservation.status = "reserved"
                    reservation.expires_at = timezone.now() + timedelta(minutes=30)
                    reservation.save()

                return JsonResponse({"success": True})

            elif action == "cancel":
                reservation = SeatReservation.objects.get(
                    showtime=showtime,
                    seat=seat,
                    user=user,
                    status="reserved"
                )
                reservation.delete()
                return JsonResponse({"success": True})

            else:
                return JsonResponse({"success": False, "message": "不支援的操作"})

        except SeatReservation.DoesNotExist:
            return JsonResponse({"success": False, "message": "找不到座位紀錄"})
        except IntegrityError:
            return JsonResponse({"success": False, "message": "儲存時發生錯誤，可能資料重複"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"錯誤：{str(e)}"})

    return JsonResponse({"success": False, "message": "只接受 POST 請求"})

@login_required
def member_index(request):    
    return render(request,"tickets/member_index.html",locals())
# 會員首頁（用戶登入後的首頁)
# 訂票頁面
@login_required
def me_ticket(request):
    # 在此處可以添加與訂票相關的內容
    return render(request, 'tickets/me_ticket.html')

# 選擇座位頁面
@login_required
def me_seat(request):
    # 在此處可以添加與座位選擇相關的內容
    return render(request, 'tickets/me_seat.html')
