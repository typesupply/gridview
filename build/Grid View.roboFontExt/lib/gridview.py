import math
import ezui
import merz
from mojo.UI import getDefault
from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber

# To Do:
# - menu item to turn it on/off
# - JIT load colors from defaults
# - use alphaColor function from guide tool
# - faster zoom?
# - text duplication?

identifierStub = "com.typesupply.GridView."

def alphaColor(color, alpha):
    r, g, b, a = color
    return (r, g, b, alpha)

backgroundColor = getDefault("glyphViewBackgroundColor")
gridColor = getDefault("glyphViewGridColor")
textColor = alphaColor(gridColor, 1)
grid1Color = alphaColor(gridColor, 0.1)
grid10Color = alphaColor(gridColor, 0.3)
grid100Color = alphaColor(gridColor, 0.6)

textSettings = dict(
    padding=(5, 2),
    horizontalAlignment="center",
    verticalAlignment="center",
    backgroundColor=backgroundColor,
    fillColor=textColor,
    figureStyle="tabular",
    pointSize=12 ,
    weight="light"
)


class GridView(Subscriber):

    debug = False

    def getGlyph(self):
        editor = self.getGlyphEditor()
        glyph = editor.getGlyph()
        if glyph is not None:
            glyph = glyph.asFontParts()
        return glyph

    def getFont(self):
        editor = self.getGlyphEditor()
        document = editor.document
        font = document.getFont()
        if font is not None:
            font = font.asFontParts()
        return font

    def build(self):
        editor = self.getGlyphEditor()
        self.container = container = editor.extensionContainer(
            identifierStub + ".dynamicGrid",
            location="background",
            clear=True
        )
        container.clearSublayers()
        self.buildGrids()

    def started(self):
        self.zoomGrid()

    def glyphEditorDidScale(self, info):
        self.zoomGrid()

    def buildGrids(self):
        container = self.container
        font = self.getFont()
        upm = font.info.unitsPerEm
        xMaximum = roundUp(upm * 5, 100)
        xMinimum = roundDown(-xMaximum, 100)
        yMaximum = roundUp(upm * 1.5, 100)
        yMinimum = roundDown(-yMaximum, 100)
        xTextMinimum = roundDown(upm * -0.75, 100)
        xTextMaximum = roundUp(upm * 1.5, 100)
        yTextMinimum = roundDown(upm * -0.5, 100)
        yTextMaximum = roundUp(upm * 1.25, 100)

        width = abs(xMinimum) + xMaximum
        height = abs(yMinimum) + yMaximum

        # lines

        x1Positions = [
            i for i in range(xMinimum, xMaximum, 1)
            if i != 0
            and i % 100
            and i % 10
        ]
        x10Positions = [
            i for i in range(xMinimum, xMaximum, 10)
            if i != 0
            and i % 100
        ]
        x100Positions = [
            i for i in range(xMinimum, xMaximum, 100)
        ]

        y1Positions = [
            i for i in range(yMinimum, yMaximum, 1)
            if i != 0
            and i % 100
            and i % 10
        ]
        y10Positions = [
            i for i in range(yMinimum, yMaximum, 10)
            if i != 0
            and i % 100
        ]
        y100Positions = [
            i for i in range(yMinimum, yMaximum, 100)
        ]

        def drawGrid(layer, xPositions, yPositions):
            pen = merz.MerzPen()
            for x in xPositions:
                pen.moveTo((x, yMinimum))
                pen.lineTo((x, yMaximum))
                pen.endPath()
            for y in yPositions:
                pen.moveTo((xMinimum, y))
                pen.lineTo((xMaximum, y))
                pen.endPath()
            layer.setPath(pen.path)

        grid1PathLayer = container.appendPathSublayer(
            name="lines.1",
            strokeColor=grid1Color,
            strokeWidth=1
        )
        drawGrid(grid1PathLayer, x1Positions, y1Positions)
        grid1PathLayer.getCALayer().setShouldRasterize_(True)

        grid10PathLayer = container.appendPathSublayer(
            name="lines.10",
            strokeColor=grid10Color,
            strokeWidth=1
        )
        drawGrid(grid10PathLayer, x10Positions, y10Positions)
        grid10PathLayer.getCALayer().setShouldRasterize_(True)

        grid100PathLayer = container.appendPathSublayer(
            name="lines.100",
            strokeColor=grid100Color,
            strokeWidth=1
        )
        drawGrid(grid100PathLayer, x100Positions, y100Positions)
        grid100PathLayer.getCALayer().setShouldRasterize_(True)

        # text

        xTextPositions = [
            i for i in range(xTextMinimum, xTextMaximum, 100)
        ]
        yTextPositions = [
            i for i in range(yTextMinimum, yTextMaximum, 100)
        ]

        grid100TextLayer = container.appendBaseSublayer(
            name="text.100"
        )
        grid200TextLayer = container.appendBaseSublayer(
            name="text.200"
        )
        with grid200TextLayer.sublayerGroup():
            with grid100TextLayer.sublayerGroup():
                for x in xTextPositions:
                    for y in yTextPositions:
                        t = None
                        if x % 200 or y % 200:
                            t = grid100TextLayer
                        elif not x % 200 and not y % 200:
                            t = grid200TextLayer
                        if t is not None:
                            l = t .appendTextLineSublayer(
                                position=(x, y),
                                text=f"{x} {y}",
                                **textSettings
                            )

    def zoomGrid(self):
        container = self.container
        scale = container.getCumulativeSublayerTransformation()[0]
        # 1 unit
        grid1PathLayer = container.getSublayer("lines.1")
        grid1PathLayer.setVisible(scale > 5)
        # 10 units
        grid10PathLayer = container.getSublayer("lines.10")
        grid10PathLayer.setVisible(scale > 0.5)
        # 100 units
        grid100PathLayer = container.getSublayer("lines.100")
        grid100PathLayer.setVisible(scale > 0.1)
        # 100 units text
        text100PathLayer = container.getSublayer("text.100")
        text100PathLayer.setVisible(scale > 1.0)
        # 200 units text
        text200PathLayer = container.getSublayer("text.200")
        text200PathLayer.setVisible(scale > 0.3)


# -----
# Tools
# -----

def roundUp(n, v=1):
    n -= n % -v
    return int(n)

def roundDown(n, v=1):
    n -= n % v
    return int(n)


# --
# Go
# --

registerGlyphEditorSubscriber(GridView)