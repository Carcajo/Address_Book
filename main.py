from tkinter import *
import sqlite3
from pathlib import Path
import datetime
from tkinter import ttk
from tkinter.messagebox import showinfo, askyesno

fle = Path('address_book.db')
fle.touch(exist_ok=True)

db = sqlite3.connect("address_book.db")
cur = db.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS books (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT,
    create_date DATE
);
""")
db.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS persons (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER,
    first_name  TEXT,
    last_name   TEXT,
    address_1   TEXT,
    address_2   TEXT,
    work_number TEXT,
    home_number TEXT,
    [index]     TEXT,
    FOREIGN KEY (
        book_id
    )
    REFERENCES books (id) ON DELETE CASCADE
);
""")
db.commit()

# функция создаёт окно, которое позволяет создать новую адресную книгу
def create_new_address_book(*args, start=False, dwindow: Tk = None):
    # эта функция вызывается при каждом изменении поля с вводом названия адресной книги и валидирует это поле
    def change_entry(value):
        nonlocal errorLabel, entry

        if value != "":
            if errorLabel.place_info() != {}:
                errorLabel.place_forget()
        else:
            if errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.1, relwidth=0.8, relx=0.1, rely=0.55)

        if len(value) > 18:
            return False

        return True

    #  функция закрывает окно
    def exit(*args):
        nonlocal window

        window.destroy()

    # функция создаёт адресную книгу и закрывает окно
    def create(*largs):
        nonlocal window, entry, errorLabel, args, dwindow
        global db, cur

        if entry.get():
            cur.execute("INSERT INTO books (name, create_date) VALUES (?, ?)",
                        (entry.get(), datetime.datetime.now().strftime("%Y-%m-%d")))
            db.commit()

            if start:
                window.destroy()
                select_book()
            else:
                if args:
                    args[0]()
                    args[1]()

                if dwindow:
                    cur.execute("SELECT * FROM books")
                    book = sorted(cur.fetchall(), key=lambda x: x[0])[-1]

                    dwindow.destroy()
                    window.destroy()
                    active_book(*book)
                else:
                    window.destroy()
        else:
            if errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.1, relwidth=0.8, relx=0.1, rely=0.55)

    window = Tk()
    window.title("Создание новой адресной книги")
    window.geometry("350x200")

    Label(window, text="Введите название адресной книги:", font=("Arial", 10)).place(relheight=0.1, relwidth=0.8,
                                                                                     relx=0.1, rely=0.1)

    entry = Entry(window, font=("Arial", 10), validate="key", validatecommand=(window.register(change_entry), '%P'))
    entry.place(relheight=0.1, relwidth=0.8, relx=0.1, rely=0.3)
    entry.focus()

    window.bind("<Return>", create)
    entry.bind("<Escape>", exit)

    errorLabel = Label(window, text="Введите название адресной книги!", foreground="red")

    Button(window, text="Отмена", command=exit, font=("Arial", 10)).place(relheight=0.1, relwidth=0.2, rely=0.8,
                                                                          relx=0.1)

    Button(window, text="Создать", command=create, font=("Arial", 10)).place(relheight=0.1, relwidth=0.2, rely=0.8,
                                                                             relx=0.7)

    window.mainloop()

