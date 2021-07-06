import time
import traceback
from Foundation import NSLog
import AppKit
import ezui
import merz
from lib.tools.debugTools import ClassNameIncrementer
from mojo.UI import getDefault
from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber

from Quartz import (
    CATiledLayer,
    CGContextGetClipBoundingBox,
    CGContextDrawImage,
    CGBitmapContextCreate,
    CGColorSpaceCreateWithName,
    kCGColorSpaceGenericRGB,
    kCGImageAlphaPremultipliedLast,
    CGContextSetShouldAntialias,
    CGContextSetLineWidth,
    CGContextSetRGBStrokeColor,
    CGContextStrokeRectWithWidth,
    CGBitmapContextCreateImage,
    CGContextBeginPath,
    CGContextMoveToPoint,
    CGContextAddLineToPoint,
    CGContextStrokePath
)

identifierStub = "com.typesupply.GridView."

import objc
objc.setVerbose(True)


null = AppKit.NSNull.null()


class GridViewTiledLayer(CATiledLayer, metaclass=ClassNameIncrementer):

    def init(self):
        self = super().init()
        self._tileImage = None
        self._convertedTileImage = None
        self.setDrawsAsynchronously_(True)
        self.setContentsScale_(AppKit.NSScreen.mainScreen().backingScaleFactor())
        self.setAnchorPoint_((0, 0))
        self.setTileSize_((100, 100))
        return self

    # def fadeDuration(self):
    #     return 0.5

    def defaultActionForKey_(self, key):
        return null

    def drawInContext_(self, ctx):
        try:
            rect = CGContextGetClipBoundingBox(
                ctx
            )
            CGContextDrawImage(
                ctx,
                rect,
                self._tileImage
            )
        except:
            t = time.time()
            tb = repr(traceback.format_exc())
            NSLog(f"> {t}")
            NSLog(tb)
            NSLog(f"< {t}")

    def setTileImage_(self, image):
        self._tileImage = image


class Grid(merz.Base):

    caLayerClass = GridViewTiledLayer

    def reset(self):
        contentsScale = self.getCALayer().contentsScale()
        scale = self.getCumulativeLayerTransformation()[0]
        scale *= contentsScale
        size = 100 * scale
        image = self._makeImage(scale, size)
        layer = self.getCALayer()
        layer.setTileSize_((size, size))
        layer.setTileImage_(image)
        layer.setNeedsDisplayInRect_(
            ((0, 0), (0, 0))
        )

    def _makeImage(self, scale, size):
        pixel = 1
        # https://developer.apple.com/documentation/coregraphics/1455939-cgbitmapcontextcreate?language=objc
        context = CGBitmapContextCreate(
            None,
            size,
            size,
            8,
            0,
            CGColorSpaceCreateWithName(kCGColorSpaceGenericRGB),
            kCGImageAlphaPremultipliedLast
        )
        CGContextSetShouldAntialias(context, True)
        CGContextSetLineWidth(context, pixel)

        whyDoesThisCauseAlignmentProblems = 28.0

        # 1 unit
        if scale > 5 and scale < whyDoesThisCauseAlignmentProblems:
            positions = [
                i
                for i in range(0, 100, 1)
                if i % 100
                and i % 10
            ]
            CGContextSetRGBStrokeColor(
                context,
                *self.color1
            )
            drawQuartzLines(context, positions, scale)
        # 10 units
        if scale > 0.5 and scale < whyDoesThisCauseAlignmentProblems:
            positions = [
                i
                for i in range(0, 100, 10)
                if i % 100
            ]
            CGContextSetRGBStrokeColor(
                context,
                *self.color10
            )
            drawQuartzLines(context, positions, scale)
        # 100 units
        if scale > 0.1 and scale < whyDoesThisCauseAlignmentProblems:
            CGContextSetRGBStrokeColor(
                context,
                *self.color100
            )
            CGContextStrokeRectWithWidth(
                context,
                ((0, 0), (size, size)),
                pixel
            )

        image = CGBitmapContextCreateImage(context)
        return image

    def setColor(self, color):
        self.color1 = scaleColorAlpha(color, 0.2)
        self.color10 = scaleColorAlpha(color, 0.3)
        self.color100 = color


class GridViewTiledTest(Subscriber):

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
        # XXX
        # these are arbitrarily chosen "big" numbers.
        # it would be better to get the actual drawing board size.
        p = -1000
        s = 5000
        self.grid = container.appendSublayerOfClass(
            layerClass=Grid,
            position=(p, p),
            size=(s, s),
        )
        self.loadDefaults()

    # Delegate Actions
    # ----------------

    def started(self):
        self.grid.reset()

    def preferencesChanged(self, info):
        self.loadDefaults()
        self.grid.reset()

    # def glyphEditorDidSetGlyph(self, info):
    #     self.grid.reset()

    def glyphEditorDidScale(self, info):
        self.grid.reset()

    # def glyphEditorGlyphDidChangeMetrics(self, info):
    #     self.grid.reset()

    # Defaults
    # --------

    def loadDefaults(self):
        self.backgroundColor = getDefault("glyphViewBackgroundColor")
        self.gridColor = getDefault("glyphViewGridColor")
        self.gridColor = (0, 0, 0, 1)
        self.textColor = self.gridColor
        self.grid.setColor(self.gridColor)

# -----
# Tools
# -----

def scaleColorAlpha(color, scale):
    r, g, b, a = color
    a *= scale
    return (r, g, b, a)

def drawQuartzLines(ctx, positions, scale):
    CGContextBeginPath(ctx)
    hundred = 100 * scale
    for p in positions:
        p *= scale
        CGContextMoveToPoint(ctx, p, 0)
        CGContextAddLineToPoint(ctx, p, hundred)
        CGContextMoveToPoint(ctx, 0, p)
        CGContextAddLineToPoint(ctx, hundred, p)
    CGContextStrokePath(ctx)

# --
# Go
# --

registerGlyphEditorSubscriber(GridViewTiledTest)