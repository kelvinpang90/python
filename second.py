import random
__all__ = ["print_star","add"]
def first(something):

    """
    Return the first element of something or return None
    :param something: something to input
    :return: something to output
    """

    print(something)
    return "first:"+something

text = first("test")
print(text)

# 局部变量，全局变量
num = 100
def get_(str):

    """
    get  count from a string
    :param str:
    :return:
    """
    # 调用的是全局变量，修改了值在退出方法后仍然有效
    global num
    num = 10000
    vowel = set("aeiou")
    print(vowel)
    print(sum(1 for c in str if c.lower() in vowel))

# get_(input("input string:"))
print(num)

# 匿名函数
# lambda 参数列表：函数体
add = lambda x,y:x+y
sub = lambda x,y:x-y
mul = lambda x,y:x*y
div = lambda x,y:x/y

def cal(x,y,oper):
    return oper(x,y)

print(cal(3,3,sub))

data_list = ["C++", "C", "Python", "Jack", "PHP", "Java", "Go", "JavaScript", "Rust"]
data_list.sort(key=lambda x:len(x),reverse=False)
print(data_list)

# 递归 函数调用自己
# 计算阶乘
def recursion(n):
    if n == 1:
        return 1
    else:
        return n*recursion(n-1)

print(recursion(6))

# case
"""
案例2：定义一个用于根据传入的一批商品信息（商品名、价格、数量）、优惠（优惠券、积分抵扣）、运费信息计算订单的总金额的函数。
具体规则如下：
1. 优惠券需要商品总额满5000才可以使用，且优惠券金额不能超过商品总价。
2. 积分抵扣需要商品总金额满5000才可以使用，100积分抵扣1元（且抵扣金额不能超过商品总价，积分只能整百抵扣）。
"""

def cal_amount(*items:tuple[str,int,int],coupon:int=0,score:int=0,shipment:int=0)->tuple:
    total_amount:int = sum(item[1]*item[2] for item in items)
    # coupon
    if 5000 <= total_amount <= coupon:
        total_amount = 0
    else:
        total_amount -= coupon
    # score
    if total_amount >0 and score >= 100:
        if score // 100 >= total_amount:
            # 积分可完全抵扣商品金额
            score -= total_amount*100
            total_amount = 0
        else:
            total_amount -= score//100
            score %= 100
    # shipment
    total_amount += shipment
    return total_amount, score

items = [("可乐",20,50),("薯片",100,200),("烧烤",50,300)]
print(cal_amount(*items,coupon=1000,score=200,shipment=100))

print(random.choice(items))


def print_star():
    print("*" * 30)

print(__name__)