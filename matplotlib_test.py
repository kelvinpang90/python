import matplotlib.pyplot as plt
import random
x = [i for i in range(1,11)]
y1 = [random.randint(0,100) for i in range(10)]
y2 = [random.randint(0,100) for i in range(10)]

plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为SimHei
plt.figure(figsize=(10,5))
plt.plot(x,y1,label="汽油车")
plt.plot(x,y2,label="柴油车")
plt.title("中文", fontsize=20)
plt.xlabel("月份", fontsize=15)
plt.ylabel("销量", fontsize=15)
plt.xticks(x)
plt.legend(loc="best")
plt.show()