# функция создаёт окно, которое позволяет добавлять новую запись в адресную книгу
def add_person(book_id: int, book_name: str, func_update, func_selecting):
    # эта функция вызывается при каждом изменении любого из полей ввода и добавляет надпись о том, что поля нужно заполнить если они ещё не заполнены
    def change_entry(type, value):
        nonlocal errorLabel, first_nameEntry, last_nameEntry, work_numberEntry, home_numberEntry

        if ((first_nameEntry.get() if type != "firstName" else value) or (
                last_nameEntry.get() if type != "lastName" else value)) and (
                (work_numberEntry.get() if type != "workNumber" else value) or (
                home_numberEntry.get() if type != "homeNumber" else value)):
            if errorLabel.place_info() != {}:
                errorLabel.place_forget()
        else:
            if errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.07, relwidth=0.3, rely=0.91, relx=0.35)

        return True

    #  функция закрывает окно
    def exit(*args):
        nonlocal window

        window.destroy()

    # функция создает новую запись в адресной книги и закрывает окно
    def create(*args):
        nonlocal window, errorLabel, first_nameEntry, last_nameEntry, address_1Entry, address_2Entry, work_numberEntry, home_numberEntry, indexEntry
        global db, cur

        if (first_nameEntry.get() or last_nameEntry.get()) and (work_numberEntry.get() or home_numberEntry.get()):
            cur.execute(
                "INSERT INTO persons (book_id, first_name, last_name, address_1, address_2, work_number, home_number, 'index') VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (book_id, first_nameEntry.get(), last_nameEntry.get(), address_1Entry.get(), address_2Entry.get(),
                 work_numberEntry.get(), home_numberEntry.get(), indexEntry.get()))
            db.commit()

            func_update()
            func_selecting()

            window.destroy()
        else:
            if errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.07, relwidth=0.3, rely=0.91, relx=0.35)

    window = Tk()
    window.title(f"Добавить запись в адресную книгу \"{book_name}\"")
    window.geometry("300x450")

    Label(window, text="Имя:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.02)
    Label(window, text="Фамилия:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.15)
    Label(window, text="Адрес 1:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.28)
    Label(window, text="Адрес 2:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.41)
    Label(window, text="Рабочий\nтелефон:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05,
                                                                      rely=0.54)
    Label(window, text="Домашний\nтелефон:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05,
                                                                       rely=0.67)
    Label(window, text="Почтовый\nиндекс:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05,
                                                                      rely=0.80)

    first_nameEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                            validatecommand=(window.register(lambda x: change_entry("firstName", x)), '%P'))
    first_nameEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.02)
    last_nameEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                           validatecommand=(window.register(lambda x: change_entry("lastName", x)), '%P'))
    last_nameEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.15)
    address_1Entry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                           validatecommand=(window.register(lambda x: change_entry(None, x)), '%P'))
    address_1Entry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.28)
    address_2Entry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                           validatecommand=(window.register(lambda x: change_entry(None, x)), '%P'))
    address_2Entry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.41)
    work_numberEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                             validatecommand=(window.register(lambda x: change_entry("workNumber", x)), '%P'))
    work_numberEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.54)
    home_numberEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                             validatecommand=(window.register(lambda x: change_entry("homeNumber", x)), '%P'))
    home_numberEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.67)
    indexEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                           validatecommand=(window.register(lambda x: change_entry(None, x)), '%P'))
    indexEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.80)

    Button(window, font=("Arial", 10), text="Отмена", command=exit).place(relheight=0.05, relwidth=0.3, rely=0.93,
                                                                          relx=0.05)
    errorLabel = Label(window, font=("Arial", 7), foreground="red", text="Введите имя,\nфамилию и\nномер телефона!")
    Button(window, font=("Arial", 10), text="Добавить", command=create).place(relheight=0.05, relwidth=0.3, rely=0.93,
                                                                              relx=0.65)

    window.bind("<Return>", create)
    window.bind("<Escape>", exit)

    window.mainloop()


