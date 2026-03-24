class Product:
    def __init__(self,name,price,quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return f"（商品名：{self.name}，价格： {self.price}，数量 {self.quantity}）"

    def __eq__(self, other):
        return self.name == other.name

class ShoppingCart:
    products = []

    def __str__(self):
        print(self.products)

    def add_product(self,name,price,quantity):

        product = Product(name,price,quantity)
        self.products.append(product)

    def remove_product(self,name):
        if self.products.__len__()<=0:
            print("购物车为空")
            return
        for product in self.products:
            if product.name == name:
                self.products.remove(product)
                print(f"商品{product.name}删除成功！")
            else:
                print("找不到对应商品！")

    def show_products(self):
        print(self.products)

    def get_product(self,name):
        for product in self.products:
            if product.name == name:
                print(product)
                return
            else:
                print("找不到对应商品！")
                return
        print("购物车为空！")

    def modify_product(self,name,price,quantity):
        for product in self.products:
            if product.name == name:
                product.price = price
                product.quantity = quantity
                return
            else:
                print("找不到对应商品！")


shopping_cart = ShoppingCart()
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
while True:
    i = int(input("输入对应操作数字："))
    match i:
        case 1:
            product_name = input("商品名字：")
            product_price = input("商品价格：")
            product_quantity = input("商品数量：")
            shopping_cart.add_product(product_name,product_price,product_quantity)
        case 2:
            product_name = input("商品名字：")
            product_price = input("商品价格：")
            product_quantity = input("商品数量：")
            shopping_cart.modify_product(product_name,product_price,product_quantity)
        case 3:
            product_name = input("商品名字：")
            shopping_cart.remove_product(product_name)
        case 4:
            shopping_cart.show_products()
        case 5:
            break
        case _:
            print("输入错误，请重新输入！")
