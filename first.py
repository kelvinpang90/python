
from second import *

num = 1
print(num)

str = "hello"
print(str)

num1 = 1.1
print(num1)

a1 = True
print(a1)
a2 = False
print(a2)

print(f"output1:{num1}, output2:{a2}, output3:{str}")

# input
# name = input("please input your name:")
# print(f"my name is {name}")
#
# total = 1000
# withdraw = input(f"withdraw amount:")
# print(f"balance is {total-int(withdraw)}")

# 算数运算符
print(10/5)
print(5/9)
print(10//3)
print(10%3)
print(10**3)

num2 = 3
num2 **= 3
print (num2)

print(True & False)
print(True | False)
print(True ^ False)

# if 语句
# sides_length = input("please input your triangle sides length:")
# sides = sides_length.split(",")
# side1 = int(sides.pop())
# side2 = int(sides.pop())
# side3 = int(sides.pop())
# if side1+side2>side3 and side1+side3>side2 and side2+side3>side1:
#     if side1 == side2 and side1 == side3:
#         print("equilateral triangle")
#     elif side1 == side2 or side2 == side3:
#         print("isosceles triangle")
#     else:
#         print("scalene triangle")
# else:
#     print("not a triangle")

# match
# question = list(input("please enter:"))
# num1 = float(question[0])
# operator = question[1]
# num3 = float(question[2])
#
# match operator:
#     case "+":
#         print(num1 + num3)
#     case "-":
#         print(num1 - num3)
#     case "*":
#         print(num1 * num3)
#     case "/":
#         print(num1 / num3)

# print(eval("".join(question)))

# while
# num = 0
# total = 0
# while num <= 100:
#     if num % 2 == 0:
#         total += num
#     num += 1
# print(total)


# for和range的使用
# msg = "hello world"
# for i in msg:
#     print(i)

# total = 0
# for j in range(1,101,2):
#     # if j % 2 != 0:
#         total += j
# print(total)

# total = 0
# for j in range(100,501):
#     if j % 3 == 0:
#         total += j
# print(total)

# 嵌套循环 九九乘法表
# str = ""
# for i in range(1,10):
#     for j in range(1,10):
#         str += f"{j}*{i}={i*j},"
#     print(str)
#     str = ""

# while True:
#     username = input("username:")
#     password = input("password:")
#     if username == "admin" and password == "111111":
#         print("login success")
#         break
#     else:
#         print("login failed, try again")

# import random
# num = random.randint(0,100)
# print(num)
# while True:
#     num1 = int(input("enter a number:"))
#     if num1 == num:
#         print("correct!!!")
#         break
#     elif num>num1:
#         print("make it greater!")
#     elif num<num1:
#         print("make it lesser!")
#     continue

# list[] editable
# s = [1,"ok",3,4,5]
# s[2] = False
# del s[4]
# print(s)
#
# str = "delete"
# print(str)
# del str
# print(str)
#
# for i in s:
#     print(i)
# print("s.count(3):"+s.count(3).__str__())
# s.append(6)
# print(s)
# s.reverse()
# print(s)
# s.pop()
# print(s)
# print(s.__len__())
# # list slice 从list提取一小段list
# print(s[0:2:1])
# # print("s.index()"+s.index())
# print("s.clear():"+s.clear().__str__())
# print(s)
#
# # case
# str = "60,70,80,90,10,20,30,40,50"
# print(str)
# s = list(map(int,str.split(",")))
# s.sort()
# average = sum(s)/len(s)
# print("greatest:"+s[0].__str__()+",least:"+s[-1].__str__()+",average:"+ average.__str__())
#
# # case 2
# s1 = [1,2,3,4,5]
# s2 = [5,6,7,8,9]
# # 解包：将list类解开成一个一个元素
# # 组包：多个元素合并到一个容器
# s3 = [*s1,*s2]
# new_list = []
# for i in s3:
#     if i not in new_list:
#         new_list.append(i)
# print(new_list)
#
# # case3
# s4 = []
# for i in range(1,21):
#     s4.append(i*i)
# # 列表推导式
# s4 = [i**2 for i in range(1,21)]
# print(s4)
#
# str = "hello"
# print(str[0])
# # 切片
# print(str[:2])
# print(str[-1:-str.__len__()-1:-1])
# str2 = "你好"
# print(str2[0])

# # tuple() uneditable
# # packing
# t1 = (1,2,3,4,5)
#
# # unpacking
# a,b,c,d,e = t1
# x,*y = t1
# print(x)
# print(y)
# x,*y,z = t1
# print(x)
# print(y)
# print(z)
#
# # swap
# a = 1
# b = 2
# a,b = b,a
# print(a)
# print(b)

# 计算个人总分，平均分
students = (
    ("S001", "王林", 85, 92, 78),
    ("S002", "李娜娜", 92, 88, 95),
    ("S003", "十二", 78, 85, 82),
    ("S004", "曾牛", 88, 79, 91),
    ("S005", "周杰", 95, 96, 89),
    ("S006", "王卓", 76, 82, 77),
    ("S007", "红霞", 89, 91, 94),
    ("S008", "徐立国", 75, 69, 82),
    ("S009", "许木", 86, 89, 98),
    ("S010", "通天", 66, 59, 72)
)

for id,name,chinese,math,english in students:
    total = chinese+math+english
    average = round(total/3,2)
    if average>90:
        print(f"名字：{name}，总分：{total}，平均分：{average}，优秀！")
    else:
        print(f"名字：{name}，总分：{total}，平均分：{average}")

# 计算各科最高分，最低分，平均分
chinese_score = [student[2] for student in students]
math_score = [student[3] for student in students]
english_score = [student[4] for student in students]

print(f"语文最高分：{max(chinese_score)}，最低分：{min(chinese_score)}，平均分：{round(sum(chinese_score)/len(chinese_score),2)}")
print(f"数学最高分：{max(math_score)}，最低分：{min(math_score)}，平均分：{round(sum(math_score)/len(math_score),2)}")
print(f"英文最高分：{max(english_score)}，最低分：{min(english_score)}，平均分：{round(sum(english_score)/len(english_score),2)}")

# set{} 无序，不可重复，可修改
s1 = {"a", "b", "c","c"}
s1.add("d")
print(s1)

# 选修足球学生名单
football_set = {"王林", "曾牛", "徐立国", "涂天", "天运子", "韩立", "厉飞雨", "马卫", "紫灵"}
# 选修篮球学生名单
basketball_set = {"张铁", "墨居仁", "王林", "姜老道", "曾牛", "王蝉", "韩立", "天运子", "李化元", "厉飞雨", "云露"}
# 选修法语学生名单
french_set = {"许木", "王卓", "十三", "虎隐", "姜老道", "天运子", "红蝶", "厉飞雨", "韩立", "曾牛"}
# 选修艺术学生名单
art_set = {"涂天", "天运子", "韩立", "虎隐", "姜老道", "紫灵"}

print(f"选修了法语和艺术：{french_set.intersection(art_set)}")
print(f"选修了法语和艺术：{french_set & art_set}")

print(f"同时选修4项：{football_set.intersection(basketball_set, french_set,art_set)}")
print(f"同时选修4项：{football_set & basketball_set & french_set & art_set}")

print(f"选足球，没选篮球：{football_set.difference(basketball_set)}")
print(f"选足球，没选篮球：{football_set - basketball_set}")

all_s = {*football_set,*basketball_set,*french_set,*art_set}
all_l = [*football_set,*basketball_set,*french_set,*art_set]
print(all_s)
print(all_l)
for s in all_s:
    print(f"{s}共选修了：{all_l.count(s)}门课程")

# dict(key:value)
# d = dict()
# d = {}
# print(d)
# d[1] = "a"
# d[2] = "b"
# d[3] = "c"
# d[4] = "d"
# d[5] = "e"
# print(d)
# print(d.keys())
# print(d.values())
# print(d.items())
#
# for k,v in d.items():
#     print(f"{k}: {v}")

text = """
########## 购物车系统 ##########

#       1. 添加购物车        #
#       2. 修改购物车        #
#       3. 删除购物车        #
#       4. 查询购物车        #
#       5. 退出购物车        #

###############################
"""
print(text)
shopping_cart = dict()
while True:
    match input("请输入操作（1-5）："):
        case "1":
            name = input("商品名字：")
            if name not in shopping_cart:
                price = input("价格：")
                count = input("数量：")
                shopping_cart[name] = {"price": price, "count": count}
            else:
                print("商品已存在！")
        case "2":
            name = input("商品名字：")
            if name in shopping_cart:
                price = input("价格：")
                count = input("数量：")
                shopping_cart[name] = {"price": price, "count": count}
        case "3":
            name = input("商品名字：")
            shopping_cart.pop(name)
        case "4":
            name = input("商品名字：")
            shopping_cart.get(name)
        case "5":
            break
        case _:
            print("unsupported input")
    print(shopping_cart)

# print(second.sub(10,20))
print_star()
# print(second.__name__)