#!/usr/bin/env python3
"""Front-panel input prototype. Python 3, standard-library Tkinter only."""
# Controls:
# Keyboard buttons 1-4: Soft buttons SW1 to SW4
# Buttons 5,6 or <> or ,. or left-right cursor keys: SW5 and SW6
# Up/down cursor keys, or mouse scroll wheel (if hovering over the encoder): ROTARY ENCODER
# Space or Enter, or clicking the encoder knob: SW7 (encoder push switch)

import math
import tkinter as tk
from tkinter import font as tkfont

W, H = 1080, 410
PANEL = '#17191d'
EDGE = '#343941'
BUTTON = '#363b43'
BUTTON_HOVER = '#484f59'
BUTTON_DOWN = '#688aa9'
TEXT = '#d9e0e7'
MUTED = '#99a5b0'

class Panel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Front Panel — Input Prototype')
        self.geometry('1100x480')
        self.minsize(720, 350)
        self.configure(bg='#101215')
        self.canvas = tk.Canvas(self, bg='#101215', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', lambda e: self.draw())
        self.canvas.bind('<Motion>', self.motion)
        self.canvas.bind('<ButtonPress-1>', self.mouse_down)
        self.canvas.bind('<ButtonRelease-1>', self.mouse_up)
        self.canvas.bind('<MouseWheel>', self.wheel)
        self.canvas.bind('<Button-4>', lambda e: self.wheel_linux(e, 1))
        self.canvas.bind('<Button-5>', lambda e: self.wheel_linux(e, -1))
        self.bind_all('<KeyPress>', self.key_down)
        self.bind_all('<KeyRelease>', self.key_up)
        self.pressed = set()
        self.key_held = {}
        self.hover = None
        self.mouse_button = None
        self.encoder_angle = 0
        self.encoder_count = 0
        self.last_event = 'Ready — press a key or click a button'
        self.event_number = 0
        self.draw()

    def scale_info(self):
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        s = min(cw / W, ch / H)
        return s, (cw - W*s)/2, (ch - H*s)/2

    def logical(self, x, y):
        s, ox, oy = self.scale_info()
        return (x-ox)/s, (y-oy)/s

    def rect(self, x1,y1,x2,y2, **kw):
        s,ox,oy = self.scale_info()
        return self.canvas.create_rectangle(ox+x1*s,oy+y1*s,ox+x2*s,oy+y2*s,**kw)

    def oval(self, x1,y1,x2,y2, **kw):
        s,ox,oy = self.scale_info()
        return self.canvas.create_oval(ox+x1*s,oy+y1*s,ox+x2*s,oy+y2*s,**kw)

    def line(self, coords, **kw):
        s,ox,oy = self.scale_info()
        xy=[]
        for i, val in enumerate(coords):
            xy.append((ox if i%2==0 else oy) + val*s)
        return self.canvas.create_line(*xy,**kw)

    def text(self,x,y,txt,size=14,color=TEXT,weight='normal',**kw):
        s,ox,oy = self.scale_info()
        return self.canvas.create_text(ox+x*s,oy+y*s,text=txt,
            font=('DejaVu Sans',max(7,round(size*s)),weight),fill=color,**kw)

    def controls(self):
        # Display area, four soft-buttons, encoder and two auxiliary buttons.
        regions={}
        for i in range(4):
            x=111+i*154
            regions[f'SW{i+1}']=('circle',x+39,307,31)
        regions['SW5']=('circle',824,307,31)
        regions['SW6']=('circle',941,307,31)
        regions['ENCODER']=('circle',880,149,67)
        return regions

    def hit(self,x,y):
        for name,(shape,cx,cy,r) in self.controls().items():
            if (x-cx)**2+(y-cy)**2 <= r*r:
                return name
        return None

    def draw(self):
        c=self.canvas
        c.delete('all')
        s,ox,oy=self.scale_info()
        self.rect(2,2,W-2,370,fill=PANEL,outline='#525861',width=max(1,2*s))
        self.rect(91,49,735,251,fill='#0c0f13',outline='#49535d',width=max(1,5*s))
        self.rect(99,57,727,243,fill='#080b0f',outline='#1c2933',width=max(1,2*s))
        self.text(413,150,'DISPLAY',size=18,color='#35414d',weight='bold')
        self.text(413,178,'TFT graphics will be added later',size=11,color='#34404a')
        self.text(880,56,'ENCODER',size=12,color=MUTED,weight='bold')
        for name,(shape,x,y,r) in self.controls().items():
            if name=='ENCODER':
                self.oval(x-r-5,y-r-5,x+r+5,y+r+5,fill='#0b0d10',outline='#4b535c',width=max(1,3*s))
                self.oval(x-r,y-r,x+r,y+r,fill=(BUTTON_DOWN if 'SW7' in self.pressed else ('#596d7f' if self.hover==name else '#343941')),outline='#69727c',width=max(1,2*s))
                self.oval(x-r+12,y-r+12,x+r-12,y+r-12,fill=('#425b70' if 'SW7' in self.pressed else '#292e35'),outline=('#c4dff3' if 'SW7' in self.pressed else '#555d66'),width=max(1,s))
                angle=math.radians(self.encoder_angle-90)
                self.line([x+math.cos(angle)*36,y+math.sin(angle)*36,
                           x+math.cos(angle)*52,y+math.sin(angle)*52],fill='#b2d6ef',width=max(2,5*s),capstyle='round')
            else:
                down=name in self.pressed
                fill=BUTTON_DOWN if down else (BUTTON_HOVER if self.hover==name else BUTTON)
                self.oval(x-r-3,y-r-3,x+r+3,y+r+3,fill='#0a0d11',outline='#20272f',width=max(1,2*s))
                self.oval(x-r,y-r,x+r,y+r,fill=fill,outline=('#c4dff3' if down else '#727a84'),width=max(1,2*s))
                if down:
                    self.oval(x-r+6,y-r+6,x+r-6,y+r-6,outline='#a7d1ef',width=max(1,s))
                self.text(x,y+51,name,size=12,color=('#d3ebff' if down else MUTED),weight='bold')
        self.text(880,244,'SWENC' if 'SW7' in self.pressed else 'PUSH: SWENC',size=11,color=('#d3ebff' if 'SW7' in self.pressed else MUTED),weight='bold')
        #  self.text(413,280,'SOFT BUTTONS',size=11,color='#7d8994')
        #  self.text(883,366,'SW5 / SW6',size=11,color='#7d8994')
        self.rect(2,379,W-2,408,fill='#252a31',outline='#3a424b')
        self.text(16,393,self.last_event,size=12,color='#cbe4f6',anchor='w')
        self.text(W-16,393,f'Encoder: {self.encoder_count:+d} detents',size=12,color='#a9b7c4',anchor='e')

    def report(self, message):
        self.event_number += 1
        self.last_event = f'#{self.event_number}   {message}'
        self.draw()

    def press(self,name):
        if name and name != 'ENCODER' and name not in self.pressed:
            self.pressed.add(name)
            self.report(f'{name} PRESSED')

    def release(self,name):
        if name in self.pressed:
            self.pressed.remove(name)
            self.report(f'{name} RELEASED')

    def rotate(self, direction, count=1):
        direction=1 if direction>0 else -1
        count=max(1,int(count))
        self.encoder_count += direction*count
        self.encoder_angle=(self.encoder_angle+direction*18*count)%360
        self.report(f'ENCODER {"CLOCKWISE" if direction>0 else "ANTICLOCKWISE"}  ({count} detent{"s" if count!=1 else ""})')

    def motion(self,event):
        new=self.hit(*self.logical(event.x,event.y))
        if new != self.hover:
            self.hover=new
            self.draw()

    def mouse_down(self,event):
        name=self.hit(*self.logical(event.x,event.y))
        self.mouse_button=name
        if name=='ENCODER':
            self.press('SW7')
        else:
            self.press(name)

    def mouse_up(self,event):
        if self.mouse_button:
            action = 'SW7' if self.mouse_button=='ENCODER' else self.mouse_button
            if action not in self.key_held.values():
                self.release(action)
        self.mouse_button=None

    def wheel(self,event):
        if self.hit(*self.logical(event.x,event.y))!='ENCODER':
            return
        if event.delta:
            # Windows usually reports 120 units per notch; macOS can report smaller values.
            count=max(1,round(abs(event.delta)/120))
            self.rotate(1 if event.delta>0 else -1,count)

    def wheel_linux(self,event,direction):
        if self.hit(*self.logical(event.x,event.y))=='ENCODER':
            self.rotate(direction)

    @staticmethod
    def key_action(event):
        key=event.keysym.lower()
        if key in ('1','2','3','4','5','6','7'):
            return 'SW'+key
        if key in ('comma','less','left'):
            return 'SW5'
        if key in ('period','greater','right'):
            return 'SW6'
        if key in ('space','return','kp_enter'): return 'SW7'
        if key=='up': return 'CW'
        if key=='down': return 'CCW'
        return None

    def key_down(self,event):
        key=event.keycode
        action=self.key_action(event)
        if not action or key in self.key_held:
            return
        self.key_held[key]=action
        if action=='CW': self.rotate(1)
        elif action=='CCW': self.rotate(-1)
        else: self.press(action)

    def key_up(self,event):
        action=self.key_held.pop(event.keycode,None)
        if action and action.startswith('SW'):
            # If multiple keys map to one button, keep it pressed until both are released.
            mouse_action = 'SW7' if self.mouse_button=='ENCODER' else self.mouse_button
            if action not in self.key_held.values() and mouse_action!=action:
                self.release(action)

if __name__=='__main__':
    app=Panel()
    app.mainloop()
