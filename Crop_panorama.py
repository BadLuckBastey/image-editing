# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:55:01 2020

@author: sebjae
"""
# =============================================================================
# Module
# =============================================================================
import cv2
import glob
import os 
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import Toplevel


# =============================================================================
# Funktionen
# =============================================================================


def get_max_x(contour):
    max_x = tuple(contour[contour[:, :, 0].argmax()][0])[0]
    return max_x


def get_max_y(contour):
    max_y = tuple(contour[contour[:, :, 1].argmax()][0])[1]
    return max_y


def get_directory():
    global dir_name
    global dir_label
    dir_label.place_forget()
    dir_name = fd.askdirectory()
    dir_label = tk.Label(root, text=':)', bg='green')
    dir_label.place(x=170, y=360)
    root.update()
# =============================================================================
# Funktionen Benutzeroberfläche
# =============================================================================


def change_row_count():
    global right_to_left
    global right_to_left_button
    if right_to_left is True:
        right_to_left = False
        right_to_left_button = tk.Button(root, text='von links nach rechts', command=change_row_count)
    else:
        right_to_left = True
        right_to_left_button = tk.Button(root, text='von rechts nach links', command=change_row_count)
    right_to_left_button.place_forget()
    right_to_left_button.place(x=250, y=100)
    preview()
    root.update()


def change_column_count():
    global bottom_to_top
    global bottom_to_top_button
    if bottom_to_top is True:
        bottom_to_top = False
        bottom_to_top_button = tk.Button(root, text='von oben nach unten', command=change_column_count)
    else:
        bottom_to_top = True
        bottom_to_top_button = tk.Button(root, text='von unten nach oben', command=change_column_count)
    bottom_to_top_button.place_forget()
    bottom_to_top_button.place(x=250, y=130)
    preview()
    root.update()


def change_linewise_count():
    global count_column_wise
    global count_column_wise_button
    if count_column_wise is True:
        count_column_wise = False
        count_column_wise_button = tk.Button(root, text='reihenweise zählen ', command=change_linewise_count)
    else:
        count_column_wise = True
        count_column_wise_button = tk.Button(root, text='spaltenweise zählen', command=change_linewise_count)
    count_column_wise_button.place_forget()
    count_column_wise_button.place(x=250, y=160)
    preview()
    root.update()


def preview():
    global right_to_left
    global bottom_to_top
    global count_column_wise

    rows = int(row_entry.get())
    columns = int(column_entry.get())

    sample_list = range(1, rows * columns+1)
    row_number = []
    column_number = []

    if count_column_wise is True:
        for i in range(columns):
            for j in range(rows):
                row_number.append(j)
                column_number.append(i)
    else:
        for i in range(rows):
            for j in range(columns):
                row_number.append(i)
                column_number.append(j)

    if right_to_left is True:
        column_number.reverse()
    if bottom_to_top is True:
        row_number.reverse()

    for i in range(rows * columns):
        number_label = tk.Label(preview_frame, text=sample_list[i])
        number_label.grid(row=row_number[i], column=column_number[i])


# =============================================================================
# Proben erkennen und ausschneiden
# =============================================================================


def crop_images():
    global status_label
    # prüfen und laden der eingegebenen Werte
    if dir_name != '' and row_entry.get().isdigit() and column_entry.get().isdigit():
        load_path = dir_name
        rows = int(row_entry.get())
        columns = int(column_entry.get())
        sample_name = name_entry.get()

        os.chdir(load_path)
        try:
            os.mkdir(load_path + '/Einzelbilder')
        except:
            print('directory already exists')
        save_path = load_path + '/Einzelbilder/'

        image_count = 1

        # Bearbeiten aller .tif-Bilder im Zielordner. Außenkonturen werden über einen Grenzwert erkannt und nach Größe und Position sortiert
        for image in glob.glob('*.tif'):
            img = cv2.imread(image)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            hull = sorted(contours, key=cv2.contourArea, reverse=True)[:(rows * columns)]

            # Die n größten Flächen werden entsprechd der Auswahl sortiert und ausgeschnitten
            if count_column_wise is True:
                for i in range(columns):
                    hull_column = sorted(hull, key=get_max_x, reverse=right_to_left)[i*rows: i*rows + rows]
                    hull_row = sorted(hull_column, key=get_max_y, reverse=bottom_to_top)
                    for j in range(rows):
                        x, y, w, h = cv2.boundingRect(hull_row[j])
                        crop_img = img[y:y+h, x:x+w]
                        if image_count < 10:
                            cv2.imwrite(save_path + sample_name + '0' + str(image_count) + '.tif', crop_img)
                        else:
                            cv2.imwrite(save_path + sample_name + str(image_count) + '.tif', crop_img)
                        status_label = tk.Label(root, text='{} Bilder ausgeschnitten  '.format(image_count))
                        status_label.place(x=500, y=300)
                        root.update()
                        image_count += 1
            else:
                for i in range(rows):
                    hull_row = sorted(hull, key=get_max_y, reverse=bottom_to_top)[i*columns: i*columns + columns]
                    hull_column = sorted(hull_row, key=get_max_x, reverse=right_to_left)
                    for j in range(columns):
                        x, y, w, h = cv2.boundingRect(hull_column[j])
                        crop_img = img[y:y+h, x:x+w]
                        if image_count < 10:
                            cv2.imwrite(save_path + sample_name + '0' + str(image_count) + '.tif', crop_img)
                        else:
                            cv2.imwrite(save_path + sample_name + str(image_count) + '.tif', crop_img)
                        status_label = tk.Label(root, text='{} Bilder ausgeschnitten  '.format(image_count))
                        status_label.place(x=500, y=300)
                        root.update()
                        image_count += 1

        root.destroy()
    else:
        warning = tk.Toplevel(root)
        warning.title('Fehler')
        # warning.iconphoto(False, tk.PhotoImage(file='Hier war der Dateipfad zum Logo'))
        warning.geometry('300x100')
        warning_label = tk.Label(warning, text='Fehler!\n\nBitte überprüfe noch einmal die Eingaben')
        warning_label.place(x=20, y=20)


# =============================================================================
# Benutzeroberfläche
# =============================================================================
right_to_left = True
bottom_to_top = True
count_column_wise = True

dir_name = ''

# Eigenschaften der Benutzeroberfläche definieren
root = tk.Tk()
root.title('IAPT - Crop Images Fast')
# root.iconphoto(False, tk.PhotoImage(file='Hier war ursprünglch der Dateipfad zum Logo'))
root.geometry('800x500')

user_header = tk.Label(root, text='Benutzereingaben', font=3)
user_header.place(x=50, y=20)

# Eingabefenster für Probenbezeichnung
name_label = tk.Label(root, text='Probenbezeichnung')
name_label.place(x=50, y=70)
name_entry = tk.Entry(root)
name_entry.place(x=50, y=90)

# Eingabefenster für die Anzahl der Zeilen
row_label = tk.Label(root, text='Anzahl der Reihen')
row_label.place(x=50, y=120)
row_entry = tk.Entry(root)
inital_rows = '4'
row_entry.insert(0, inital_rows)
row_entry.place(x=50, y=140)

# Eingabefenster für die Anzahl der Spalten
column_label = tk.Label(root, text='Anzahl der Spalten')
column_label.place(x=50, y=170)
column_entry = tk.Entry(root)
initial_columns = '3'
column_entry.insert(0, initial_columns)
column_entry.place(x=50, y=190)

# Knöpfe zur Anordnung der Proben im Panoramabild
count_order_label = tk.Label(root, text='Anordnung der Proben')
count_order_label.place(x=250, y=70)
right_to_left_button = tk.Button(root, text='von rechts nach links', command=change_row_count)
right_to_left_button.place(x=250, y=100)
bottom_to_top_button = tk.Button(root, text='von unten nach oben', command=change_column_count)
bottom_to_top_button.place(x=250, y=130)
count_column_wise_button = tk.Button(root, text='spaltenweise zählen', command=change_linewise_count)
count_column_wise_button.place(x=250, y=160)

# Vorschau zur aktuellen Probensortierung
preview_header = tk.Label(root, text='Vorschau', font=3)
preview_header.place(x=500, y=20)
preview_frame = tk.Frame(root)
preview_frame.place(x=500, y=40)

# Angabe für den Nutzer, zeigt den aktuellen Fortschritt
status_update_header = tk.Label(root, text='Statusupdates', font=3)
status_update_header.place(x=500, y=260)
status_label = tk.Label(root, text='0 Bilder ausgeschnitten  ')
status_label.place(x=500, y=300)

# Auswahl des Ordners in dem Bilder ausgeschnitten werden sollen
dir_button = tk.Button(root, text='Ordner auswählen', command=get_directory)
dir_button.place(x=50, y=360)
dir_label = tk.Label(root, text='!', bg='red')
dir_label.place(x=170, y=360)

# Programm starten
start_button = tk.Button(root, text='Bilder ausschneiden', command=crop_images)
start_button.place(x=50, y=420)
preview()


root.mainloop()
