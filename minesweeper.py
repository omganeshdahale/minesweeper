from tkinter import *
from random import randint
from PIL import Image, ImageTk
import pygame

WIDTH = 9
HEIGHT = 9
TOTAL_MINES = 8
TOTAL_NON_MINES = WIDTH * HEIGHT - TOTAL_MINES
total_revealed_sq = 0

COL = {
    1:'blue', 
    2:'green', 
    3:'orange', 
    4:'dark blue', 
    5:'brown', 
    6:'cyan', 
    7:'purple', 
    8:'black'
}
flag_count = 0

pygame.mixer.init()

root = Tk()
root.title('Minesweeper')
icon = PhotoImage(file="img/bomb.png")
root.iconphoto(True, icon)
root.resizable(width=False, height=False)

## gui
happy_img = Image.open("img/happy.png")
happy_img.thumbnail((64,64))
happy_img = ImageTk.PhotoImage(happy_img)
dead_img = Image.open("img/dead.png")
dead_img.thumbnail((64,64))
dead_img = ImageTk.PhotoImage(dead_img)
cool_img = Image.open("img/cool.png")
cool_img.thumbnail((64,64))
cool_img = ImageTk.PhotoImage(cool_img)

utility_frame = Frame(root)
flag_label = Label(
    utility_frame, text=flag_count, bg='black', 
    fg='red', font=('San Serif', 24, 'bold'))
smiley = Button(utility_frame,image=happy_img)
utility_frame.pack(side=TOP, fill=X, expand=1)
flag_label.pack(side=LEFT, fill=BOTH, expand=1)
smiley.pack(side=RIGHT, fill=Y)

board_frame = Frame(root)
board_frame.pack()

class Square(Button):
    flag_img = Image.open("img/flag.png")
    flag_img.thumbnail((29,29))
    flag_img = ImageTk.PhotoImage(flag_img)
    
    def __init__(self, master=None, value=0, r=0, c=0, cnf={}, **kw):
        cnf.update(kw)
        super().__init__(master, cnf)
        self.value = value
        self.r = r
        self.c = c
        self.flagged = False
        
        self.config(command=self.on_click)
        self.bind('<Button-3>', self.flag)
    
    def on_click(self):
        pygame.mixer.music.load("audio/click.wav")
        pygame.mixer.music.play()

        if self.value == -1 and not self.flagged:
            # on game over
            pygame.mixer.music.load("audio/explosion.wav")
            pygame.mixer.music.play()

            smiley.config(image=dead_img)
            self.config(bg='red')
            end_game()
            
        else:
            self.spread()
            if total_revealed_sq >= TOTAL_NON_MINES:
                # on win
                pygame.mixer.music.load("audio/win.wav")
                pygame.mixer.music.play()

                smiley.config(image=cool_img)
                end_game()
                            
    def spread(self):
        global total_revealed_sq
        
        if (self.value == 0 and self.cget('state') != DISABLED and
                not self.flagged):
            # open neighbor non mine Squares
            self.config(relief=RIDGE, state=DISABLED, image='')
            self.unbind('<Button-3>')
            total_revealed_sq += 1
            
            if self.r != 0:
                #check top element
                sqr = board[self.r-1][self.c]
                sqr.spread()
                    
            if self.r != HEIGHT-1:
                #check bottom element
                sqr = board[self.r+1][self.c]
                sqr.spread()
                
            if self.c != 0:
                #check left element
                sqr = board[self.r][self.c-1]
                sqr.spread()
                
            if self.c != WIDTH-1:
                #check right element
                sqr = board[self.r][self.c+1]
                sqr.spread()

            ## diagonal
            if self.r != 0 and self.c != 0:
                #check NW element
                sqr = board[self.r-1][self.c-1]
                sqr.spread()

            if self.r != 0 and self.c != WIDTH-1:
                #check NE element
                sqr = board[self.r-1][self.c+1]
                sqr.spread()

            if self.r != HEIGHT-1 and self.c != 0:
                #check SW
                sqr = board[self.r+1][self.c-1]
                sqr.spread()

            if self.r != HEIGHT-1 and self.c != WIDTH-1:
                #check SE
                sqr = board[self.r+1][self.c+1]
                sqr.spread()
            
        elif self.cget('state') != DISABLED and not self.flagged:
            self.config(
                text=self.value, disabledforeground=COL[self.value],
                relief=RIDGE, state=DISABLED, image='')
            self.unbind('<Button-3>')
            total_revealed_sq += 1

    def flag(self, ev):
        global flag_count

        pygame.mixer.music.load("audio/flag.wav")
        pygame.mixer.music.play()
        
        if self.flagged:
            self.config(image='', width=2)
            self.flagged = False
            flag_count -= 1
            flag_label.config(text=flag_count)
        else:
            self.config(image=self.flag_img, width=0)
            self.flagged = True
            flag_count += 1
            flag_label.config(text=flag_count)


