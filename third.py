class Car:
    car_status:bool = False
    temperature:float
    def __init__(self, brand:str, model:str, color:str, price:float):
        self.brand = brand
        self.model = model
        self.color = color
        self.price = price
        self.range = 500

    def __str__(self):
        return f"{self.brand} {self.model} {self.color} {self.price} {self.range}"

    def __repr__(self):
        return f"{self.brand} {self.model} {self.color} {self.price} {self.range}"

    def __eq__(self, other):
        return self.model == other.model and self.brand == other.brand

    def start(self, driver:str):
        self.car_status = True
        print(f"{driver} has started {self.model}.")

    def stop(self):
        self.car_status = False
        print(f"{self.model} has stopped.")

    def start_charge(self, charge_type:str):
        print(f"{self.model} has charged at {charge_type}.")

    def play_youtube(self):
        if not self.car_status:
            print("playing youtube.")
        else:
            print("please stop the car before playing youtube.")

    def set_temperature(self, temperature:float):
        self.temperature = temperature
        print(f"{self.model} has set temperature to {temperature}℃.")

car1 = Car("Tesla","Model Y","Grey",260000)
car2 = Car("Tesla","Model 3","White",220000)
car3 = Car("Tesla","Model 3","White",220000)
print(car1)
print(car2 == car3)

car1.start("Kelvin")
car1.stop()
car1.play_youtube()
car1.set_temperature(22)
