import sqlite3
import tkinter as tk
from tkinter import filedialog, Menu, ttk
import os
import sys
from PIL import Image, ImageTk
import webbrowser
from pygame import mixer
mixer.init()

current_canvas = None

def setCursor(db):
    global conn, cursor
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

DB = "Minecraft"
if getattr(sys, 'frozen', False):
    db_path = os.path.join(sys._MEIPASS, 'databases', f'{DB}.db')
else:
    db_path = os.path.join('databases', f'{DB}.db')
setCursor(db_path)

def play_sound(sfx):
    if getattr(sys, 'frozen', False):
        sfx_path = os.path.join(sys._MEIPASS, sfx)
    else:
        sfx_path = sfx
    try:
        sound = mixer.Sound(sfx_path)
        sound.play()
    except Exception as e:
        print(f"Error playing sound: {e}")

def open_Link(url):
    try:
        webbrowser.open(url)
    except:
        print(f"Could not open URL: {url}")

def printTable(table, cursor):
    cursor.execute(f"SELECT * FROM {table}")
    results = cursor.fetchall()
    for row in results:
        print(row)

def getTable(table, cursor):
    cursor.execute(f"SELECT * FROM {table}")
    results = cursor.fetchall()
    return results

def getAns(cha, cursor):
    cursor.execute(f"SELECT * FROM 'character_answers' WHERE character_id={cha}")
    results = cursor.fetchall()
    return results

def characterDict():
    cursor.execute("SELECT id FROM characters")
    results = cursor.fetchall()
    dictionary = {r[0]: 0 for r in results}
    return dictionary

def addScore(dictionary, current, user_answer):
    cursor.execute(f"SELECT * FROM character_answers WHERE question_id={current+1}")
    results = cursor.fetchall()
    for i in dictionary:
        for r in results:
            try:
                if r[1] == i and r[3] == user_answer:
                    dictionary[i] += 1
                elif r[1] == i and r[3] != user_answer:
                    dictionary[i] -= 1
            except:
                print(r)
    return dictionary

def mostLikely(dictionary, current, rcharacter):
    highScore = 3
    character = None
    #getting top characters
    for i in dictionary:
        if dictionary[i] > highScore and current >= 3:
            highScore = dictionary[i]
            character2 = character
            character = i
        elif dictionary[i] == highScore and current >= 3:
            character2 = i
    #skipping questions
    if character:
        if character2 is None:
            character2 = character
        cursor.execute(f"SELECT question_id, answer FROM character_answers WHERE character_id={character2}")
        results2 = cursor.fetchall()
        cursor.execute(f"SELECT question_id, answer FROM character_answers WHERE character_id={character}")
        results = cursor.fetchall()
        newtrue = False
        while newtrue == False and current < len(results):
            #print(results[current])
            if results[current][1] == 'Y' or results2[current][1] == 'Y':
                newtrue = True
            else:
                current += 1
    #deciding winner or repeat
    if current >= len(getTable('questions', cursor)):
        chalist = getTable('characters', cursor)
        try:
            character = chalist[character-1][1]
        except:
            character = "nobody"
        print(f"You are {character}!")
        rcharacter = character
    return current, rcharacter

def screen_create():
    root = tk.Tk(screenName=None, baseName=None, className='Versefinder', useTk=1)
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    win_w = int(screen_w * 0.48)
    win_h = int(screen_h * 0.48)
    root.geometry(f"{win_w}x{win_h}")
    root.resizable(False, False) 
    
    def on_closing():
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    return root, screen_h, screen_w

def db_Selctor():
    if getattr(sys, 'frozen', False):
        initial_dir = os.path.join(sys._MEIPASS, 'databases')
    else:
        initial_dir = 'databases'
    db_path = filedialog.askopenfilename(
        title="Select database",
        initialdir=initial_dir,
        filetypes=[
            ("SQLite database", "*.db *.sqlite *.sqlite3"),
            ("All files", "*.*")
        ]
    )

    if db_path:
        print("Selected DB:", db_path)
        setCursor(db_path)
    guesser(True)

def topbar():
    menu = Menu(root)
    root.config(menu=menu) 
    filemenu = Menu(menu)
    menu.add_cascade(label='File', menu=filemenu) 
    filemenu.add_command(label='Reset', command = lambda: (guesser(True)))
    filemenu.add_command(label='Open', command = lambda: (db_Selctor()))
    filemenu.add_command(label='Close', command = root.destroy)

    modemenu = Menu(menu)
    menu.add_cascade(label='Modify', menu=modemenu) 
    modemenu.add_command(label='Play', command = lambda: (enable_Edit(False)))
    modemenu.add_separator()
    modemenu.add_command(label='Edit Answers', command = lambda: (enable_Edit(True)))
    modemenu.add_separator()
    modemenu.add_command(label='Create Character', command = lambda: (enable_Create('char')))
    modemenu.add_command(label='Create Question', command = lambda: (enable_Create('ques')))
    modemenu.add_command(label='Create File', command = lambda: (enable_Create('file')))
    modemenu.add_separator()
    modemenu.add_command(label='Deleter', command = lambda: (enable_Create('dele')))

    pagemenu = Menu(menu)
    menu.add_cascade(label='Links', menu=pagemenu) 
    pagemenu.add_command(label='Github', command = lambda: (open_Link("https://github.com/Hicks404")))

