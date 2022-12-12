import tkinter as tk
from tkinter.ttk import Scrollbar, Style
from tkinter.filedialog import askopenfile, asksaveasfile
from tkinter.messagebox import showwarning
from os.path import basename
from re import finditer

FILETYPE={'filetypes': [('Text files', '*.txt')], 'defaultextension': '.txt'}

class Editor:
    def __init__(self):
        self.root=tk.Tk()
        self.root.geometry("1080x600")
        self.root.resizable('no', 'no') 
        self.root.title("Text editor") 

        style=Style(self.root)
        self.root.tk.call('source', './awthemes/awdark.tcl')
        style.theme_use('awdark')

        # Scroll
        self.scroll=Scrollbar(self.root)
        self.scroll.pack(side='right', fill='y')

        # Text space
        self.text=tk.Text(self.root, yscroll=self.scroll.set, 
                            wrap='word', font=("Gill Sans", "12"),
                            undo=True)
        self.text.pack(fill='both', expand='TRUE')
        self.scroll.config(command=self.text.yview)

        ## Menus
        self.menu=tk.Menu(self.root)

        # File menu
        self.files=tk.Menu(self.menu, tearoff=0)
        self.root.config(menu=self.menu)

        self.files.add_command(label="New file", command=self.new_file, accelerator='Ctrl + n')
        self.files.add_command(label="New window", command=new_editor, accelerator='Ctrl + Shift + n')
        self.files.add_command(label="Open file", command=self.open_file, accelerator='Ctrl + o')
        self.files.add_command(label="Save as", command=self.save_file, accelerator='Ctrl + s')
        self.files.add_separator()
        self.files.add_command(label="Exit", command=self.root.destroy)

        self.menu.add_cascade(label="File", menu=self.files)

        # Edit menu
        self.edit=tk.Menu(self.menu, tearoff=0)

        self.edit.add_command(label="Find", command=self.find, accelerator='Ctrl + f')

        self.menu.add_cascade(label="Edit", menu=self.edit)
        

        self._shortcuts()

    def save_file(self, *_):
        with asksaveasfile(**FILETYPE, initialfile=self.root.title(), parent=self.root) as file:
            file.write(self.text.get("1.0", 'end'))
            self.root.title(basename(file.name))

    def open_file(self, *_):
        with askopenfile(**FILETYPE, parent=self.root) as file:
            self.text.delete("1.0", 'end')
            self.text.insert("1.0", file.read())
            self.root.title(basename(file.name))

    def new_file(self, *_):
        self.text.delete("1.0", 'end')
        self.root.title("New file")

    # finds string in text
    def find(self, *_):
        window=tk.Toplevel(self.root, takefocus=True)
        window.geometry("400x90")
        window.resizable('no', 'no')
        window.attributes('-topmost', 'true')
        window.title("Find word")

        casesens=tk.IntVar()
        casecheck=tk.Checkbutton(window, text="Case sensitive", variable=casesens)
        casecheck.pack(side='bottom', anchor='w')

        tk.Label(window, text="Find: ").pack(side='left', pady=5)

        entry=tk.Entry(window, textvariable=tk.StringVar())
        entry.pack(side='left', fill='x', expand=True, pady=5, padx=5)
        entry.focus()
        entry.bind('<Return>', lambda _: highlight())

        button=tk.Button(window, text='Find next', width=10, command=lambda: highlight('r'))
        button.pack(side='top', anchor='e', pady=5)

        button2=tk.Button(window, text='Find previous', width=10, command=lambda: highlight())
        button2.pack(side='top', anchor='e')
        
        point=None

        # higlights string in text
        def highlight(dire=None):
            nonlocal point
                
            try:
                word=entry.get()
                text=self.text.get(1.0, 'end')

                if casesens.get() == 0:
                    text=text.lower()
                    word=word.lower()
                
                if dire:
                    index1=text.index(word, point)
                    point=index1 + len(word)
                else:
                    index1=text.rindex(word, 0, point)
                    point=index1

                self.text.tag_delete('mark')
                self.text.tag_add('mark', f'1.{index1}', f'1.{index1 + len(word)}')
                self.text.tag_config('mark', background='gray', foreground='#252525')
                
            except:
                if self.text.get(1.0, 'end').find(word) == -1:
                    showwarning("No matches", "No matches found!")
                else:
                    point=None
                    if dire:
                        highlight('r')
                    else:
                        highlight()

    def replace_all(self, *_):
        text=self.text.get(1.0, 'end')
        index1=self.text.tag_ranges(self.text.tag_names())
        highlighted=self.text.get(index1[0], index1[1])

        # higlights all instances of string in text
        def highlight_all():
            indexes=finditer(highlighted, text)
            for index in indexes:
                self.text.tag_add('mark', f'1.{index.start()}', f'1.{index.end()}')
                self.text.tag_config('mark', background='gray', foreground='#252525')

        def replacefun():
            nonlocal text 
            text=text.replace(highlighted, entry.get())
            self.text.delete(1.0, 'end')
            self.text.insert(1.0, text)

        highlight_all()
    
        entry=tk.Entry(self.root, textvariable=tk.StringVar(), font=("Gill Sans", "10"))
        entry.pack(side='left', fill='x', expand=True, pady=5)
        entry.focus()
        entry.bind("<Return>", lambda _: replacefun())
        self.text.bind('<ButtonPress>', lambda _: entry.destroy(), add='+')

    def _clear_tags(self, *_):
        for tag in self.text.tag_names():
            self.text.tag_delete(tag)

    def _shortcuts(self):
        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-Lock-O>', self.open_file)

        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-Lock-S>', self.save_file)

        self.root.bind('<Control-Shift-N>', new_editor)

        self.root.bind('<Control-n>', self.new_file)
        self.root.bind('<Control-Lock-N>', self.new_file)

        self.root.bind("<Control-f>", self.find)
        self.root.bind('<Control-Lock-F>', self.find)

        self.text.bind("<ButtonPress>", self._clear_tags, add='+')
        self.text.bind("<KeyPress>", self._clear_tags, add='+')
        self.root.bind("<F2>", self.replace_all)


def new_editor():
    new = Editor()
    new.text.focus()
    new.root.mainloop()

if __name__ == "__main__":
    new_editor()