# функция создаёт окно, которое позволяет изменить запись в адресной книге
def edit_person(book_name: str, *persons, func_update, func_selecting):
    # эта функция вызывается при каждом изменении любого из полей ввода и добавляет надпись о том, что поля нужно заполнить если они ещё не заполнены
    def change_entry(type, value):
        nonlocal errorLabel, first_nameEntry, last_nameEntry, work_numberEntry, home_numberEntry

        if ((first_nameEntry.get() if type != "firstName" else value) or (
                last_nameEntry.get() if type != "lastName" else value)) and (
                (work_numberEntry.get() if type != "workNumber" else value) or (
                home_numberEntry.get() if type != "homeNumber" else value)):
            if errorLabel.place_info() != {}:
                errorLabel.place_forget()
        else:
            if errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.07, relwidth=0.3, rely=0.91, relx=0.35)

        return True

    #  функция закрывает окно
    def exit(*args):
        nonlocal window

        window.destroy()

    # функция изменяет запись в адресной книги и закрывает окно
    def save(*args):
        nonlocal window, errorLabel, first_nameEntry, last_nameEntry, address_1Entry, address_2Entry, work_numberEntry, home_numberEntry, indexEntry
        global db, cur

        if (first_nameEntry.get() or last_nameEntry.get()) and (work_numberEntry.get() or home_numberEntry.get()):
            cur.execute(
                "UPDATE persons SET first_name = ?, last_name = ?, address_1 = ?, address_2 = ?, work_number = ?, home_number = ?, 'index' = ? WHERE id = ?",
                (first_nameEntry.get(), last_nameEntry.get(), address_1Entry.get(), address_2Entry.get(),
                 work_numberEntry.get(), home_numberEntry.get(), indexEntry.get(), persons[0]))
            db.commit()

            func_update()
            func_selecting()

            window.destroy()
        else:
            if errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.07, relwidth=0.3, rely=0.91, relx=0.35)

    window = Tk()
    window.title(f"Изменить запись в адресной книге \"{book_name}\"")
    window.geometry("300x450")

    Label(window, text="Имя:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.02)
    Label(window, text="Фамилия:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.15)
    Label(window, text="Адрес 1:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.28)
    Label(window, text="Адрес 2:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.41)
    Label(window, text="Рабочий\nтелефон:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05,
                                                                      rely=0.54)
    Label(window, text="Домашний\nтелефон:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05,
                                                                       rely=0.67)
    Label(window, text="Почтовый\nиндекс:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05,
                                                                      rely=0.80)

    first_nameEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                            validatecommand=(window.register(lambda x: change_entry("firstName", x)), '%P'))
    first_nameEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.02)
    last_nameEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                           validatecommand=(window.register(lambda x: change_entry("lastName", x)), '%P'))
    last_nameEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.15)
    address_1Entry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                           validatecommand=(window.register(lambda x: change_entry(None, x)), '%P'))
    address_1Entry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.28)
    address_2Entry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                           validatecommand=(window.register(lambda x: change_entry(None, x)), '%P'))
    address_2Entry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.41)
    work_numberEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                             validatecommand=(window.register(lambda x: change_entry("workNumber", x)), '%P'))
    work_numberEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.54)
    home_numberEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                             validatecommand=(window.register(lambda x: change_entry("homeNumber", x)), '%P'))
    home_numberEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.67)
    indexEntry = Entry(window, font=("Arial", 9), justify=LEFT, validate="key",
                       validatecommand=(window.register(lambda x: change_entry(None, x)), '%P'))
    indexEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.80)

    Button(window, font=("Arial", 10), text="Отмена", command=exit).place(relheight=0.05, relwidth=0.3, rely=0.93,
                                                                          relx=0.05)
    errorLabel = Label(window, font=("Arial", 7), foreground="red", text="Введите имя,\nфамилию и\nномер телефона!")
    Button(window, font=("Arial", 10), text="Сохранить", command=save).place(relheight=0.05, relwidth=0.3, rely=0.93,
                                                                             relx=0.65)

    first_nameEntry.insert(0, persons[2])
    last_nameEntry.insert(0, persons[3])
    address_1Entry.insert(0, persons[4])
    address_2Entry.insert(0, persons[5])
    work_numberEntry.insert(0, persons[6])
    home_numberEntry.insert(0, persons[7])
    indexEntry.insert(0, persons[8])

    window.bind("<Return>", save)
    window.bind("<Escape>", exit)

    window.mainloop()