def enable_Create(choice = 'none'):
    global create_mode
    create_mode = choice.lower()
    guesser(True)

def enable_Edit(logic = True):
    global edit_mode
    edit_mode = logic
    enable_Create('none')

def comboChange(event, combo):
    name = combo.get()
    chalist = getTable('characters', cursor)
    id = None
    for i in chalist:
        if i[1] == name:
            id = i[0]
    if id:
        id -= 1
        for widget in root.winfo_children():
            widget.destroy()
        quiz_Editor(id)

def changeAns(n, button, cur):
    global anslist
    ans = anslist[n]
    tex = 'U'
    #play_sound('sound/pop.ogg')
    if ans[3] == 'Y':
        cursor.execute(f"UPDATE character_answers SET answer = 'N' WHERE character_id={ans[1]} AND question_id={ans[2]};")
        tex = 'N'
    elif ans[3] == 'N' or ans[3] == 'U':
        cursor.execute(f"UPDATE character_answers SET answer = 'Y' WHERE character_id={ans[1]} AND question_id={ans[2]};")
        tex = 'Y'
    conn.commit()
    button.config(text=tex)
    anslist = getAns(cur+1, cursor)

def Edit_Ans_Listing(content, cur):
    questlist = getTable('questions', cursor)
    global anslist
    anslist = getAns(cur+1, cursor)
    num = 0
    for i in questlist:
        try:
            button = tk.Button(content, text=anslist[num][3], font=("Arial", int(screen_h * 0.02)), width=int(screen_h * 0.01))
            button.config(command=lambda n=num, b=button: changeAns(n, b, cur))
            button.grid(row=num, column=0, padx=5, pady=5)
            tk.Label(content, text=i[1], font=("Arial", int(screen_h * 0.02)), wraplength=screen_w * 0.4, justify="left", anchor="w").grid(row=num, column=1, padx=5, pady=5)
            num += 1
        except:
            tk.Label(content, text="Error. Add more questions or characters", font=("Arial", int(screen_h * 0.02)), wraplength=screen_w * 0.4, justify="left", anchor="w").grid(row=num, column=1, padx=5, pady=5)

def scroller(framed):
    container = tk.Frame(framed)
    container.pack(padx=20, pady=20, fill="both", expand=True)
    canvas = tk.Canvas(container, height=int(screen_h * 0.3))
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    content = tk.Frame(container)
    canvas.create_window((0, 0), window=content, anchor="nw")
    content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    global current_canvas
    current_canvas = canvas
    def _on_mousewheel(event):
        if current_canvas:
            x = root.winfo_pointerx()
            y = root.winfo_pointery()
            cx = current_canvas.winfo_rootx()
            cy = current_canvas.winfo_rooty()
            cw = current_canvas.winfo_width()
            ch = current_canvas.winfo_height()
            if cx <= x < cx + cw and cy <= y < cy + ch:
                current_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    root.bind_all("<MouseWheel>", _on_mousewheel)

    return content 

def quiz_Editor(cur = 0):
    topbar()
    chalist = getTable('characters', cursor)
    options = [cha[1] for cha in chalist]

    combo = ttk.Combobox(root, values=options, state="readonly", font=("Arial", int(screen_h * 0.02)), width=int(screen_h * 0.03))
    combo.pack(padx=10, pady=10)
    combo.current(cur)
    combo.bind("<<ComboboxSelected>>", lambda event: comboChange(event, combo))

    content = scroller(root)

    Edit_Ans_Listing(content, cur)

    root.mainloop()

def submit_Char(name_entry):
    name = name_entry.get()
    chalist = getTable('characters', cursor)
    for i in chalist:
        if i[1].lower() == name.lower():
            return

    cursor.execute(f"INSERT INTO characters (id, name) VALUES ('{len(chalist)+1}','{name}');")
    conn.commit()

    anslist = getTable('characters', cursor)
    quest_id = 1
    for i in getTable('questions', cursor):
        cursor.execute(f"INSERT INTO character_answers (character_id, question_id, answer) VALUES ({anslist[-1][0]}, {quest_id}, 'N');")
        quest_id += 1
    conn.commit()

    guesser(True)

