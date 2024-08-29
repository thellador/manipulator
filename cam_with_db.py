#!/usr/bin/env python
import time
import cv2
import numpy as np
from ArucoDetection_definitions import *
import sqlite3

start_time = time.time()
xGreen = None
yGreen = None
xYellow = None
yYellow = None

desired_aruco_dictionary1 = "DICT_4X4_50"
desired_aruco_dictionary2 = "DICT_6X6_50"

ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL
}

# Define the physical dimensions of the area in millimeters
area_width_mm = 303  # x
area_height_mm = 186  # y

def get_markers(vid_frame, aruco_dictionary, aruco_parameters):
    bboxs, ids, rejected = cv2.aruco.detectMarkers(vid_frame, aruco_dictionary, parameters=aruco_parameters)
    if ids is not None:
        ids_sorted = [id_number[0] for id_number in ids]
    else:
        ids_sorted = ids
    return bboxs, ids_sorted

square_points = [[10, cv2.CAP_PROP_FRAME_HEIGHT - 10], [cv2.CAP_PROP_FRAME_WIDTH - 10, cv2.CAP_PROP_FRAME_HEIGHT - 10],
                 [cv2.CAP_PROP_FRAME_WIDTH - 10, 10], [10, 10]]
init_loc_1 = [10, 470]
init_loc_2 = [630, 470]
init_loc_3 = [630, 10]
init_loc_4 = [10, 10]

current_square_points = [init_loc_1, init_loc_2, init_loc_3, init_loc_4]
current_center_Corner = [[0, 0]]
marker_location_hold = True

def nothing(*arg):
    pass

def convert_pixels_to_mm(x_pixel, y_pixel, img_width_pixels, img_height_pixels):
    x_mm = (x_pixel / img_width_pixels) * area_width_mm - area_width_mm / 2
    y_mm = area_height_mm - (y_pixel / img_height_pixels) * area_height_mm + 185
    return x_mm, y_mm

