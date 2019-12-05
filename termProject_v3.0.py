
######## 15-112 Term Project
######## Shiva Peri

import math, random, string, copy, os, json, numpy

# from http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html 
# modified saveSnapshot()
from cmu_112_graphics import *

from tkinter import *
from PIL import Image
from buttonsAndSliders import *
from svgFunctions import *

def drawCircle(canvas, x, y, r, outline='gray80', fill=None):
    if fill == None: canvas.create_oval(x-r, y-r, x+r, y+r, outline=outline)
    else: canvas.create_oval(x-r, y-r, x+r, y+r, outline=outline, fill=fill)

def distance(x0,y0,x1,y1):
    return ((x0-x1)**2 + (y0-y1)**2)**0.5

def map(value, lo, hi, newLo, newHi):
    oldRange = hi - lo
    newRange = newHi - newLo
    scaleFactor = (value - lo)/oldRange
    return (newLo + scaleFactor * newRange)

# wheel object beahves like a rotating vector
# the main attributes which are modifed are radius and dtheta
class Wheel(object):
    def __init__(self, x, y, r, speed):
        self.cx = x
        self.cy = y
        self.r = r
        self.rx = x + self.r * math.cos(0)
        self.ry = y + self.r * math.sin(0)
        self.speedConstant = speed
        
    def __repr__(self):
        return str(self.__dict__)

    def updateRotation(self, theta):
        self.rx = self.cx + self.r * math.cos(theta)
        self.ry = self.cy + self.r * math.sin(theta)
    

    def draw(self, canvas):
        drawCircle(canvas, self.cx, self.cy, 1, 'gray80')
        drawCircle(canvas, self.cx, self.cy, self.r)
        canvas.create_line(self.cx, self.cy, self.rx, self.ry, fill='gray50')

# an assembly object has a list of wheels and connects each wheel 'vector' tip-to-tail
# each of the wheel's rotations are updated independently
# each wheel's position is updated based on the previous wheel's 'vector'
class Assembly(object):
    def __init__(self, x, y):
        self.cx, self.cy = x, y
        self.main = Wheel(x, y, 100, 0.05)
        self.wheels = [self.main]
        self.theta = 0
        self.dtheta = 0.05

    def addWheel(self, r):
        prev = self.wheels[-1]
        newX, newY = prev.rx, prev.ry
        newSpeed = (random.randint(-10, 10))
        newWheel = Wheel(newX, newY, r, newSpeed)
        self.wheels.append(newWheel)

    def rotate(self):
        self.theta += self.dtheta
        self.wheels[0].updateRotation(self.wheels[0].speedConstant * self.theta)
            
        for i in range(len(self.wheels)-1):
            prev = self.wheels[i]
            cur = self.wheels[i+1]
            prev.updateRotation(prev.speedConstant * self.theta)
            cur.cx, cur.cy = prev.rx, prev.ry
            cur.updateRotation(cur.speedConstant * self.theta)

    def update(self):
        for i in range(1,len(self.wheels)):
            prev = self.wheels[i-1]
            cur = self.wheels[i]
            cur.cx, cur.cy = prev.rx, prev.ry
            cur.updateRotation(cur.speedConstant * self.theta)

    def draw(self, canvas):
        for wheel in self.wheels:
            wheel.draw(canvas)

# Pen object stores color and weight of the drawPath
# One pen object is created in Modal App and referenced in drawMode, viewMode, settingsMode
class Pen(object):
    def __init__(self, shape, size, r, g, b):
        self.color = _from_rgb((r,g,b))
        self.shape = shape
        self.size = size

    def changeColor(self, r, g, b):
        self.color = _from_rgb((r,g,b))

    def drawPoint(self, canvas, x, y):
        canvas.create_oval(x-self.size, y-self.size, x+self.size, y+self.size, fill= self.color, width=0)

