import math
import AppKit
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

# def alphaColor(color, alpha):
#     r, g, b, a = color
#     return (r, g, b, alpha)
#
# textSettings = dict(
#     padding=(5, 2),
#     horizontalAlignment="center",
#     verticalAlignment="center",
#     backgroundColor=backgroundColor,
#     fillColor=textColor,
#     figureStyle="tabular",
#     pointSize=12 ,
#     weight="light"
# )





class GridView2(Subscriber):

    debug = True

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
        self.loadDefaults()
        self.buildBases()

    # Delegate Actions
    # ----------------

    def started(self):
        pass

    def preferencesChanged(self, info):
        self.loadDefaults()
        self.buildImageContainers()
        self.populateImageContainers()

    def glyphEditorDidSetGlyph(self, info):
        self.buildImageContainers()
        self.populateImageContainers()

    def glyphEditorDidScale(self, info):
        self.populateImageContainers()

    def glyphEditorGlyphDidChangeMetrics(self, info):
        self.buildImageContainers()
        self.populateImageContainers()

    # Defaults
    # --------

    def loadDefaults(self):
        self.gridBuffer = getDefault("glyphViewGridBorder")
        self.backgroundColor = getDefault("glyphViewBackgroundColor")
        self.gridColor = getDefault("glyphViewGridColor")
        self.gridColor = (1, 0, 0, 1)
        self.textColor = self.gridColor
        self.grid1Color = scaleColorAlpha(self.gridColor, 0.1)
        self.grid10Color = scaleColorAlpha(self.gridColor, 0.3)
        self.grid100Color = self.gridColor

    gridBuiltForWidth = None
    gridBuiltForDescender = None
    gridBuiltForUPM = None
    gridBuiltForBuffer = None

    def buildBases(self):
        container = self.container
        container.clearSublayers()
        self.grid1Base = container.appendBaseSublayer(
            name="grid1Base"
        )
        self.grid10Base = container.appendBaseSublayer(
            name="grid10Base"
        )
        self.grid100Base = container.appendBaseSublayer(
            name="grid100Base"
        )

    def clearBases(self):
        self.grid1Base.clearSublayers()
        self.grid10Base.clearSublayers()
        self.grid100Base.clearSublayers()

    def buildImageContainers(self):
        container = self.container
        glyph = self.getGlyph()
        if glyph is None:
            self.clearBases()
            return
        font = self.getFont()
        needRebuild = False
        if self.gridBuffer != self.gridBuiltForBuffer:
            needRebuild = True
        elif glyph.width != self.gridBuiltForWidth:
            needRebuild = True
        elif font.info.descender != self.gridBuiltForDescender:
            needRebuild = True
        elif font.info.unitsPerEm == self.gridBuiltForUPM:
            needRebuild = True
        if not needRebuild:
            return
        self.gridBuiltForWidth = glyph.width
        self.gridBuiltForDescender = font.info.descender
        self.gridBuiltForUPM = font.info.unitsPerEm
        self.gridBuiltForBuffer = self.gridBuffer

        xMinimum, xMaximum = sorted((0, glyph.width))
        xMinimum = roundDown(xMinimum - self.gridBuffer, 100)
        xMaximum = roundUp(xMaximum + self.gridBuffer, 100)
        yMinimum = roundDown(font.info.descender - self.gridBuffer, 100)
        yMaximum = roundUp(font.info.unitsPerEm + self.gridBuffer, 100)
        self.clearBases()

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

        self.grid100Containers = []
        for x in x100Positions:
            for y in y100Positions:
                layer = self.grid100Base.appendImageSublayer(
                    position=(x, y),
                    size=(100, 100),
                    alignment="center"
                    # backgroundColor=(1, 0, 0, 0.2),
                    # borderColor=(1, 0, 0, 1),
                    # borderWidth=1
                )
                self.grid100Containers.append(layer)



#
#         # lines
#