# функция создаёт окно, в котором можно посмотреть список записей в одной из адресных книг
def active_book(book_id: int, book_name: str, create_date: str):
    # функция закрывает окно
    def exit(func=None):
        nonlocal window

        window.destroy()

        if func:
            func()

    # эта функция вызывается каждый раз при выборе любой записи из списка и показывает в специальных полях все данные из записи
    def selecting(*args):
        nonlocal personsListbox, editButton, deleteButton, firstnameEntry, lastnameEntry, address1Entry, address2Entry, worknumberEntry, homenumberEntry, sorted_persons, flag

        flag = True

        if personsListbox.curselection():
            if editButton["state"] == "disabled":
                editButton.configure(state="active")
            if deleteButton["state"] == "disabled":
                deleteButton.configure(state="active")

            person = sorted_persons[personsListbox.curselection()[0]]

            if firstnameEntry['state'] == "disabled":
                firstnameEntry.configure(state="normal")
            if lastnameEntry['state'] == "disabled":
                lastnameEntry.configure(state="normal")
            if address1Entry['state'] == "disabled":
                address1Entry.configure(state="normal")
            if address2Entry['state'] == "disabled":
                address2Entry.configure(state="normal")
            if worknumberEntry['state'] == "disabled":
                worknumberEntry.configure(state="normal")
            if homenumberEntry['state'] == "disabled":
                homenumberEntry.configure(state="normal")
            if indexEntry['state'] == "disabled":
                indexEntry.configure(state="normal")

            firstnameEntry.delete(0, END)
            lastnameEntry.delete(0, END)
            address1Entry.delete(0, END)
            address2Entry.delete(0, END)
            worknumberEntry.delete(0, END)
            homenumberEntry.delete(0, END)
            indexEntry.delete(0, END)

            firstnameEntry.insert(0, person[2])
            lastnameEntry.insert(0, person[3])
            address1Entry.insert(0, person[4])
            address2Entry.insert(0, person[5])
            worknumberEntry.insert(0, person[6])
            homenumberEntry.insert(0, person[7])
            indexEntry.insert(0, person[8])
        else:
            if editButton["state"] != "disabled":
                editButton.configure(state="disabled")
            if deleteButton["state"] != "disabled":
                deleteButton.configure(state="disabled")

        flag = False

    # функция вызывает функцию, которая позволяет изменить запись в адресной книге
    def prepare_to_edit_person(*args):
        nonlocal personsListbox, persons, book_name, update, selecting

        person = sorted_persons[personsListbox.curselection()[0]]
        edit_person(book_name, *person, func_update=update, func_selecting=selecting)

    # функция удаляет запись из адресной книги
    def delete_person():
        nonlocal personsListbox, persons, selecting, sorted_persons

        select_person = personsListbox.curselection()[0]

        person = sorted_persons[select_person]
        person_name = (person[2] if person[2] else "") + " " + (person[3] if person[3] else "")

        result = askyesno(title=f"Удаление записи об {person_name}",
                          message=f"Вы уверены, что хотите удалить запись о(б) {person_name}?")

        if result:
            cur.execute("DELETE FROM persons WHERE id = ?", (person[0],))
            db.commit()

            persons.remove(person)
            sorted_persons.remove(person)

            showinfo("Запись удалена", message=f"Запись о(б) {person_name} удалена навсегда")

            persons_var.set(list(
                map(lambda x: x[2] + " " + x[3] + " " * 5 + x[-3], sorted_persons)))
            selecting()

    # функция делает поиск записей в адресной книге и cортирует их по имени или фамилиии
    def sort_and_filter(*args):
        nonlocal searchEntry, personsListbox, persons_var, sortedCombobox, sorted_persons, persons

        request = searchEntry.get()
        selection = sortedCombobox.get()

        if request == "":
            if selection == "Имя":
                sorted_persons = sorted(persons, key=lambda x: x[2])
            elif selection == "Фамилия":
                sorted_persons = sorted(persons, key=lambda x: x[3])
        else:
            if selection == "Имя":
                sorted_persons = sorted(filter(lambda x: request.lower() in (x[2] + x[3] + x[4] + x[5] + x[6] + x[7] + x[8]).lower(), persons), key=lambda x: x[2])
            elif selection == "Фамилия":
                sorted_persons = sorted(filter(lambda x: request.lower() in (x[2] + x[3] + x[4] + x[5] + x[6] + x[7] + x[8]).lower(), persons), key=lambda x: x[3])

        persons_var.set(list(
            map(lambda x: x[2] + " " + x[3] + " " * 5 + x[-3], sorted_persons)))

    # функция обновляет список записей в адресной книге
    def update():
        nonlocal persons, persons_var, personsListbox, sortedCombobox, sorted_persons, searchEntry

        cur.execute(
            "SELECT * FROM persons WHERE book_id = ?",
            (book_id,))
        persons = cur.fetchall()

        selection = sortedCombobox.get()
        request = searchEntry.get()

        if request == "":
            if selection == "Имя":
                sorted_persons = sorted(persons, key=lambda x: x[2])
            elif selection == "Фамилия":
                sorted_persons = sorted(persons, key=lambda x: x[3])
        else:
            if selection == "Имя":
                sorted_persons = sorted(
                    filter(lambda x: request.lower() in (x[2] + x[3] + x[4] + x[5] + x[6] + x[7] + x[8]).lower(),
                           persons), key=lambda x: x[2])
            elif selection == "Фамилия":
                sorted_persons = sorted(
                    filter(lambda x: request.lower() in (x[2] + x[3] + x[4] + x[5] + x[6] + x[7] + x[8]).lower(),
                           persons), key=lambda x: x[3])

        persons_var.set(list(
            map(lambda x: x[2] + " " + x[3] + " " * 5 + (x[-3] if x[-3] else x[-2]), sorted_persons)))

    # функция не даёт вставить значения в поле, где отображается информация о записи в адресной книге
    def validate():
        nonlocal flag

        return flag

    cur.execute(
        "SELECT * FROM persons WHERE book_id = ?",
        (book_id,))
    persons = cur.fetchall()
    sorted_persons = sorted(persons, key=lambda x: x[2])

    flag = False

    window = Tk()
    window.title(f"Адресная книга \"{book_name}\"")
    window.geometry("400x550")

    pp_menu = Menu(window, tearoff=0)
    pp_menu.add_command(label="Python Proga")

    help_menu = Menu(window, tearoff=0)
    help_menu.add_cascade(label="Про нас", menu=pp_menu)

    file_menu = Menu(window, tearoff=0)
    file_menu.add_command(label="Добавить новую запись",
                          command=lambda: add_person(book_id, book_name, update, selecting))
    file_menu.add_command(label="Выбрать другую адресную книгу", command=lambda: exit(select_book))
    file_menu.add_command(label="Создать новую адресную книгу", command=lambda: create_new_address_book(dwindow=window))
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=exit)

    main_menu = Menu(window)
    main_menu.add_cascade(label="Файл", menu=file_menu)
    main_menu.add_cascade(label="Помощь", menu=help_menu)

    sortedCombobox = ttk.Combobox(window, values=["Имя", "Фамилия"], font=("Arial", 10), state="readonly")
    sortedCombobox.current(0)
    sortedCombobox.place(relwidth=0.3, relheight=0.035, rely=0.03, relx=0.05)
    sortedCombobox.bind("<<ComboboxSelected>>", sort_and_filter)

    Button(window, text="Поиск:", font=("Arial", 10), command=sort_and_filter).place(relwidth=0.15, relheight=0.035, rely=0.03,
                                                                            relx=0.55)
    searchEntry = Entry(window, font=("Arial", 10))
    searchEntry.place(relwidth=0.20, relheight=0.035, rely=0.03, relx=0.75)
    searchEntry.bind("<Return>", sort_and_filter)

    persons_var = Variable(window, value=list(
        map(lambda x: x[2] + " " + x[3] + " " * 5 + x[-3], sorted_persons)))
    personsListbox = Listbox(window, listvariable=persons_var, font=("Arial", 10))
    personsListbox.place(relwidth=0.35, relheight=0.8, rely=0.1, relx=0.05)
    personsListbox.bind("<<ListboxSelect>>", selecting)
    personsListbox.bind("<Double-Button-1>", prepare_to_edit_person)

    frame = Frame(window)
    frame.place(relwidth=0.5, relheight=0.8, rely=0.1, relx=0.45)

    Label(frame, text="Имя:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.05)
    Label(frame, text="Фамилия:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.18)
    Label(frame, text="Адрес 1:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.31)
    Label(frame, text="Адрес 2:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.44)
    Label(frame, text="Рабочий\nтелефон:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.57)
    Label(frame, text="Домашний\nтелефон:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.7)
    Label(frame, text="Почтовый\nиндекс:", font=("Arial", 10)).place(relwidth=0.35, relheight=0.1, relx=0.05, rely=0.83)

    firstnameEntry = Entry(frame, font=("Arial", 9), justify=LEFT, validate="key", validatecommand=(window.register(validate), ), state="disabled")
    firstnameEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.05)
    lastnameEntry = Entry(frame, font=("Arial", 9), justify=LEFT, validate="key", validatecommand=(window.register(validate), ), state="disabled")
    lastnameEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.18)
    address1Entry = Entry(frame, font=("Arial", 9), justify=LEFT, validate="key", validatecommand=(window.register(validate), ), state="disabled")
    address1Entry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.3)
    address2Entry = Entry(frame, font=("Arial", 9), justify=LEFT, validate="key", validatecommand=(window.register(validate), ), state="disabled")
    address2Entry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.44)
    worknumberEntry = Entry(frame, font=("Arial", 9), justify=LEFT, validate="key", validatecommand=(window.register(validate), ), state="disabled")
    worknumberEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.57)
    homenumberEntry = Entry(frame, font=("Arial", 9), justify=LEFT, validate="key", validatecommand=(window.register(validate), ), state="disabled")
    homenumberEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.7)
    indexEntry = Entry(frame, font=("Arial", 9), justify=LEFT, validate="key", validatecommand=(window.register(validate), ), state="disabled")
    indexEntry.place(relwidth=0.5, relheight=0.1, relx=0.45, rely=0.83)

    Button(window, text="Добавить", font=("Arial", 10),
           command=lambda: add_person(book_id, book_name, update, selecting)).place(
        relheight=0.035, relwidth=0.15, rely=0.935, relx=0.1)
    deleteButton = Button(window, text="Удалить", font=("Arial", 10), state="disabled", command=delete_person)
    deleteButton.place(relheight=0.035, relwidth=0.15, rely=0.935, relx=0.425)
    editButton = Button(window, text="Изменить", font=("Arial", 10), state="disabled", command=prepare_to_edit_person)
    editButton.place(relheight=0.035, relwidth=0.15, rely=0.935, relx=0.75)

    window.config(menu=main_menu)

    window.mainloop()

