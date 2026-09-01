import customtkinter as ctk

# region Setup

Config = {
    "Appearance": "dark",
    "Text_Color": "#A500F2",
    "Background_Color": "#201020",
}

ctk.set_appearance_mode(Config["Appearance"])

undo_history = []

Current_File = None

TextFont = "JetBrains Mono"

# region Global Functions

def File_Picker():
    File_Path = ctk.filedialog.askopenfilename(title="Select a File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    return File_Path

def Popup(Message, Button_Text):
    Popup_Window = ctk.CTkToplevel()
    Popup_Window.title("🦊 ATTENTION 🦊")
    Popup_Window.geometry("400x200")

    Message_Label = ctk.CTkLabel(Popup_Window, text=Message, font=("Arial", 20), wraplength=400, justify="center")
    Message_Label.pack(fill="x", expand=True, pady=20)

    if Button_Text is not None:
        Close_Button = ctk.CTkButton(Popup_Window, text=Button_Text, width=100, height=50, font=("Arial", 28), corner_radius=0, fg_color="black", hover_color="gray", command=Popup_Window.destroy)
        Close_Button.pack(side="bottom", fill="x")

def Load_Text(Text_Editor):
    global Current_File
    File_Location = File_Picker()
    if File_Location:
        try:
            with open(File_Location, "r", encoding="utf-8") as File:
                Text_Content = File.read()
                Text_Editor.delete("1.0", "end")
                Text_Editor.insert("1.0", Text_Content)
                Current_File = File_Location
                Popup("File Loaded Successfully!", "Okay :3")
                return Current_File
        except Exception as e:
            Popup(f"Failed to load file: {e}", "Okay :3")
    else:
        Popup("No file selected.", "Okay :3")

def Save_Text(event, Text_Editor, Force_Save_As=False):
    global Current_File
    Text_Content = Text_Editor.get("1.0", "end-1c") 

    if Current_File and not Force_Save_As:
        File_Location = Current_File
    else:
        File_Location = ctk.filedialog.asksaveasfilename(
            title="Save File", 
            defaultextension=".txt", 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

    # Print this to your terminal to check the exact path
    print(f"DEBUG: Attempting to save to -> {File_Location}")

    if File_Location:
        try:
            with open(File_Location, "w", encoding="utf-8") as File:
                File.write(Text_Content)
            Current_File = File_Location
            Popup("File Saved Successfully!", "Okay :3")
        except Exception as e:
            Popup(f"Error: {e}", "Okay :3")
    else:
        Popup("Oh, guess you didn't want to save then...", "Okay :3")

def select_all(event, Text_Editor):
    Text_Editor.tag_add("sel", "1.0", "end")
    return "break"  # Prevents the literal 'a' character from being typed

def delete_word_back(event, Text_Editor):
    text_content = Text_Editor.get("1.0", "insert")
    if not text_content:
        return "break"
        
    stripped_len = len(text_content) - len(text_content.rstrip(" \t"))
    if stripped_len > 0:
        start_idx = f"insert - {stripped_len} chars"
    else:
        idx = max(text_content.rfind(" "), text_content.rfind("\n"))
        if idx == -1:
            start_idx = "1.0"
        else:
            start_idx = f"1.0 + {idx + 1} chars"
            
    Text_Editor.delete(start_idx, "insert")
    return "break"

def record_history(event, Text_Editor):
    global undo_history
    current_text = Text_Editor.get("1.0", "end-1c")
    
    # Check if the event was a space, return, or punctuation boundary, 
    # OR if the history list is empty. This groups typing into words/phrases 
    # instead of capturing every single individual letter.
    keysym = getattr(event, 'keysym', '')
    is_boundary = keysym in ('space', 'Return', 'BackSpace', 'period', 'comma', 'exclam', 'question')
    
    if not undo_history:
        undo_history.append(current_text)
        return

    # If it's a boundary or a significant change, push a new state
    if undo_history[-1] != current_text:
        if is_boundary or abs(len(current_text) - len(undo_history[-1])) > 1:
            undo_history.append(current_text)
            if len(undo_history) > 20:
                undo_history.pop(0)
        else:
            # Otherwise, update the current tip of the history stack so typing flows together
            undo_history[-1] = current_text

def undo_text(event, Text_Editor):
    global undo_history
    if len(undo_history) > 1:
        # 1. Pop the current state
        undo_history.pop()
        previous_text = undo_history[-1]
        
        # 2. Update text content
        Text_Editor.delete("1.0", "end")
        Text_Editor.insert("1.0", previous_text)
        
        # 3. Move cursor to the END of the restored text block (like standard editors)
        Text_Editor.mark_set("insert", "end-1c")
        Text_Editor.see("insert")
            
    return "break"

def Safe_Exit(Window, Text_Editor):
    Popup_Window = ctk.CTkToplevel()
    Popup_Window.title("🦊 ATTENTION 🦊")
    Popup_Window.geometry("500x300")

    Message_Label = ctk.CTkLabel(Popup_Window, text="You should probably save if you haven't yet!", font=("Arial", 20), wraplength=400, justify="center")
    Message_Label.pack(fill="x", expand=True, pady=20)

    Close_Button = ctk.CTkButton(Popup_Window, text="No thanks, I probably saved already :3", width=100, height=50, font=("Arial", 24), corner_radius=0, fg_color="black", hover_color="gray", command=lambda: Popup_Window.destroy() or Window.destroy())
    Close_Button.pack(side="bottom", fill="x")

    Close_Button2 = ctk.CTkButton(Popup_Window, text="Oh yeah, I will do that :3", width=100, height=50, font=("Arial", 24), corner_radius=0, fg_color="black", hover_color="gray", command=lambda: Popup_Window.destroy() or Save_Text(None, Text_Editor) or Window.after(100, Window.destroy()))
    Close_Button2.pack(side="bottom", fill="x")

def Find_Text(event, Text_Editor):
    Find_Window = ctk.CTkToplevel()
    Find_Window.title("🦊 Find 🦊")
    Find_Window.geometry("400x150")
    Find_Window.grab_set()

    Entry = ctk.CTkEntry(Find_Window, width=300, font=("Arial", 20))
    Entry.pack(pady=20)
    Entry.focus()

    def execute_search():
        query = Entry.get()
        if not query:
            return
        
        content = Text_Editor.get("1.0", "end-1c")
        pos = content.find(query)
        
        if pos != -1:
            # Convert string index to Tkinter text index format (line.char)
            row = content.count("\n", 0, pos) + 1
            col = pos if row == 1 else pos - content.rfind("\n", 0, pos) - 1
            idx = f"{row}.{col}"
            
            # Move cursor and highlight matched word temporarily using tag
            Text_Editor.tag_remove("match", "1.0", "end")
            end_idx = f"{row}.{col + len(query)}"
            Text_Editor.tag_add("match", idx, end_idx)
            Text_Editor.tag_config("match", background="yellow", foreground="black")
            
            Text_Editor.mark_set("insert", idx)
            Text_Editor.see(idx)
            Find_Window.destroy()
        else:
            Popup("Phrase not found!", "Okay :3")

    Search_Button = ctk.CTkButton(Find_Window, text="Find", font=("Arial", 20), command=execute_search)
    Search_Button.pack(pady=5)
    
    # Allow pressing Enter to search
    Entry.bind("<Return>", lambda e: execute_search())

def Adjust_Font_Size(Text_Editor, Delta, Minimum=14):
    try:
        Current_Font = Text_Editor.cget("font")
        New_Size = max(Minimum, int(Current_Font[1]) + Delta)
        Text_Editor.configure(font=(TextFont, New_Size))
    except (TypeError, IndexError, ValueError):
        # cget("font") didn't return an indexable (Family, Size) tuple, so skip silently
        pass

def Clear_Text(Text_Editor):
    # Honestly, I have no idea whwy anyone would want to have this here. The chances of pressing this on accident is very high ngl.
    record_history(None, Text_Editor)
    Text_Editor.delete("1.0", "end")

def update_stats(event, Text_Editor, Status_Label):
    content = Text_Editor.get("1.0", "end-1c")
    # Split across any whitespace (spaces, tabs, newlines) to get real word tokens
    words = len(content.split()) if content.strip() else 0
    chars = len(content)
    Status_Label.configure(text=f"Words: {words} | Chars: {chars}")

# endregion

# endregion



def Main():
    Window = ctk.CTk()
    Window.title("Fuffy Furry Text Editor :3")
    Window.geometry("1200x800")

    Options_Bar = ctk.CTkFrame(Window, width=200, height=50, corner_radius=0)
    Options_Bar.pack(side="top", fill="x")

    Save_Button = ctk.CTkButton(Options_Bar, text="Save", width=100, height=50, font=("Arial", 28), corner_radius=0, fg_color="black", hover_color="gray", command=lambda: Save_Text(None, Text_Editor))
    Save_Button.pack(side="left", fill="y")

    Save_As_Button = ctk.CTkButton(Options_Bar, text="Save As", width=100, height=50, font=("Arial", 28), corner_radius=0, fg_color="black", hover_color="gray", command=lambda: Save_Text(None, Text_Editor, Force_Save_As=True))
    Save_As_Button.pack(side="left", fill="y", padx=5)

    Load_Button = ctk.CTkButton(Options_Bar, text="Load", width=100, height=50, font=("Arial", 28), corner_radius=0, fg_color="black", hover_color="gray", command=lambda: Load_Text(Text_Editor))
    Load_Button.pack(side="left", fill="y")

    Clear_Button = ctk.CTkButton(Options_Bar, text="Clear", width=100, height=50, font=("Arial", 28), corner_radius=0, fg_color="black", hover_color="gray", command=lambda: Clear_Text(Text_Editor))
    Clear_Button.pack(side="right", fill="y")

    Stats_Label = ctk.CTkLabel(
        Options_Bar,
        text="Words: 0 | Chars: 0",
        font=("Arial", 16),
        text_color="#A500F2"
    )
    Stats_Label.pack(side="right", padx=15)

    Text_Editor = ctk.CTkTextbox(Window, width=1200, height=750, font=(TextFont, 28), wrap="word", corner_radius=0, fg_color=Config["Background_Color"], text_color=Config["Text_Color"])
    Text_Editor.pack(side="bottom", fill="both", expand=True)

    # region bindings

    Window.protocol("WM_DELETE_WINDOW", lambda: Safe_Exit(Window, Text_Editor))

    Text_Editor.bind("<Control-a>", lambda event: select_all(event, Text_Editor))
    Text_Editor.bind("<Control-A>", lambda event: select_all(event, Text_Editor))

    Text_Editor.bind("<Control-BackSpace>", lambda event: delete_word_back(event, Text_Editor))

    Text_Editor.bind("<Control-s>", lambda event: Save_Text(event, Text_Editor))
    Text_Editor.bind("<Control-S>", lambda event: Save_Text(event, Text_Editor))

    Text_Editor.bind("<KeyRelease>", lambda e: [record_history(e, Text_Editor), update_stats(e, Text_Editor, Stats_Label)])

    Text_Editor.bind("<Control-z>", lambda event: undo_text(event, Text_Editor))
    Text_Editor.bind("<Control-Z>", lambda event: undo_text(event, Text_Editor))

    Text_Editor.bind("<Control-f>", lambda event: Find_Text(event, Text_Editor))
    Text_Editor.bind("<Control-F>", lambda event: Find_Text(event, Text_Editor))

    Text_Editor.bind("<Control-equal>", lambda event: Adjust_Font_Size(Text_Editor, 2))
    Text_Editor.bind("<Control-minus>", lambda event: Adjust_Font_Size(Text_Editor, -2))

    Text_Editor.bind("<Control-plus>", lambda event: Adjust_Font_Size(Text_Editor, 5))
    Text_Editor.bind("<Control-underscore>", lambda event: Adjust_Font_Size(Text_Editor, -5))
    # endregion

    Window.mainloop()

Main()
