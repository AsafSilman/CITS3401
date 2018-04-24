from datetime import datetime, date, timedelta
import random
import os
import csv

START_DATE = date(2015, 1, 1)
END_DATE   = date(2018, 11, 1)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

class SalesGenerator(object):
    # Pick random number[0,100], if in range, pick that
    daily_probability = {
        "Mon": (0,3),
        "Tue": (4,7),
        "Wed": (8,25),
        "Thu": (26,28),
        "Fri": (29,31),
        "Sat": (32,33),
        "Sun": (34,35)
    }

    # Pick random number[0,100], if in range, pick that
    product_probability = {
        "1": (0, 25),
        "2": (25, 50),
        "3": (51, 100)
    }

    product_prices = {
        "1": 10,
        "2": 10,
        "3": 10
    }

    # Quantity of product in order
    quantity_choices = [
        500,
        800,
        1000,
        2000,
        4000,
        6000
    ]

    currency_ids = [
        1,
        2,
        3,
        4
    ]

    refund_rate = 5 # percentage

    minimum_quantity = 7500 

    buy_back = 5000

    def __init__(self):
        self.order_id = 1
        self.purchase_id = 1
        self.stock_level_id = 1
        self.orders = []
        self.purchases = []
        self.stock_levels_daily = []

    def _parse_csv_file(self, path):
        lines = []
        with open(path) as f:
            reader = csv.reader(f)
            for line in reader:
                lines.append(line)
        return lines
    
    def load_customers(self, customer_path):
        self.customers = self._parse_csv_file(customer_path)
        self.customer_ids = [customer[0] for customer in self.customers]

    def load_dates(self, date_path):
        self.dates = self._parse_csv_file(date_path)
        self.date_ids = [date[0] for date in self.dates]

    def load_employees(self, employee_path):
        self.employees = self._parse_csv_file(employee_path)
        self.employee_ids = [employee[0] for employee in self.employees]

    def load_products(self, customer_path):
        self.products = self._parse_csv_file(customer_path)
        self.product_ids = [product[0] for product in self.products]

    def load_warehouse_data(self, warehouse_path):
        self.warehouses = self._parse_csv_file(warehouse_path)
        self.warehouse_ids = [warehouse[0] for warehouse in self.warehouses]

    def init_warehouse_stocks(self, level):
        self.warehouse_stocks = {
            w_id : {product: level+random.randint(-15,15) for product in self.product_ids}
            for w_id in self.warehouse_ids
        }

    def _pick_product(self):
        product_random = random.randint(0,100)

        for product in self.product_probability:
            p_low, p_high = self.product_probability[product]
            if p_low <= product_random <= p_high:
                return product

    def _pick_employee(self, department=None):
        if department is None:
            return random.choice(self.employee_ids)
        else:
            employee_departments = [
                employee[0] 
                for employee in self.employees
                if employee[8].lower()==department.lower()
            ]
            return random.choice(employee_departments)

    def _is_refunded(self, order_date):
        refund = random.randint(0,100)

        if refund <= self.refund_rate:
            refund_date = (order_date + timedelta(days=3)).strftime("%Y%m%d")
            refund_employee = self._pick_employee()
            return (refund_date, refund_employee)
        else: return ("NULL","NULL")

    def generate_order(self, order_d):
        order_id = self.order_id; self.order_id+= 1
        order_date = order_d.strftime("%Y%m%d")
        product_id  = self._pick_product()
        customer_id = random.choice(self.customer_ids)
        warehouse_id = random.choice(self.warehouse_ids)
        currency_id = random.choice(self.currency_ids)
        quantity = random.choice(self.quantity_choices)

        fulfilment_date = (order_d + timedelta(days=1)).strftime("%Y%m%d")
        fulfilment_employee = self._pick_employee(department="Warehouse")

        refund_date, refunt_employee = self._is_refunded(order_d)

        self.adjust_stocks(order_d, warehouse_id, product_id, quantity, refund_date)
        self.purchase_low_stocks(order_d, warehouse_id, product_id)

        total = quantity * self.product_prices[product_id]

        self.orders.append({
            "OrderID": order_id,
            "OrderDate": order_date,
            "ProductID": product_id,
            "CustomerID": customer_id,
            "FulfilmentDate": fulfilment_date,
            "FulfilmentEmployee": fulfilment_employee, 
            "RefundDate": refund_date,
            "RefundEmployee": refunt_employee,
            "WarehouseID": warehouse_id,
            "CurrencyID": currency_id,
            "Quantity": quantity,
            "TotalPriceAUD": total
        })

    def adjust_stocks(self, order_date, warehouse_id, product_id, quantity, refund_date):
        # nothing to adjust if there was a refund
        if len(refund_date) != 0:
            return
        self.warehouse_stocks[warehouse_id][product_id] -= quantity
        if self.warehouse_stocks[warehouse_id][product_id] < 0:
            self.generate_purchase(order_date, warehouse_id, product_id)


    def purchase_low_stocks(self, order_date, warehouse_id, product_id):
        if self.warehouse_stocks[warehouse_id][product_id] < self.minimum_quantity:
            quantity = self.generate_purchase(order_date, warehouse_id, product_id)
            self.warehouse_stocks[warehouse_id][product_id] += quantity


    def generate_purchase(self, order_date, warehouse_id, product_id):
        order_quantity = self.buy_back + random.randint(-5,5)*10
        purchase_id = self.purchase_id; self.purchase_id+= 1
        self.purchases.append(
            {
                "PurchaseID": purchase_id,
                "PurchaseDate": order_date.strftime("%Y%m%d"), 
                "WarehouseID": warehouse_id,
                "ProductID": product_id,
                "Quantity": order_quantity
            }
        )
        return order_quantity

    def generate_daily_stock_levels(self, day):
        day_code = day.strftime("%Y%m%d")
        for warehouse_id in self.warehouse_stocks:
            for product_id in self.warehouse_stocks[warehouse_id]:
                stock_level_id = self.stock_level_id; self.stock_level_id+= 1
                self.stock_levels_daily.append({
                    "StockLevelID": stock_level_id,
                    "DateID": day_code,
                    "WarehouseID": warehouse_id,
                    "ProductID": product_id,
                    "StockLevel": self.warehouse_stocks[warehouse_id][product_id]
                })

    def generate_data(self, start_date, end_date, daily_iterations=5):
        for d in daterange(start_date, end_date):
            for _ in range(daily_iterations):
                daily_random   = random.randint(0,100)

                weekday_short = d.strftime("%a")
                d_low, d_high = self.daily_probability[weekday_short] # daily low/high
                
                # Generate a sale
                if d_low<= daily_random <= d_high:
                    self.generate_order(d)

            # Calculate daily stock
            self.generate_daily_stock_levels(d)

    def write_out_data(self, out_dir=".."):
        orders_path = os.path.join(out_dir,"OrderFactSampleData.csv")
        purchases_path = os.path.join(out_dir,"PurchasesFactSampleData.csv")
        stock_levels_path = os.path.join(out_dir,"StockLevelsFactSampleData.csv")

        orders_headers = [
            "OrderID",
            "OrderDate",
            "CustomerID",
            "ProductID",
            "FulfilmentDate",
            "FulfilmentEmployee",
            "RefundDate",
            "RefundEmployee",
            "WarehouseID",
            "CurrencyID",
            "Quantity",
            "TotalPriceAUD"
        ]

        purchases_headers = [
            "PurchaseID",
            "PurchaseDate",
            "Quantity",
            "ProductID",
            "WarehouseID"
        ]

        stock_headers = [
            "StockLevelID",
            "DateID",
            "ProductID",
            "WarehouseID",
            "StockLevel",
        ]

        self._write_data(self.orders, orders_path, orders_headers)
        self._write_data(self.purchases, purchases_path, purchases_headers)
        self._write_data(self.stock_levels_daily, stock_levels_path, stock_headers)


    def _write_data(self, data_list, out_dir, headers=None):
        with open(out_dir, "w") as f:
            if headers is None:
                writer = csv.DictWriter(f, data_list[0].keys())
            else:
                writer = csv.DictWriter(f, headers)
            writer.writeheader()
            for data in data_list:
                writer.writerow(data)

def main():
    sg = SalesGenerator()
    
    sg.load_customers("../CustomerDimSampleData.csv")
    sg.load_dates("../DateDimSampleData.csv")
    sg.load_employees("../EmployeeDimSampleData.csv")
    sg.load_products("../ProductDimSampleData.csv")
    sg.load_warehouse_data("../WarehouseDimSampleData.csv")

    sg.init_warehouse_stocks(10000)

    sg.generate_data(START_DATE, END_DATE)

    sg.write_out_data()

if __name__=="__main__":
    main()