# функция создаёт окно, в котором можно переименовать адресную книгу
def rename_book(book_id, book_name, book_last_edit_date, func_update, func_select):
    # эта функция вызывается при каждом изменении поля с вводом названия адресной книги и валидирует это поле
    def change_entry(value):
        nonlocal errorLabel, entry

        if value != "":
            if errorLabel.place_info() != {}:
                errorLabel.place_forget()
        else:
            if errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.1, relwidth=0.8, relx=0.1, rely=0.55)

        if len(value) > 18:
            return False

        return True

    #  функция закрывает окно
    def exit(*args):
        nonlocal window

        window.destroy()

    # функция изменяет название адресной книги и закрывает окно
    def save(*args):
        nonlocal window, entry, errorLabel, func_update
        global db, cur

        if entry.get():
            cur.execute("UPDATE books SET name = ?, create_date = ? WHERE id = ?",
                        (entry.get(), datetime.datetime.now().strftime("%Y-%m-%d"), book_id))
            db.commit()

            func_update()
            func_select()

            window.destroy()
        else:
            if errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.1, relwidth=0.8, relx=0.1, rely=0.55)

    window = Tk()
    window.title(f"Переименование адресной книги \"{book_name}\"")
    window.geometry("350x200")

    Label(window, text="Введите новое название адресной книги:", font=("Arial", 10)).place(relheight=0.1, relwidth=0.8,
                                                                                           relx=0.1, rely=0.1)

    entry = Entry(window, font=("Arial", 10), validate="key", validatecommand=(window.register(change_entry), '%P'))
    entry.place(relheight=0.1, relwidth=0.8, relx=0.1, rely=0.3)
    entry.focus()

    entry.bind("<Return>", save)
    entry.bind("<Escape>", exit)

    errorLabel = Label(window, text="Введите название адресной книги!", foreground="red")

    entry.insert(0, book_name)

    Button(window, text="Отмена", command=exit, font=("Arial", 10)).place(relheight=0.1, relwidth=0.2, rely=0.8,
                                                                          relx=0.1)

    Button(window, text="Сохранить", command=save, font=("Arial", 10)).place(relheight=0.1, relwidth=0.2, rely=0.8,
                                                                             relx=0.7)

    window.mainloop()

