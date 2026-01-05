from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from .models import Students, QueraDataCustomuser

@api_view(['POST'])
def Register_adminter(request):
    try:
      username = request.data.get("username")
      password = request.data.get("password")
      
      admin_username = QueraDataCustomuser.objects.filter(username=username)
      if admin_username:
          return JsonResponse({"success":False, 'reason':"this admin is exist"})
      
      s = Students.objects.get(pid=1)
      account_super = QueraDataCustomuser(
            username=username,
            is_superuser=True,
            students_pid=s
         )
      account_super.set_password(password)
      account_super.save()
      return JsonResponse({'success':True, 'reason':""})
    except Exception as e:
      return JsonResponse({"success":False, "reason":str(e)})
        
@api_view(['POST'])
def update_password_adminter(request):
    try:
        user = request.user
        new_password = request.data.get("password")
        user.set_password("new_password")
        user.save()
        return JsonResponse({"success":True, "reason":""})
    except Exception as e:
        return JsonResponse({"success":False, "reason":str(e)})

@api_view(['POST'])
def delete_account_adminter(request):
    try:
        username = request.data.get("username")
        account_super = QueraDataCustomuser.objects.get(username=username)
        account_super.delete()
        return JsonResponse({"success":True, "reason":""})
    except Exception as e:
        return JsonResponse({"success":False, "reason":str(e)})
        
@api_view(['POST'])
def update_password(request):
    new_password = request.data.get("password")
    pid = request.data.get("pid")
    
    if pid == 1:
        return JsonResponse({'success':False , 'reason':"you can not delete user whose pid is 1, this user is important"})
    
    try:
      s = Students.objects.get(pid=pid)
    except Studnets.DoesNotExist:
      return JsonResponse({"success":False, "reason":"this students is not exist"})
    
    customer = s.account
    customer.set_password(new_password)
    customer.save()
    return JsonResponse({"success":True, "reason":""})

@api_view(['POST'])
def Register(request):
    try:
     username = request.data.get('username')
     password = request.data.get('password')
     name = request.data.get('name')
     sduid = request.data.get('sduid')
     contact = request.data.get('contact')
     
     student_use_username = QueraDataCustomuser.objects.filter(username=username)
     student_use_sduid = Students.objects.filter(sduid=sduid)
     
     if student_use_username:
         return JsonResponse({'success':False, 'reason':"user is exist"})
     if student_use_sduid:
         return JsonResponse({'success':False, 'reason':"sduid is exist"})
     
     student = Students.objects.create(sduid=sduid, contact=contact, name=name)
     account = QueraDataCustomuser(
        username = username,
        students_pid=student
     )
     account.set_password(password)
     account.save()

    except Exception as e:
        return JsonResponse({'success': False, 'reason':str(e)})
    return JsonResponse({'success': True, 'reason':""})


# @api_view(['POST'])
# def SearchAccount(request):
#     type = request.data.get('type')
#     data = request.data.get('data')
#     students = None
#     customers = None

#     if data is not None and data.strip():
#       if type == 'name':
#         students = Students.objects.filter(name=data)
#         # 从每个学生反向查询关联用户（一对一/多对多）
#         customers = [student.account for student in students]
#       elif type == 'sduid':
#         students = Students.objects.filter(sduid=data)
#         # 从每个学生反向查询关联用户（一对一/多对多）
#         customers = [student.account for student in students]
#       elif type == 'username':
#         customers = QueraDataCustomuser.objects.filter(username=data)
#         students = [customer.students_pid for customer in customers]
#     else:
#         students = Students.objects.all()
#         customers = [student.account for student in students]

