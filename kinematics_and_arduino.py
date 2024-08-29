import serial
from sympy import *
from math import *

from time import sleep


import sqlite3


# Configure the COM port
port = "COM6"  # Replace with the appropriate COM port name
baudrate = 115200

# Подключение к базе данных
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Извлечение последней записи (можно изменить запрос в зависимости от ваших требований)
cursor.execute('''
SELECT xGreen, yGreen, xYellow, yYellow
FROM manipulator
ORDER BY id DESC
LIMIT 1
''')

row = cursor.fetchone()
conn.close()

# Обработка и вывод данных
if row:
    xGreen, yGreen, xYellow, yYellow = row
    print(f"xGreen: {xGreen}, yGreen: {yGreen}, xYellow: {xYellow}, yYellow: {yYellow}")
else:
    print("No data found")

# Закрытие соединения
conn.close()

def move_to_position_cart(x, y, z):
    l0 = 130
    l1 = 120
    l2 = 120 
    l3 = 120

    r_compensation = 1.00  # Коэффициент компенсации (2%)
    r_hor = sqrt(x ** 2 + y ** 2)
    r = sqrt(r_hor ** 2 + (z - l0) ** 2) * r_compensation

    # Рассчитываем угол для базы
    if y == 0:
        if x <= 0:
            theta_base = 180
        else:
            theta_base = 0
    else:
        theta_base = 90 - degrees(atan(x / y))

    # Корректируем координаты только после расчета угла базы
    y -= 15  # Учитываем смещение по оси Y

    # Рассчитываем углы для плеча, локтя и запястья
    alpha1 = acos(((r - l2) / (l1 + l3)))
    theta_shoulder = degrees(alpha1)
    alpha3 = asin((sin(alpha1) * l3 - sin(alpha1) * l1) / l2)
    theta_elbow = (90 - degrees(alpha1)) + degrees(alpha3)
    theta_wrist = (90 - degrees(alpha1)) - degrees(alpha3)

    # Проверяем граничные условия для запястья
    if theta_wrist <= 0:
        alpha1 = acos(((r - l2) / (l1 + l3)))
        theta_shoulder = degrees(alpha1 + asin((l3 - l1) / r))
        theta_elbow = (90 - degrees(alpha1))
        theta_wrist = (90 - degrees(alpha1))

    # Корректируем угол для плеча, если z не совпадает с l0
    if z != l0:
        theta_shoulder = theta_shoulder + degrees(atan(((z - l0) / r)))

    # Преобразуем углы для соответствия формату передачи в Arduino
    theta_elbow = 180 - theta_elbow
    theta_wrist = theta_wrist

    # Формируем список углов
    theta_array = [round(theta_base + 5), round(theta_shoulder-1), round(theta_elbow+3), round(theta_wrist+1)]
    return theta_array



try:
    # Open the COM port
    ser = serial.Serial(port, baudrate=baudrate)
    print("Serial connection established.")

    # Send commands to the Arduino
    while True:
        what_colour = input("Выберите цвет: ")
        if what_colour == "g":
            # Подключение к базе данных
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            # Извлечение последней записи (можно изменить запрос в зависимости от ваших требований)
            cursor.execute('''
            SELECT xGreen, yGreen, xYellow, yYellow
            FROM manipulator
            ORDER BY id DESC
            LIMIT 1
            ''')

            row = cursor.fetchone()
            conn.close()

            # Обработка и вывод данных
            if row:
                xGreen, yGreen, xYellow, yYellow = row
                print(f"xGreen: {xGreen}, yGreen: {yGreen}, xYellow: {xYellow}, yYellow: {yYellow}")
            else:
                print("No data found")

            # Закрытие соединения
            conn.close()

            x = xGreen
            y = yGreen
            z = 15

        if what_colour == "y":
            # Подключение к базе данных
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            # Извлечение последней записи (можно изменить запрос в зависимости от ваших требований)
            cursor.execute('''
            SELECT xGreen, yGreen, xYellow, yYellow
            FROM manipulator
            ORDER BY id DESC
            LIMIT 1
            ''')

            row = cursor.fetchone()
            conn.close()

            # Обработка и вывод данных
            if row:
                xGreen, yGreen, xYellow, yYellow = row
                print(f"xGreen: {xGreen}, yGreen: {yGreen}, xYellow: {xYellow}, yYellow: {yYellow}")
            else:
                print("No data found")

            # Закрытие соединения
            conn.close()

            x = xYellow
            y = yYellow
            z = 15


        #x = int(input("Enter a command (x): "))
        #y = int(input("Enter a command (y): "))
       # z = int(input("Enter a command (z): "))

        angles_for_robot = move_to_position_cart(x, y, z + 200)
        command = f"{angles_for_robot[0]} {angles_for_robot[1]} {angles_for_robot[2]} 65 {angles_for_robot[3]} 75"
        ser.write(command.encode())
        print(f"Sent command: {command}")
        sleep(2)
        angles_for_robot = move_to_position_cart(x, y, z)
        command = f"{angles_for_robot[0]} {angles_for_robot[1]} {angles_for_robot[2]} 65 {angles_for_robot[3]} 75"
        ser.write(command.encode())
        print(f"Sent command: {command}")
        sleep(2)
        command = f"{angles_for_robot[0]} {angles_for_robot[1]} {angles_for_robot[2]} 65 {angles_for_robot[3]} 0"
        ser.write(command.encode())
        print(f"Sent command: {command}")
        sleep(2)
        angles_for_robot = move_to_position_cart(-200, 0, 300)
        command = f"{angles_for_robot[0] - 5} {angles_for_robot[1]} {angles_for_robot[2]} 65 {angles_for_robot[3]} 0"
        ser.write(command.encode())
        print(f"Sent command: {command}")
        sleep(2)
        angles_for_robot = move_to_position_cart(-200, 0, 50)
        command = f"{angles_for_robot[0] - 5} {angles_for_robot[1]} {angles_for_robot[2]} 65 {angles_for_robot[3]} 0"
        ser.write(command.encode())
        print(f"Sent command: {command}")
        sleep(2)
        angles_for_robot = move_to_position_cart(-200, 0, 50)
        command = f"{angles_for_robot[0] - 5} {angles_for_robot[1]} {angles_for_robot[2]} 65 {angles_for_robot[3]} 75"
        ser.write(command.encode())
        print(f"Sent command: {command}")
        sleep(1)
        command = f"{0} {90} {90} 65 {90} 75" #agle for kleshnia
        ser.write(command.encode())
        print(f"Sent command: {command}")

except serial.SerialException as se:
    print("Serial port error:", str(se))

except KeyboardInterrupt:
    pass

finally:
    # Close the serial connection
    if ser.is_open:
        ser.close()
        print("Serial connection closed.")