#
#         def drawGrid(layer, xPositions, yPositions):
#             pen = merz.MerzPen()
#             for x in xPositions:
#                 pen.moveTo((x, yMinimum))
#                 pen.lineTo((x, yMaximum))
#                 pen.endPath()
#             for y in yPositions:
#                 pen.moveTo((xMinimum, y))
#                 pen.lineTo((xMaximum, y))
#                 pen.endPath()
#             layer.setPath(pen.path)
#
#         grid1PathLayer = container.appendPathSublayer(
#             name="lines.1",
#             strokeColor=grid1Color,
#             strokeWidth=1
#         )
#         drawGrid(grid1PathLayer, x1Positions, y1Positions)
#         grid1PathLayer.getCALayer().setShouldRasterize_(True)
#
#         grid10PathLayer = container.appendPathSublayer(
#             name="lines.10",
#             strokeColor=grid10Color,
#             strokeWidth=1
#         )
#         drawGrid(grid10PathLayer, x10Positions, y10Positions)
#         grid10PathLayer.getCALayer().setShouldRasterize_(True)
#
#         grid100PathLayer = container.appendPathSublayer(
#             name="lines.100",
#             strokeColor=grid100Color,
#             strokeWidth=1
#         )
#         drawGrid(grid100PathLayer, x100Positions, y100Positions)
#         grid100PathLayer.getCALayer().setShouldRasterize_(True)
#
#         # text
#
#         xTextPositions = [
#             i for i in range(xTextMinimum, xTextMaximum, 100)
#         ]
#         yTextPositions = [
#             i for i in range(yTextMinimum, yTextMaximum, 100)
#         ]
#
#         grid100TextLayer = container.appendBaseSublayer(
#             name="text.100"
#         )
#         grid200TextLayer = container.appendBaseSublayer(
#             name="text.200"
#         )
#         with grid200TextLayer.sublayerGroup():
#             with grid100TextLayer.sublayerGroup():
#                 for x in xTextPositions:
#                     for y in yTextPositions:
#                         t = None
#                         if x % 200 or y % 200:
#                             t = grid100TextLayer
#                         elif not x % 200 and not y % 200:
#                             t = grid200TextLayer
#                         if t is not None:
#                             l = t .appendTextLineSublayer(
#                                 position=(x, y),
#                                 text=f"{x} {y}",
#                                 **textSettings
#                             )

    def populateImageContainers(self):
        container = self.container
        scale = container.getCumulativeSublayerTransformation()[0]
        if scale < 0.1:
            self.grid100Base.setVisible(False)
        else:
            self.make100Image(scale)
            for layer in self.grid100Containers:
                layer.setBackgroundColor((1, 1, 0, 0.25))
                # layer.setImage(self.grid100Image)
            self.grid100Base.setVisible(True)

    def make100Image(self, unit):
        size = unit * 100
        image = AppKit.NSImage.alloc().initWithSize_((size, size))
        image.lockFocus()
        AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
            *self.grid100Color
        ).set()
        path = AppKit.NSBezierPath.bezierPathWithRect_(
            ((0, 0), (size, size))
        )
        path.setLineWidth_(1.0 / unit)
        path.stroke()
        image.unlockFocus()
        self.grid100Image = image

    # def zoomGrid(self):
    #     pass
        # container = self.container
        # scale = container.getCumulativeSublayerTransformation()[0]
        # # 1 unit
        # grid1PathLayer = container.getSublayer("lines.1")
        # grid1PathLayer.setVisible(scale > 5)
        # # 10 units
        # grid10PathLayer = container.getSublayer("lines.10")
        # grid10PathLayer.setVisible(scale > 0.5)
        # # 100 units
        # grid100PathLayer = container.getSublayer("lines.100")
        # grid100PathLayer.setVisible(scale > 0.1)
        # # 100 units text
        # text100PathLayer = container.getSublayer("text.100")
        # text100PathLayer.setVisible(scale > 1.0)
        # # 200 units text
        # text200PathLayer = container.getSublayer("text.200")
        # text200PathLayer.setVisible(scale > 0.3)


# -----
# Tools
# -----

def roundUp(n, v=1):
    n -= n % -v
    return int(n)

def roundDown(n, v=1):
    n -= n % v
    return int(n)

def scaleColorAlpha(color, scale):
    r, g, b, a = color
    a *= scale
    return (r, g, b, a)

# --
# Go
# --

registerGlyphEditorSubscriber(GridView2)