def create(cnf={}, **kw):
    """generates board data and gui"""

    global board

    cnf.update(kw)
    ## generating board
    board =[]
    for r in range(HEIGHT):
        board.append([])
        for c in range(WIDTH):
            sqr = Square(board_frame, 0, r, c, cnf)
            sqr.grid(row=r, column=c, sticky=N+S+E+W)
            board[-1].append(sqr)

    ## generating Mines
    if TOTAL_MINES < WIDTH*HEIGHT:
        for b in range(TOTAL_MINES):
            while True:
                r = randint(0,HEIGHT-1)
                c = randint(0,WIDTH-1)
                if board[r][c].value == 0:
                    board[r][c].value = -1
                    break

    ## calculating neighbor Mines
    for r in range(HEIGHT):
        for c in range(WIDTH):
            if board[r][c].value != -1:
                neighbors = 0
                ## vertical and horizontal
                if r != 0:
                    #check top element
                    if board[r-1][c].value == -1:
                        neighbors += 1
                        
                if r != HEIGHT-1:
                    #check bottom element
                    if board[r+1][c].value == -1:
                        neighbors += 1
                    
                if c != 0:
                    #check left element
                    if board[r][c-1].value == -1:
                        neighbors += 1
                    
                if c != WIDTH-1:
                    #check right element
                    if board[r][c+1].value == -1:
                        neighbors += 1

                ## diagonal
                if r != 0 and c != 0:
                    #check NW element
                    if board[r-1][c-1].value == -1:
                        neighbors += 1

                if r != 0 and c != WIDTH-1:
                    #check NE element
                    if board[r-1][c+1].value == -1:
                        neighbors += 1

                if r != HEIGHT-1 and c != 0:
                    #check SW
                    if board[r+1][c-1].value == -1:
                        neighbors += 1

                if r != HEIGHT-1 and c != WIDTH-1:
                    #check SE
                    if board[r+1][c+1].value == -1:
                        neighbors += 1

                board[r][c].value = neighbors

def destroy():
    """destroys board data and gui"""

    for sqr in board_frame.winfo_children():
        sqr.destroy()

def restart():
    """resets game data, destroy gui and regenerate it"""

    global total_revealed_sq, flag_count

    total_revealed_sq = 0
    flag_count = 0
    destroy()
    create()
    smiley.config(image=happy_img)
    flag_label.config(text=flag_count)

def end_game():
    """disable and unbind all squares and reveal all mines"""

    for row in board:
            for c in row:
                c.config(state=DISABLED)
                c.unbind('<Button-3>')
                if c.value == -1 and not c.flagged:
                    
                    c.img = Image.open("img/bomb.png")
                    c.img.thumbnail((29,29))
                    c.img = ImageTk.PhotoImage(c.img)

                    c.config(relief=RIDGE, width=0, image=c.img)

                elif c.value != -1 and c.flagged:
                    
                    c.img = Image.open("img/no-bomb.png")
                    c.img.thumbnail((29,29))
                    c.img = ImageTk.PhotoImage(c.img)

                    c.config(relief=RIDGE, width=0, image=c.img)

smiley.config(command=restart)

create(width=2, font=('San Serif', 16, 'bold'), borderwidth=3)

root.mainloop()
