def main():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS manipulator (
        id INTEGER PRIMARY KEY,
        xGreen INTEGER,
        yGreen INTEGER,
        xYellow INTEGER,
        yYellow INTEGER
    )
    ''')

    conn.commit()
    conn.close()

    global xGreen
    global yGreen
    global xYellow
    global yYellow
    print("[INFO] detecting '{}' markers...".format(desired_aruco_dictionary1))
    this_aruco_dictionary1 = cv2.aruco.Dictionary_get(ARUCO_DICT[desired_aruco_dictionary1])
    this_aruco_parameters1 = cv2.aruco.DetectorParameters_create()
    this_aruco_dictionary2 = cv2.aruco.Dictionary_get(ARUCO_DICT[desired_aruco_dictionary2])
    this_aruco_parameters2 = cv2.aruco.DetectorParameters_create()

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    # Set camera resolution to the maximum supported
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Change this to the maximum width supported by your camera
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Change this to the maximum height supported by your camera

    square_points = current_square_points

    color_ranges = [
        (np.array((66, 87, 31), np.uint8), np.array((83, 187, 93), np.uint8), (0, 255, 0)),
        (np.array((23, 199, 50), np.uint8), np.array((40, 255, 140), np.uint8), (0, 255, 255)),
    ]

    cv2.namedWindow("settings")
    cv2.createTrackbar('h1', 'settings', 0, 255, nothing)
    cv2.createTrackbar('s1', 'settings', 0, 255, nothing)
    cv2.createTrackbar('v1', 'settings', 0, 255, nothing)
    cv2.createTrackbar('h2', 'settings', 255, 255, nothing)
    cv2.createTrackbar('s2', 'settings', 255, 255, nothing)
    cv2.createTrackbar('v2', 'settings', 255, 255, nothing)

    while True:
        current_time = time.time()
        delay = 0

        ret, frame = cap.read()
        img_height_pixels, img_width_pixels = frame.shape[:2]

        markers, ids = get_markers(frame, this_aruco_dictionary1, this_aruco_parameters1)

        frame_clean = frame.copy()
        left_corners, corner_ids = getMarkerCoordinates(markers, ids, 0)

        if marker_location_hold:
            if corner_ids is not None:
                count = 0
                for id in corner_ids:
                    if id > 4:
                        break
                    current_square_points[id - 1] = left_corners[count]
                    count += 1
            left_corners = current_square_points
            corner_ids = [1, 2, 3, 4]

        if (start_time + delay * 1) < current_time and (start_time + delay * 2) > current_time:
            cv2.aruco.drawDetectedMarkers(frame, markers)
        if (start_time + delay * 2) < current_time:
            draw_corners(frame, left_corners)
        if (start_time + delay * 3) < current_time:
            draw_numbers(frame, left_corners, corner_ids)
        if (start_time + delay * 4) < current_time:
            show_spec(frame, left_corners)

        frame_with_square, squareFound = draw_field(frame, left_corners, corner_ids)

        if (start_time + delay * 6) < current_time:
            if squareFound:
                square_points = left_corners
            img_wrapped = four_point_transform(frame_clean, np.array(square_points))
            h, w, c = img_wrapped.shape
            marker_foam, ids_foam = get_markers(img_wrapped, this_aruco_dictionary2, this_aruco_parameters2)
            left_corner_foam, corner_id_foam = getMarkerCoordinates(marker_foam, ids_foam, 0)
            centerCorner = getMarkerCenter_foam(marker_foam)

            if marker_location_hold:
                if corner_id_foam is not None:
                    current_center_Corner[0] = centerCorner[0]
                centerCorner[0] = current_center_Corner[0]

            draw_corners(img_wrapped, centerCorner)
            img_wrapped = cv2.line(img_wrapped, (centerCorner[0][0], 0), (centerCorner[0][0], h), (0, 0, 255), 2)
            img_wrapped = cv2.line(img_wrapped, (0, centerCorner[0][1]), (w, centerCorner[0][1]), (0, 0, 255), 2)
            draw_numbers(img_wrapped, left_corner_foam, corner_id_foam)

            color_coordinates = {}
            for hsv_min, hsv_max, color in color_ranges:
                color_coordinates[color] = []


            for hsv_min, hsv_max, color in color_ranges:
                hsv = cv2.cvtColor(img_wrapped, cv2.COLOR_BGR2HSV)
                thresh = cv2.inRange(hsv, hsv_min, hsv_max)

                moments = cv2.moments(thresh, 1)
                dM01 = moments['m01']
                dM10 = moments['m10']
                dArea = moments['m00']

                if dArea > 100:
                    x = int(dM10 / dArea)
                    y = int(dM01 / dArea)
                    x_mm, y_mm = convert_pixels_to_mm(x, y, w, h)
                    color_coordinates[color].append((x_mm, y_mm))
                    cv2.circle(img_wrapped, (x, y), 5, color, 2)
                    cv2.putText(img_wrapped, f"{x_mm:.0f},{y_mm:.0f}", (x - 65, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                color, 2)

            cv2.imshow('img_wrapped', img_wrapped)

            conn = sqlite3.connect("database.db")

            cursor = conn.cursor()
            global xGreen
            global yGreen
            global xYellow
            global yYellow
            for color, coordinates in color_coordinates.items():
                for x_mm, y_mm in coordinates:
                    print(f"Found {color} at {x_mm}, {y_mm}")
                    if color == (0, 255, 0):  # Зеленый цвет
                        xGreen = x_mm
                        yGreen = y_mm
                    elif color == (0, 255, 255):  # Желтый цвет
                        xYellow = x_mm
                        yYellow = y_mm

            id = 0

            sql = '''
            INSERT INTO manipulator (id, xGreen, yGreen, xYellow, yYellow)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
            xGreen = excluded.xGreen,
            yGreen = excluded.yGreen,
            xYellow = excluded.xYellow,
            yYellow = excluded.yYellow
            '''

            try:
                if xGreen != None:
                    cursor.execute(sql, (id, xGreen, yGreen, xYellow, yYellow))
                    print("УСПЕШНО!!!")
                    #xGreen = None
                    #yGreen = None
                    #xYellow = None
                    #yYellow = None
                else:
                    print("НЕТ ШАРИКА!!!")
            except:
                print("ОШИБКА")

            conn.commit()
            conn.close()

            hsv = cv2.cvtColor(img_wrapped, cv2.COLOR_BGR2HSV)

            h1 = cv2.getTrackbarPos('h1', 'settings')
            s1 = cv2.getTrackbarPos('s1', 'settings')
            v1 = cv2.getTrackbarPos('v1', 'settings')
            h2 = cv2.getTrackbarPos('h2', 'settings')
            s2 = cv2.getTrackbarPos('s2', 'settings')
            v2 = cv2.getTrackbarPos('v2', 'settings')

            h_min = np.array((h1, s1, v1), np.uint8)
            h_max = np.array((h2, s2, v2), np.uint8)

            thresh = cv2.inRange(hsv, h_min, h_max)
            cv2.imshow('result', thresh)

        cv2.imshow('frame_with_square', frame_with_square)

        if cv2.waitKey(1) & 0xFF == ord('\r'):
            print(f"(np.array(({h1}, {s1}, {v1}), np.uint8), np.array(({h2}, {s2}, {v2}), np.uint8), (255, 255, 255))")
        print(xYellow)

    cap.release()
    cv2.destroyAllWindows()


    return save_coordinate()


if __name__ == '__main__':
    foam_center = main()