def submit_Ques(ques):
    question = ques.get()
    questlist = getTable('questions', cursor)
    for i in questlist:
        if i[1].lower() == question.lower():
            return

    cursor.execute(f"INSERT INTO questions (id, text) VALUES ('{len(questlist)+1}','{question}');")
    conn.commit()

    anslist = getTable('characters', cursor)
    for cha in anslist:
        cursor.execute(f"INSERT INTO character_answers (character_id, question_id, answer) VALUES ({cha[0]}, {len(questlist)+1}, 'N');")
    conn.commit()

    guesser(True)

def submit_File(file_path):
    name = file_path.get().strip()
    if not name:
        return
    db_path = f'databases/{name}.db' #path
    if os.path.exists(db_path):
        return
    
    conn_new = sqlite3.connect(db_path) #database tables
    cursor_new = conn_new.cursor()
    cursor_new.execute('''CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY,
        name TEXT
    )''')
    cursor_new.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        text TEXT
    )''')
    cursor_new.execute('''CREATE TABLE IF NOT EXISTS character_answers (
        id INTEGER PRIMARY KEY,
        character_id INTEGER,
        question_id INTEGER,
        answer TEXT
    )''')
    conn_new.commit()
    conn_new.close()
    
    guesser(True)

def c_UI(row = 0, col = 0, txt = "Name: "):
    tk.Label(root, text=txt, font=("Arial", int(screen_h * 0.025)), wraplength=screen_w*0.1, anchor="w").grid(row=row, column=col, padx=10, pady=10, sticky='ew')
    form = tk.Entry(root, font=("Arial", int(screen_h * 0.025)), width=int(screen_w * 0.013))
    form.grid(row=row, column=col+1, padx=10, pady=10, sticky='ew')
    return form

def table_display(table, cursor, row):
    container = tk.Frame(root)
    container.grid(padx=20, pady=20, row=row, column=1, sticky='nsew')
    content = scroller(container)
    num = 0
    charlist = getTable(table, cursor)
    for i in charlist:
        tk.Label(content, text=f"{num+1}. {i[1]}", font=("Arial", int(screen_h * 0.02)), wraplength=screen_w*0.4, anchor="w").grid(row=num+5, column=0, padx=10, pady=5, sticky='w')
        num += 1

def char_Create():
    topbar()
    form = c_UI()
    button = tk.Button(root, text='Create', font=("Arial", int(screen_h * 0.02)), width=int(screen_w * 0.01), command=lambda: submit_Char(form))
    button.grid(row=1, column=1, sticky='w', padx=5, pady=5)

    tk.Label(root, text="Already existing characters:", font=("Arial", int(screen_h * 0.025)), wraplength=screen_w*0.1, anchor="w").grid(row=3, column=0, padx=10, pady=10, sticky='ew')
    table_display('characters', cursor, 3)

    root.mainloop()

def ques_Create():
    topbar()
    form = c_UI()
    button = tk.Button(root, text='Create', font=("Arial", int(screen_h * 0.02)), width=int(screen_w * 0.01), command=lambda: submit_Ques(form))
    button.grid(row=1, column=1, sticky='w', padx=5, pady=5)

    tk.Label(root, text="Already existing questions:", font=("Arial", int(screen_h * 0.025)), wraplength=screen_w*0.1, anchor="w").grid(row=3, column=0, padx=10, pady=10, sticky='ew')
    table_display('questions', cursor, 3)

    root.mainloop()

def file_Create():
    topbar()
    form = c_UI()
    button = tk.Button(root, text='Create', font=("Arial", int(screen_h * 0.02)), width=int(screen_w * 0.01), command=lambda: submit_File(form))
    button.grid(row=1, column=1, sticky='w', padx=5, pady=5)
    #tk.Label(root, text="You won't be automatically set to the new file.", font=("Arial", int(screen_h * 0.015)), wraplength=screen_w*0.1, anchor="w").grid(row=3, column=1, padx=10, pady=10, sticky='w')
    tk.Label(root, text="Already existing database files:", font=("Arial", int(screen_h * 0.025)), wraplength=screen_w*0.1, anchor="w").grid(row=3, column=0, padx=10, pady=10, sticky='ew')
    container = tk.Frame(root)
    container.grid(padx=20, pady=20, row=3, column=1, sticky='nsew')
    content = scroller(container)
    num = 0
    filelist = [f for f in os.listdir("databases") if f.endswith('.db')]
    for i in filelist:
        tk.Label(content, text=f"{num+1}. {i}", font=("Arial", int(screen_h * 0.02)), wraplength=screen_w*0.4, anchor="w").grid(row=num+5, column=0, padx=10, pady=5, sticky='w')
        num += 1

    root.mainloop()

def deleteChange(event, combo):
    name = combo.get()
    if name == 'characters':
        deleter_Mode(0)
    elif name == 'questions':
        deleter_Mode(1)

def deleter(form, choice):
    if choice == 'characters':
        cursor.execute(f"DELETE FROM characters WHERE id={form.get()};")
        cursor.execute(f"DELETE FROM character_answers WHERE character_id={form.get()};")
    elif choice == 'questions':
        cursor.execute(f"DELETE FROM questions WHERE id={form.get()};")
        cursor.execute(f"DELETE FROM character_answers WHERE question_id={form.get()};")
    conn.commit()
    deleter_Mode(0 if choice == 'characters' else 1)

def deleter_Mode(col = 0):
    topbar()
    tk.Label(root, text="Option: ", font=("Arial", int(screen_h * 0.025)), wraplength=screen_w*0.1, anchor="w").grid(row=0, column=0, padx=10, pady=10, sticky='ew')
    options = ['characters', 'questions']
    combo = ttk.Combobox(root, values=options, state="readonly", font=("Arial", int(screen_h * 0.02)), width=int(screen_h * 0.03))
    combo.grid(row=0, column=1, padx=10, pady=10)
    combo.current(col)
    combo.bind("<<ComboboxSelected>>", lambda event: deleteChange(event, combo))

    form = c_UI(1, 0, "Num ID: ")

    button = tk.Button(root, text='Delete', font=("Arial", int(screen_h * 0.02)), width=int(screen_w * 0.01), command=lambda: deleter(form, combo.get()))
    button.grid(row=2, column=1, sticky='w', padx=5, pady=5)

    table_display(combo.get(), cursor, 3)

    root.mainloop()

def setAns(ans):
    global answer
    answer = ans

def quiz_GUI():
    question_label = tk.Label(root, text="", font=("Arial", int(screen_h * 0.035)), wraplength=screen_w*0.4)
    question_label.grid(row=1, column=0, padx=5, pady=10)
    button = tk.Button(root, text='Yes', font=("Arial", int(screen_h * 0.02)), width=int(screen_h * 0.04), command=lambda: setAns('Y'))
    button.grid(row=2, column=0, sticky='w', padx=5, pady=5)
    button2 = tk.Button(root, text='No', font=("Arial", int(screen_h * 0.02)), width=int(screen_h * 0.04), command=lambda: setAns('N'))
    button2.grid(row=3, column=0, sticky='w', padx=5, pady=5)
    button3 = tk.Button(root, text='Unsure', font=("Arial", int(screen_h * 0.02)), width=int(screen_h * 0.04), command=lambda: setAns('U'))
    button3.grid(row=4, column=0, sticky='w', padx=5, pady=5)
    return question_label, button, button2, button3

def title():
    db_file = cursor.execute("PRAGMA database_list").fetchone()[2]
    DB = os.path.splitext(os.path.basename(db_file))[0]
    title = tk.Label(root, text=DB, font=("Arial", int(screen_h * 0.05)), border=2, relief="solid", wraplength=screen_w*0.4)
    title.grid(row=0, column=0, padx=5, pady=10)

def quiz_Player():
    global answer
    topbar()
    title()
    question_label, button, button2, button3 = quiz_GUI()

    #guesser logic
    questions = getTable('questions', cursor)
    current = 0
    character = None
    possible = characterDict()
    while character is None:
        #print(questions[current][1])
        #print(possible)
        question_label.config(text=questions[current][1])
        answer = None
        while answer is None:
            root.update()
        play_sound('sound/blow.ogg')
        possible = addScore(possible, current, answer)
        current += 1
        current, character = mostLikely(possible, current, character)

    question_label.config(text=f"You are {character}!")
    button.destroy()
    button2.destroy()
    button3.destroy()
    #button4 = tk.Button(root, text='Exit', font=("Arial", int(screen_h * 0.015)), width=int(screen_h * 0.02), command=root.destroy())
    #button4.grid(row=1, column=0)
    play_sound('sound/hard.ogg')
    if root.winfo_exists():
        root.mainloop()

def guesser(clear = False):
    play_sound('sound/swing.ogg')
    if clear:
        for widget in root.winfo_children():
            widget.destroy()
    #icon
    try:
        icon_path = 'icon.jpg'
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, 'icon.jpg')
        img = Image.open(icon_path)
        p1 = ImageTk.PhotoImage(img)
        root.iconphoto(True, p1)
    except Exception as e:
        print(f"Could not load icon: {e}")

    if edit_mode == False and create_mode == 'none':
        quiz_Player()
    elif edit_mode == True and create_mode == 'none':
        quiz_Editor()
    elif create_mode == 'char':
        char_Create()
    elif create_mode == 'ques':
        ques_Create()
    elif create_mode == 'file':
        file_Create()
    elif create_mode == 'dele':
        deleter_Mode()

if __name__ == "__main__":
    root, screen_h, screen_w = screen_create()
    edit_mode = False
    create_mode = 'none'
    guesser()