
def drawCircle(canvas, x, y, r, fill=None):
    if fill == None: canvas.create_oval(x-r, y-r, x+r, y+r)
    else: canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline=fill)

def distance(x0, y0, x1, y1):
    return ((x0-x1)**2 + (y0-y1)**2)**0.5

def map(value, lo, hi, newLo, newHi):
    oldRange = hi - lo
    newRange = newHi - newLo
    scaleFactor = (value - lo)/oldRange
    return (newLo + scaleFactor * newRange)

class Button(object):
    def __init__(self, name, function, x, y, w, h):
        self.name = name
        self.function = function
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def inBounds(self, event):
        if (self.x <= event.x <= self.x + self.w) and (self.y <= event.y <= self.y + self.h):
            self.function()

    def inBounds2(self, event):
        return (self.x <= event.x <= self.x + self.w) and (self.y <= event.y <= self.y + self.h)

    def draw(self, canvas,  fill='light cyan', outline='sky blue'):
        canvas.create_rectangle(self.x, self.y, self.x + self.w, self.y + self.h, fill=fill, outline=outline)
        canvas.create_text(self.x + self.w/2, self.y + self.h/2, text=self.name, fill='RoyalBlue4')

class Slider(object):
    def __init__(self, name, min, max, x, y, w, h):
        self.name = name
        self.max = max
        self.min = min
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.value = (min + max)/2
        self.sliderPos = self.x + self.w/2

    def updateSlider(self, value):
        self.sliderPos = map(value, self.min, self.max, self.x, self.x + self.w)

    def updateValue(self, sliderPos):
        self.value = map(sliderPos, self.x, self.x + self.w, self.min, self.max)

    def inBounds(self, event):
        if distance(self.sliderPos, self.y + self.h/2, event.x, event.y) <= 10:
            if self.x <= event.x <= self.x + self.w:
                self.sliderPos = event.x
                self.value = map(event.x, self.x, self.x + self.w, self.min, self.max)

    def draw(self, canvas):
        canvas.create_text(self.x - 10, self.y + self.h/2, text=self.name, anchor='e')
        canvas.create_rectangle(self.x, self.y, self.x + self.w, self.y + self.h, fill='light cyan', outline='sky blue')
        drawCircle(canvas, self.sliderPos, self.y + self.h/2, 5, 'sky blue')
        #canvas.create_text(self.sliderPos, self.y + 4*self.h, text=str(round(self.value)))