# from https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinterv 
def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code"""
    return "#%02x%02x%02x" % rgb  

# Program's main feature. Allows user to customize drawing machine and save files
class DrawMode(Mode):
    def appStarted(mode):
        mode.assembly = Assembly(mode.width/2, mode.height/2)

        bWidth, bHeight = 110, 25
        buttonX, buttonY = 20, mode.height-270
        spacer = 1.5*bHeight

        addButton = Button('Create Wheel', mode.addWheel, buttonX, buttonY, bWidth, bHeight)
        removeButton = Button('Remove Wheel', mode.removeWheel, buttonX, buttonY + spacer, bWidth, bHeight)
        drawButton = Button('Draw / Pause', mode.togglePause, buttonX, buttonY + 2*spacer, bWidth, bHeight)
        waveButton = Button('Wave', mode.toggleWave, buttonX, buttonY + 3*spacer, bWidth, bHeight)
        saveButton = Button('Save', mode.save, buttonX, buttonY + 4*spacer, bWidth, bHeight)
        homeButton = Button('Home', mode.goHome, buttonX, buttonY + 5*spacer, bWidth, bHeight)

        mode.buttons = [addButton, removeButton, drawButton, waveButton, saveButton, homeButton]

        mode.showWave = False
        mode.waveSpeed = 2
        mode.drawSpeed = 1

        mode.path = []
        
        mode.wheelIndex = 0

        mode.timerDelay = 10
        mode.isPaused = True
        mode.hideMachine = False

    def addWheel(mode):
        r = random.randint(1, 100)
        mode.assembly.addWheel(r)
        mode.wheelIndex = -1

    def removeWheel(mode):
        if len(mode.assembly.wheels) > 1:
            if mode.wheelIndex == len(mode.assembly.wheels)-1:
                mode.wheelIndex -= 1
            mode.assembly.wheels.pop()

    def togglePause(mode):
        mode.isPaused = not mode.isPaused
        
    def toggleWave(mode):
        mode.showWave = not mode.showWave

    def save(mode):
        count = len(os.listdir(mode.app.filesPath))
        newFolderPath = mode.app.filesPath + os.sep + 'file_' + str(count)
        os.makedirs(newFolderPath)

        newImagePath = newFolderPath + os.sep + 'img.png'
        image = mode.app.saveSnapshot(newImagePath)

        d = {'color': mode.app.pen.color, 'size': mode.app.pen.size, 'drawPath': mode.path}
        #drawPathString = str([mode.app.pen.color] + [mode.app.pen.size] + mode.path)
        #newFilePath = newFolderPath + '/drawPath.txt'
        newFilePath = newFolderPath + os.sep + 'drawPath.json'
        writeJSONFile(newFilePath, d)

    def goHome(mode):
        mode.app.setActiveMode(mode.app.splashScreenMode)

    def timerFired(mode):
        if not mode.isPaused:
            for i in range(mode.drawSpeed):
                mode.assembly.rotate()
                wheel = mode.assembly.wheels[-1]
                mode.path.append((wheel.rx, wheel.ry, mode.app.pen.color, mode.app.pen.size))    
        else:
            mode.assembly.update()
        
    def keyPressed(mode, event):
        keys = ['Left', 'Right', 'Up', 'Down']
        #dirs = [(-1,0), (1,0), (0,0.01), (0,-0.01)]
        dirs = [(-1,0), (1,0), (0,0.1), (0,-0.1)]

        if event.key in keys:
            newR, newDTheta = dirs[keys.index(event.key)]
            newR, newSpeed = dirs[keys.index(event.key)]
            temp = mode.assembly.wheels[mode.wheelIndex]
            temp.r += newR
            temp.updateRotation(temp.speedConstant * mode.assembly.theta)
            temp.speedConstant += newSpeed

        elif event.key == 'c' or event.key == 'C':
            mode.path = []
        elif event.key == 'r' or event.key == 'R':
            mode.assembly = Assembly(mode.width/2, mode.height/2)
            mode.appStarted()
        elif event.key == 'q' or event.key == 'Q':
            mode.app.setActiveMode(mode.app.splashScreenMode)
        elif event.key == 'h' or event.key == 'H':
            mode.hideMachine = not mode.hideMachine

        elif event.key == 'Space':
            mode.wheelIndex += 1
            mode.wheelIndex %= len(mode.assembly.wheels)

        elif event.key == '-' or event.key == '_':
            if mode.waveSpeed > 0.1:
                mode.waveSpeed -= 0.1
        elif event.key == '+' or event.key == '=':
            mode.waveSpeed += 0.1

        elif event.key == '<' or event.key == ',':
            if mode.drawSpeed > 1:
                mode.drawSpeed -= 1
        elif event.key == '>' or event.key == '.':
            mode.drawSpeed += 1

    def mousePressed(mode, event):
        for button in mode.buttons:    
            button.inBounds(event)

    def drawSelectedWheelInfo(mode, canvas):
        wheel = mode.assembly.wheels[mode.wheelIndex]
        textX, textY = 20, 20
        spacer = 30
        s1 = 'Radius: ' + str(wheel.r)
        s2 = 'Speed: ' + str(round(wheel.speedConstant, 1))
        helpText = 'Use Left/Right keys to change radius \nUse Up/Down keys to change speed \nUse Space to change editing wheel'

        canvas.create_text(textX, textY, text= s1, font='Arial 25', anchor = 'nw')
        canvas.create_text(textX, textY + spacer, text= s2, font='Arial 25', anchor = 'nw')
        canvas.create_text(textX, textY + 2.5 * spacer, text= helpText, anchor = 'nw')

        wheelX, wheelY = 125, 275
        drawCircle(canvas, wheelX, wheelY, wheel.r, 'gray80')
        newX = wheelX + wheel.r * math.cos(wheel.speedConstant * mode.assembly.theta)
        newY = wheelY + wheel.r * math.sin(wheel.speedConstant * mode.assembly.theta)
        canvas.create_line(wheelX, wheelY, newX, newY, fill='gray50')

    def drawWave(mode, canvas):
        wave = []
        i = 0
        for point in mode.path:
            y = point[1]
            wave.append((i, y))
            i += mode.waveSpeed

        xOffset = mode.width - 300
        for i in range(len(wave)):
            (x, y) = wave[i]
            newX = xOffset + (len(wave)* mode.waveSpeed - x)
            wave[i] = (newX, y)

        if len(wave) > 0:
            for i in range(1, len(wave)):
                prev = wave[i-1]
                cur = wave[i]
                if not (0 <= cur[0] <= mode.width) and not (0 <= cur[1] <= mode.height): break
                canvas.create_line(prev[0], prev[1], cur[0], cur[1], fill='red', width=1)
                
            canvas.create_line(wave[-1][0], wave[-1][1], mode.path[-1][0], mode.path[-1][1], fill='gray90')

    def drawPath(mode, canvas):
        if len(mode.path) > 1:
            for i in range(1, len(mode.path)):
                prev = mode.path[i-1]
                cur = mode.path[i]
                canvas.create_line(prev[0], prev[1], cur[0], cur[1], fill= cur[2], width= cur[3])
                #drawCircle(canvas, prev[0], prev[1], mode.app.pen.size/2, mode.app.pen.color)

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0,0,mode.width, mode.height, fill= 'light cyan')
        if not mode.hideMachine:
            mode.assembly.draw(canvas)
            tempWheel = mode.assembly.wheels[mode.wheelIndex]
            drawCircle(canvas, tempWheel.cx, tempWheel.cy, tempWheel.r, outline='gray50')

        for button in mode.buttons:
            button.draw(canvas)

        corner = 20
        s = 'Key Shortcuts: c - Clear, r - Reset, h - Hide'
        canvas.create_text(corner, mode.height - corner, text=s, anchor='sw')

        if mode.showWave:
            s = 'Use +/- to alter wave speed'
            canvas.create_text(mode.width - corner, mode.height - corner, text=s, anchor='se')
        else: 
            s = 'Use </> to alter drawing speed'
            canvas.create_text(mode.width - corner, mode.height - corner, text=s, anchor='se')
        
        mode.drawSelectedWheelInfo(canvas)
        if mode.showWave:
            mode.drawWave(canvas)
        else:
            mode.drawPath(canvas)
        
# Allows users to open and view files
class GalleryMode(Mode):
    def appStarted(mode):
        homeButton = Button('Home', mode.goHome, 20, 20, 80, 20)
        prevButton = Button('Previous', mode.previousPage, mode.width/2 - 50, mode.height - 40, 80, 20)
        nextButton = Button('Next', mode.nextPage, mode.width/2 + 50, mode.height - 40, 80, 20)
        mode.buttons = [homeButton, prevButton, nextButton]

        mode.currentPage = 0
        mode.pages = []

        xOffset, yOffset = 100, 150
        row, col = 0, 0
        rowScale, colScale = 300, 200
        newPage = []
        fileCount = 0
        for filename in os.listdir(mode.app.filesPath):
            if fileCount % 12 == 0 and fileCount != 0:
                row, col = 0, 0
                mode.pages.append(newPage)
                newPage = []

            if not filename.endswith('.DS_Store'):
                imagePath = (mode.app.filesPath + os.sep + filename + os.sep + 'img.png')
                image = Image.open(imagePath)
                scaledImage = mode.app.scaleImage(image, 0.1)
                bWidth, bHeight = scaledImage.size

                filePath = mode.app.filesPath + os.sep + filename

                buttonX, buttonY = col * rowScale, row * colScale
                button = Button(filePath, mode.uselessFunction, xOffset + buttonX, yOffset + buttonY, bWidth, bHeight)

                newPage.append((button, scaledImage))

                col += 1
                if col % 4 == 0:
                    col = 0
                    row += 1

                fileCount += 1

        mode.pages.append(newPage)
        #(len(mode.pages))

    def goHome(mode):
        mode.app.setActiveMode(mode.app.splashScreenMode)

    def previousPage(mode):
        if mode.currentPage > 0:
            mode.currentPage -= 1

    def nextPage(mode):
        if mode.currentPage < len(mode.pages)-1:
            mode.currentPage += 1

    # this is a useless function to fill the Button arguments
    def uselessFunction(mode):
        pass

    def mousePressed(mode, event):
        for button in mode.buttons:
            button.inBounds(event)

        for button in mode.pages[mode.currentPage]:
            if button[0].inBounds2(event):
                mode.app.currentFile = button[0].name
                mode.app.viewMode = ViewMode()
                mode.app.setActiveMode(mode.app.viewMode)

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill= 'light cyan')
        font1 = 'Arial 26 bold'
        font2 = 'Arial 12 bold'
        fill = 'RoyalBlue4'
        canvas.create_text(mode.width/2, 100, text='Gallery', font=font1, fill=fill)
        
        for button in mode.buttons:
            button.draw(canvas)

        i = 0
        for button, thumbnail in mode.pages[mode.currentPage]:
            button.draw(canvas)
            x = button.x + button.w/2
            y = button.y + button.h/2
            canvas.create_image(x, y, image=ImageTk.PhotoImage(thumbnail))


# Pen Editor
# the sliders here are just for aesthetic. They are controlled by keys
class SettingsMode(Mode):
    def appStarted(mode):
        bWidth, bHeight = 100, 25
        buttonX, buttonY = 20, mode.height - 50
        
        homeButton = Button('Home', mode.goHome, buttonX, buttonY, bWidth, bHeight)
        mode.buttons = [homeButton]

        sWidth, sHeight = 200, 5
        sliderX, sliderY = mode.width/2 - 100, mode.height/2 + 100
        spacer = 30

        mode.redSlider = Slider('Red:', 0, 255, sliderX, sliderY, sWidth, sHeight)
        mode.redSlider.value = 255

        mode.greenSlider = Slider('Green:', 0, 255, sliderX, sliderY + spacer, sWidth, sHeight)
        mode.greenSlider.value = 0

        mode.blueSlider = Slider('Blue:', 0, 255, sliderX, sliderY + 2*spacer, sWidth, sHeight)
        mode.blueSlider.value = 0

        mode.sizeSlider = Slider('Size:', 0, 5, sliderX, sliderY + 3*spacer, sWidth, sHeight)
        mode.sizeSlider.value = 1
        mode.sliders = [mode.redSlider, mode.greenSlider, mode.blueSlider, mode.sizeSlider]

        for slider in mode.sliders:
            slider.updateSlider(slider.value)

        mode.selectedSliderIndex = 0

    def goHome(mode):
        mode.app.setActiveMode(mode.app.splashScreenMode)

    def timerFired(mode):
        r = int(mode.redSlider.value)
        g = int(mode.greenSlider.value)
        b = int(mode.blueSlider.value)
        
        mode.app.pen.changeColor(r,g,b)
        mode.app.pen.size = int(mode.sizeSlider.value)

    def mousePressed(mode, event):
        for button in mode.buttons:
            button.inBounds(event)

    def keyPressed(mode, event):
        if event.key == 'Up':
            mode.selectedSliderIndex -= 1
            mode.selectedSliderIndex %= 4
        elif event.key == 'Down':
            mode.selectedSliderIndex += 1
            mode.selectedSliderIndex %= 4
        
        temp = mode.sliders[mode.selectedSliderIndex]
        if event.key == 'Right':
            if temp.value < temp.max:
                temp.sliderPos += 5
                if temp.sliderPos > temp.x + temp.w:
                    temp.sliderPos = temp.x + temp.w
                temp.updateValue(temp.sliderPos)
        elif event.key == 'Left':
            if temp.value > temp.min:
                temp.sliderPos -= 5
                if temp.sliderPos < temp.x:
                    temp.sliderPos = temp.x
                temp.updateValue(temp.sliderPos)

        mode.sliders[mode.selectedSliderIndex] = temp
        
    def drawColorPreview(mode, canvas, x, y, w, h):
        canvas.create_oval(x, y, x+w, y+h, fill=mode.app.pen.color, width=0)

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill= 'light cyan')
        font1 = 'Arial 26 bold'
        font2 = 'Arial 18 bold'
        fill = 'RoyalBlue4'
        canvas.create_text(mode.width/2, 150, text='Pen Settings', font=font1, fill=fill)
        canvas.create_text(mode.width/2, 250, text='edit pen type here', font=font2, fill=fill)

        mode.app.pen.drawPoint(canvas, mode.width/2, mode.height/2)

        for button in mode.buttons:
            button.draw(canvas)
        
        textX, textY = 20, 20
        helpText = 'Use Left/Right keys to edit slider \nUse Up/Down keys to change current slider'
        canvas.create_text(textX, textY, text=helpText, anchor='nw')

        temp = mode.sliders[mode.selectedSliderIndex]
        border = 5
        canvas.create_rectangle(temp.x - border, temp.y - border, temp.x + temp.w + border, temp.y + temp.h + border)

        x = mode.redSlider.x + mode.redSlider.w + 20
        y = mode.redSlider.y
        mode.drawColorPreview(canvas, x, y, 100, 100)

        for slider in mode.sliders:
            slider.draw(canvas)

# File viewer
class ViewMode(Mode):
    def appStarted(mode):
        path = mode.app.currentFile
        #print(path + os.sep + 'drawPath.json')
        d = readJSONFile(path + os.sep + 'drawPath.json')
        mode.penColor = d['color']
        mode.penSize = d['size']
        mode.drawPath = d['drawPath']

        mode.drawnPath = []

        bWidth, bHeight = 80, 25
        buttonX, buttonY = 20, mode.height - 130
        spacer = 40

        viewButton = Button('View', mode.view, buttonX, buttonY, bWidth, bHeight)
        resetButton = Button('Reset', mode.reset, buttonX, buttonY + spacer, bWidth, bHeight)
        homeButton = Button('Home', mode.goHome, buttonX, buttonY + 2*spacer, bWidth, bHeight)

        mode.buttons = [viewButton, resetButton, homeButton]

        mode.drawSpeed = 1
        
    def view(mode):
        mode.drawnPath = mode.drawPath

    def reset(mode):
        mode.drawnPath = []
        mode.drawSpeed = 1

    def goHome(mode):
        mode.app.filesPath = 'SpirographFiles'
        mode.app.setActiveMode(mode.app.galleryMode)

    def timerFired(mode):
        for i in range(mode.drawSpeed):
            if len(mode.drawnPath) < len(mode.drawPath):
                mode.drawnPath.append(mode.drawPath[len(mode.drawnPath)])
        
    def drawCurrentPath(mode, canvas):
        if len(mode.drawPath) > 1:
            for i in range(1, len(mode.drawnPath)):
                prev = mode.drawnPath[i-1]
                cur = mode.drawnPath[i]
                canvas.create_line(prev[0], prev[1], cur[0], cur[1], fill= cur[2], width= cur[3])
                
    def mousePressed(mode, event):
        for button in mode.buttons:
            button.inBounds(event)

    def keyPressed(mode, event):
        if event.key == '<' or event.key == ',':
            if mode.drawSpeed > 1:
                mode.drawSpeed -= 1
        elif event.key == '>' or event.key == '.':
            mode.drawSpeed += 1

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill= 'light cyan')
        font1 = 'Arial 26 bold'
        fill = 'RoyalBlue4'
        canvas.create_text(mode.width/2, 50, text='Viewer', font=font1, fill=fill)

        corner = 20
        s2 = 'Use </> to alter drawing speed'
        canvas.create_text(mode.width - corner, mode.height - corner, text=s2, anchor='se')

        mode.drawCurrentPath(canvas)

        for button in mode.buttons:
            button.draw(canvas)


# Referenced the following
# https://www.youtube.com/watch?v=MY4luNgGfms
# https://www.youtube.com/watch?v=r6sGWTCMz2k
# https://mathematica.stackexchange.com/questions/171755/how-can-i-draw-a-homer-with-epicycloids
# https://www.youtube.com/watch?v=ds0cmAV-Yek
# https://docs.scipy.org/doc/numpy/reference/generated/numpy.fft.fft.html#numpy.fft.fft
# http://www.jezzamon.com/fourier/index.html
class Fourier(object):
    def __init__(self, path, x, y):
        self.path = numpy.fft.fft(path)
        self.wheels = []
        self.numWheels = len(self.path)
        temp = [( c.real**2 + c.imag**2)**0.5 for c in self.path]
        self.largestVectorIndex = temp.index(max(temp[1:]))
        self.dtheta = math.pi * 2 / len(self.path)

        self.offsets = []
        self.assembly = self.getAssemblyObject(x, y)

    def getAssemblyObject(self, x, y):
        newAssembly = Assembly(x, y)
        for i in range(1, len(self.path)):
            newAssembly.addWheel(1)

        temp = self.path[self.largestVectorIndex]    
        largestR = (temp.real**2 + temp.imag**2)**0.5
        scale = largestR / 100 

        for i in range(len(self.path)):
            complexNum = self.path[i]
            a, bi = complexNum.real, complexNum.imag
            r = ((a**2 + bi**2) ** 0.5) / scale
            speed = i
            offset = math.atan2(bi, a) 
            #offset = math.atan2(bi, a) + self.rotation
            self.offsets.append(offset)

            newAssembly.wheels[i].r = r
            newAssembly.wheels[i].speedConstant = speed

        newAssembly.wheels[0].r = 0
        self.wheels = copy.deepcopy(newAssembly.wheels)
        return newAssembly

    def addWheel(self):
        if self.numWheels < len(self.wheels):
            self.numWheels += 1
            self.assembly.wheels = self.wheels[:self.numWheels]

    def removeWheel(self):
        if self.numWheels > 1:
            self.numWheels -= 1
            self.assembly.wheels = self.wheels[:self.numWheels]

    def rotateByOffset(self, offset):
        for i in range(len(self.path)):
            self.offsets[i] += offset

    def fourierRotation(self):
        self.assembly.theta += self.dtheta

        for i in range(len(self.assembly.wheels) - 1):
            prev = self.assembly.wheels[i]
            cur = self.assembly.wheels[i+1]
            prev.updateRotation(prev.speedConstant * self.assembly.theta + self.offsets[i])
            cur.cx, cur.cy = prev.rx, prev.ry
            cur.updateRotation(cur.speedConstant * self.assembly.theta + self.offsets[i+1])

# Fast Fourier Transform -- Image input Mode
# pikachu svg from http://thecraftchop.com/entries/svg/pikachu
# mustache svg from http://www.webpop.com/blog/2013/08/16/support-for-svg
# these files are accessed in this file, they must be accessed when the program is running
class FourierMode(Mode):
    def appStarted(mode):  
        mode.drawPaths = []
        mode.file = mode.app.fourierFile
        mode.fourierObject = None

        if mode.file != None:
            svgPaths = getSvgPath(mode.file)
            for path in svgPaths:
                mode.drawPaths.append(svgToPath(200, path, 1/50))

            mode.fourierObject = Fourier(mode.drawPaths[0], mode.width/2, mode.height/2)

        bWidth, bHeight = 100, 25
        buttonX, buttonY = 20, mode.height - 150
        spacer = bHeight * 1.5

        drawButton = Button('Draw / Pause', mode.togglePause, buttonX, buttonY, bWidth, bHeight)
        importButton = Button('Import File', mode.importFile, buttonX, buttonY + spacer, bWidth, bHeight)
        homeButton = Button('Home', mode.goHome, buttonX, buttonY + 2*spacer, bWidth, bHeight)

        mode.buttons = [drawButton, importButton, homeButton]

        mode.drawSpeed = 1
        mode.isPaused = False
        mode.hideMachine = False
        mode.path = []
        mode.timerDelay = 1

    # modified from https://pythonspot.com/tk-file-dialogs/
    def importFile(mode):
        mode.app.fourierFile = filedialog.askopenfilename(initialdir = os.sep,title = "Select file",filetypes = (("svg files","*.svg"),))
        if mode.app.fourierFile == '':
            mode.app.fourierFile = mode.file
        else:
            mode.app.fourierMode = FourierMode()
            mode.app.setActiveMode(mode.app.fourierMode)

    def togglePause(mode):
        mode.isPaused = not mode.isPaused

    def goHome(mode):
        mode.app.setActiveMode(mode.app.splashScreenMode)

    def timerFired(mode):
        if not mode.isPaused and mode.fourierObject != None:
            for i in range(mode.drawSpeed):
                mode.fourierObject.fourierRotation()
                wheel = mode.fourierObject.assembly.wheels[-1]
                mode.path.append((wheel.rx, wheel.ry))  

    def drawPath(mode, canvas):
        if len(mode.path) > 1:
            for i in range(1, len(mode.path)):
                prev = mode.path[i-1]
                cur = mode.path[i]
                canvas.create_line(prev[0], prev[1], cur[0], cur[1], fill= mode.app.pen.color, width= mode.app.pen.size)
                #drawCircle(canvas, prev[0], prev[1], mode.app.pen.size/2, mode.app.pen.color)  


    def keyPressed(mode, event):
        if event.key == 'Left' and mode.fourierObject != None:
            mode.fourierObject.removeWheel()
        elif event.key == 'Right' and mode.fourierObject != None:
            mode.fourierObject.addWheel()
        elif event.key == 'c' or event.key == 'C':
            mode.path = []
        elif event.key == 'h' or event.key == 'H':
            mode.hideMachine = not mode.hideMachine
        elif event.key == 'Space' and mode.fourierObject != None:
            mode.fourierObject.rotateByOffset(math.pi / 2)
            mode.path = []
        elif event.key == '<' or event.key == ',':
            if mode.drawSpeed > 1:
                mode.drawSpeed -= 1
        elif event.key == '>' or event.key == '.':
            mode.drawSpeed += 1


    def mousePressed(mode, event):
        for button in mode.buttons:
            button.inBounds(event)

    def drawWheelInfo(mode, canvas):
        textX, textY = 20, 20
        spacer = 30
        s1 = 'Number of Wheels: ' + str(mode.fourierObject.numWheels)
        helpText = 'Use Left/Right keys to change the number of wheels in the assembly'

        canvas.create_text(textX, textY, text= s1, font='Arial 25', anchor = 'nw')
        canvas.create_text(textX, textY + spacer, text= helpText, anchor = 'nw')

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill= 'light cyan')
        #drawSVG(canvas, mode.drawPaths[0])
        font1, font2 = 'Arial 26 bold', 'Arial 12'
        fill = 'RoyalBlue4'
        canvas.create_text(mode.width/2, 50, text='Fourier Mode', font=font1, fill=fill)
        canvas.create_text(mode.width/2, 75, text='Input a path image (.svg) and watch the generated machine', font=font2, fill=fill)

        corner = 20
        s1 = 'Key Shortcuts: c - Clear, h - Hide, Spacebar - Rotate Drawing'
        canvas.create_text(corner, mode.height - corner, text=s1, anchor='sw')

        s2 = 'Use </> to alter drawing speed'
        canvas.create_text(mode.width - corner, mode.height - corner, text=s2, anchor='se')

        for button in mode.buttons:
            button.draw(canvas)
            
        if not mode.hideMachine and mode.fourierObject != None:
            mode.fourierObject.assembly.draw(canvas)

        if mode.fourierObject != None:
            mode.drawWheelInfo(canvas)
        mode.drawPath(canvas)

class SplashScreenMode(Mode):
    def appStarted(mode):

        bWidth, bHeight = 70, 25
        buttonX, buttonY = mode.width/2, mode.height/5 * 3
        spacer = 1.5 * bWidth

        drawButton = Button('Draw', mode.draw, buttonX - 2*spacer, buttonY, bWidth, bHeight)
        galleryButton = Button('Gallery', mode.gallery, buttonX - spacer, buttonY, bWidth, bHeight)
        fourierButton = Button('Fourier', mode.fourier, buttonX, buttonY, bWidth, bHeight)
        settingsButton = Button('Settings', mode.settings, buttonX + spacer, buttonY, bWidth, bHeight)
        mode.buttons = [drawButton, galleryButton, fourierButton, settingsButton]

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill= 'light cyan')

        font1 = 'Arial 36 bold'
        fill = 'RoyalBlue4'
        canvas.create_text(mode.width/2, mode.height/2, text='FOURIER DRAWING MACHINE', font=font1, fill=fill)
        for button in mode.buttons:
            button.draw(canvas)

        drawCircle(canvas, mode.width/2, mode.height/2, mode.height/2.5, outline='RoyalBlue4')
        drawCircle(canvas, mode.width/2, mode.height/2, mode.height/2.4, outline='RoyalBlue4')

    def draw(mode):
        mode.app.setActiveMode(mode.app.drawMode)

    def gallery(mode):
        mode.app.galleryMode = GalleryMode()
        mode.app.setActiveMode(mode.app.galleryMode)

    def settings(mode):
        mode.app.setActiveMode(mode.app.settingsMode)

    def fourier(mode):
        mode.app.setActiveMode(mode.app.fourierMode)

    def mousePressed(mode, event):
        for button in mode.buttons:
            button.inBounds(event)

        
# modified from https://stackoverflow.com/questions/20199126/reading-json-from-a-file 
def readJSONFile(path):
    with open(path) as json_data:
        d = json.load(json_data)
        json_data.close()
        return d

# modified from https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file 
def writeJSONFile(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)

class MyModalApp(ModalApp):
    def appStarted(app):
        app.pen = Pen('oval', 1, 255, 0, 0)
        app.filesPath = 'SpirographFiles'
        app.currentFile = None
        app.fourierFile = None

        app.splashScreenMode = SplashScreenMode()
        app.drawMode = DrawMode()
        app.settingsMode = SettingsMode()
        app.galleryMode = GalleryMode()
        app.viewMode = ViewMode()
        app.fourierMode = FourierMode()
        app.setActiveMode(app.splashScreenMode)

app = MyModalApp(width=1400, height=800)
