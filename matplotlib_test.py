import matplotlib.pyplot as plt
import random

from matplotlib.axes import Axes

x = [i for i in range(1,11)]
y1 = [random.randint(0,100) for i in range(10)]
y2 = [random.randint(0,100) for i in range(10)]

plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为SimHei
# 折线图
# plt.figure(figsize=(10,5)) # 定义画布长宽
# plt.plot(x,y1,label="汽油车")
# plt.plot(x,y2,label="柴油车")
# plt.title("汽车销量", fontsize=20)
# plt.xlabel("月份", fontsize=15)
# plt.ylabel("销量", fontsize=15)
# plt.xticks(x)
# plt.legend(loc="best")
# plt.show()

figure, axes = plt.subplots(nrows=1, ncols=2,figsize=(20,5),dpi=100)

countries = ['China','Usa','Australia','Japan','Korea','Russia','Singapore']
values = [random.randint(10,100) for i in range(7)]
# 图一 柱状图
axis1: Axes = axes[0]
axis1.bar(countries,values,color="green")
axis1.set_title(label='oil reservation')
axis1.set_xlabel('countries')
axis1.set_ylabel('million barrels')
# 图二 饼状图
axis2: Axes = axes[1]
axis2.pie(values,labels=countries,autopct='%1.2f%%')
axis2.legend('lower center',ncol=7)
plt.savefig('test.png')
plt.show()