# функция создаёт окно, в котором можно выбрать адресную книгу
def select_book():
    #  функция закрывает окно
    def exit():
        nonlocal window

        window.destroy()

    # функция вызывается каждый раз при выборе адресной книги из списка
    def selecting(*args):
        nonlocal booksListbox, errorLabel, renameButton, deleteButton

        if booksListbox.curselection():
            if errorLabel.place_info() != {}:
                errorLabel.place_forget()

            if renameButton["state"] == "disabled":
                renameButton.configure(state="active")
            if deleteButton["state"] == "disabled":
                deleteButton.configure(state="active")
        else:
            if errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.1, relwidth=0.6, relx=0.3, rely=0.85)

            if renameButton["state"] != "disabled":
                renameButton.configure(state="disabled")
            if deleteButton["state"] != "disabled":
                deleteButton.configure(state="disabled")

    # функция закрывает окно и вызывает функцию active_book
    def select(*args):
        nonlocal booksListbox, books, window, errorLabel

        if booksListbox.curselection():
            if errorLabel.place_info() != {}:
                errorLabel.place_forget()

            if renameButton["state"] == "disabled":
                renameButton.configure(state="active")
            if deleteButton["state"] == "disabled":
                deleteButton.configure(state="active")

            book = books[booksListbox.curselection()[0]]

            window.destroy()

            active_book(*book)
        else:
            if not args and errorLabel.place_info() == {}:
                errorLabel.place(relheight=0.1, relwidth=0.6, relx=0.3, rely=0.85)

            if renameButton["state"] != "disabled":
                renameButton.configure(state="disabled")
            if deleteButton["state"] != "disabled":
                deleteButton.configure(state="disabled")

    #  # функция вызывает функцию, которая позволяет переименовать адресную книгу
    def prepare_to_rename_book():
        nonlocal booksListbox, books, update, selecting

        book = books[booksListbox.curselection()[0]]
        rename_book(*book, update, selecting)

    # функция удалет адресную книгу
    def delete_book():
        nonlocal booksListbox, books

        select_book = booksListbox.curselection()[0]

        book = books[select_book]

        result = askyesno(title=f"Удаление адресной книги \"{book[1]}\"",
                          message=f"Вы уверены, что хотите удалить адресную книгу \"{book[1]}\"?")

        if result:
            cur.execute("DELETE FROM books WHERE id = ?", (book[0],))
            db.commit()

            showinfo("Адресная книга удалена", message=f"Адресная книга \"{book[1]}\" удалена навсегда")

            booksListbox.delete(select_book)
            selecting()

    # функция обновляет список адресных книг
    def update():
        nonlocal books, books_var

        cur.execute("SELECT * FROM books")
        books = cur.fetchall()

        books_var.set(list(
            map(lambda x: x[1] + " " * 5 + f"Дата создания: {x[2]}", books)))

    window = Tk()
    window.title("Выбор адресной книги")
    window.geometry("350x200")

    Label(window, text="Выберите адресную книгу:", font=("Arial", 10)).place(relheight=0.1, relwidth=0.8,
                                                                             relx=0.1, rely=0.05)

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    books_var = Variable(window, value=list(
        map(lambda x: x[1] + " " * 5 + f"Дата создания: {x[2]}", books)))
    booksListbox = Listbox(window, listvariable=books_var, font=("Arial", 10))
    booksListbox.place(relheight=0.55, relwidth=0.8,
                       relx=0.1, rely=0.2)
    booksListbox.bind("<Return>", select)
    booksListbox.bind("<Double-Button-1>", select)
    booksListbox.bind("<<ListboxSelect>>", selecting)

    Button(window, text="Выбрать", font=("Arial", 10), command=select).place(relheight=0.1, relwidth=0.2, rely=0.85,
                                                                             relx=0.1)

    renameButton = Button(window, text="Переименовать", font=("Arial", 10), state="disabled",
                          command=prepare_to_rename_book)
    renameButton.place(relheight=0.1, relwidth=0.3, rely=0.85, relx=0.35)

    deleteButton = Button(window, text="Удалить", font=("Arial", 10), state="disabled", command=delete_book)
    deleteButton.place(relheight=0.1, relwidth=0.2, rely=0.85, relx=0.7)

    errorLabel = Label(window, text="Выберите адресную книгу!", foreground="red")

    file_menu = Menu(window, tearoff=0)
    file_menu.add_command(label="Создать новую адресную книгу",
                          command=lambda: create_new_address_book(update, selecting))
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=exit)

    main_menu = Menu(window)
    main_menu.add_cascade(label="Файл", menu=file_menu)

    window.config(menu=main_menu)

    window.mainloop()


def main():
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    if books == []:
        create_new_address_book(start=True)
    else:
        select_book()


if __name__ == '__main__':
    main()

if db:
    db.close()