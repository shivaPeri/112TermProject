
### svg fucntion
# https://pypi.org/project/svg.path/
from svg.path import *

# Somewhat followed this tutorial https://www.youtube.com/watch?v=bbY13xi0yhM 

## https://stackoverflow.com/questions/15857818/python-svg-parser
from xml.dom import minidom

# svgPath is the string of the svg file
# n is the number of segments in between points
def svgToPath(n, svgPath, scale):
    path = parse_path(svgPath)
    #points = [(p.real * scale, p.imag * scale) for p in (path.point(i/n) for i in range(0, n+1))]
    points = [ path.point(i/n) for i in range(0, n+1)]
    return points

def svgToPath2(n, svgPath, scale):
    path = parse_path(svgPath)
    points = [(p.real * scale, p.imag * scale) for p in (path.point(i/n) for i in range(0, n+1))]
    return points

# modified from https://stackoverflow.com/questions/15857818/python-svg-parser
def getSvgPath(filePath):
    doc = minidom.parse(filePath)  # parseString also exists
    path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
    doc.unlink()
    #print(path_strings)
    return path_strings

def drawSVG(canvas, path, fill='gray80'):
    for i in range(len(path)-1):
        prev = path[i]
        cur = path[i+1]
        canvas.create_line(prev[0] + xOffset, prev[1] + yOffset, cur[0] + xOffset, cur[1]+ yOffset, fill=fill) 