#     resutl = [ {'pid': student.pid, 'username':customer.username, 'password':customer.password, 'name':student.name, 'sduid':student.sduid, 'contact':student.contact} for customer, student in zip(customers, students)]
#     return JsonResponse({'results': resutl}, status=200)
@api_view(['POST'])
def SearchAccount(request):
    type = request.data.get('type')
    data = request.data.get('data')
    try:
        if type == 'name':
           students = Students.objects.filter(name=data)

           if not students:
               return JsonResponse({'success': False, 'reason':"不存在该姓名的学生信息"})

           customers = [student.account for student in students]
        elif type == 'sduid':
           students = Students.objects.filter(sduid=data)

           if not students:
               return JsonResponse({'success': False, 'reason':"不存在该学号的学生信息"})

           customers = [student.account for student in students]
        elif type == 'username':
           customers = QueraDataCustomuser.objects.filter(username=data)

           if not customers:
               return JsonResponse({'success':False, 'reason':'不存在该用户名的用户信息'})

           students = [customer.students_pid for customer in customers]
        else:
           students = list(Students.objects.all())
           students.pop(0)

           if not students:
               return JsonResponse({'success': False, 'reason':"不存在学生信息"})

           customers = [student.account for student in students]

    except Exception as e:
        return JsonResponse({"success":False, "reason":str(e)})
    
    results = [{
        'pid':student.pid,
        'sduid':student.sduid,
        'name':student.name,
        'username':customer.username,
        'password':customer.password,
        'contact':student.contact
    } for student, customer in zip(students, customers)]
    
    return JsonResponse({'results':results}, status=200)


@api_view(['POST'])
def UpdateAccount(request):
    try:
     pid = request.data.get('pid')
     username = request.data.get('username')
     password = request.data.get('password')
     name = request.data.get('name')
     sduid = request.data.get('sduid')
     contact = request.data.get('contact')

     try:
      student = Students.objects.get(pid=pid)
     except Students.DoesNotExist:
        return JsonResponse({'success':False,'reason':"对应的学生信息不存在"})
     else:
        try:
            customer = student.account
        except customer.DoesNotExist:
            return JsonResponse({'success':False, "reason":"对应的账户信息不存在"})

     student.name = name
     student.sduid = sduid
     student.contact = contact

     customer.username = username
     customer.set_password(password)

     student.save()
     customer.save()
    except Exception as e:
        return JsonResponse({'success':False,'reason':str(e)})
    return JsonResponse({'success':True, 'reason':""})

@api_view(['POST'])
def DeleteAccount(request):
    pid = request.data.get('pid')
    
    if pid == 1:
        return JsonResponse({'success':False , 'reason':"you can not delete user whose pid is 1, this user is important"})
    
    try:
        try:
            student = Students.objects.get(pid=pid)
        except Students.DoesNotExist:
            return JsonResponse({'success': False, 'reason': "对应的学生信息不存在"})
        else:
            try:
                customer = student.account
            except customer.DoesNotExist:
                return JsonResponse({'success': False, "reason": "对应的账户信息不存在"})
        student.delete()
    except Exception as e:
        return JsonResponse({'success':False,"reason":str(e)})

    return JsonResponse({'success':True, "reason":""})

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

@api_view(['POST'])
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "reason": "POST only"})

    username = request.data.get("account")
    password = request.data.get("password")
    remember_me = request.data.get("remember_me")  # "true" or "false"
    ismanager = request.data.get('ismanager')

    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({"success": False, "reason": "invalid credentials"})
    
    if ismanager:
        if not user.is_superuser:
            return JsonResponse({"success": False, "reason": "not an administrator"})
    if not ismanager:
        if user.is_superuser:
            return JsonResponse({"success": False, "reason": "adminstrator can not log in common user"})

    # 登录并创建 session
    login(request._request, user)
    get_token(request._request)

    # ========= 动态设置 Session 过期时间 =========
    if remember_me:
        # 记住我：7 天
        request.session.set_expiry(60 * 60 * 24 * 7)
    else:
        # 不记住：浏览器关闭后失效
        request.session.set_expiry(60 * 32)    # 设置没选择记住我时，登录有效的最长空闲时间为32分钟

    return JsonResponse({"success": True, "reason": ""})

@api_view(['GET'])
def check_status(request):
    #return JsonResponse({"cookie":request.COOKIE})
    if not request.user.is_authenticated:
        return JsonResponse({"success":False, "reason":"no log in"})
    
    if request.user.is_authenticated:
        return JsonResponse({"success":True, "reason":""})

@api_view(['GET'])
def logout_view(request):
    if request.method not in ['GET']:
        return JsonResponse({"success":False, "reason":"GET only"})

    try:
        # 调用Django内置的logout函数
        logout(request._request)
        # 返回成功响应
        return JsonResponse({"success":True, "reason":""})
    except Exception as e:
        return JsonResponse({"success":False, "reason":str(e)})


    
    
        
    
