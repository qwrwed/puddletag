# -*- coding: utf-8 -*-
from PyQt5.QtCore import QBuffer, QIODevice, QRect, Qt
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QBrush
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ..audioinfo.util import commonimages
from ..constants import RIGHTDOCK, SELECTIONCHANGED
from ..puddleobjects import PicWidget
from ..translations import translate


def svg_to_pic(data, desc):
    return {'data': data, 'size': len(data),
            'description': desc, 'imagetype': 3}


def get_font(rect, *text):
    font = QFont()
    lengths = [(t, QFontMetrics(font).horizontalAdvance(t)) for t in text]
    lowest = max(lengths, key=lambda x: x[1])
    size = 12
    while QFontMetrics(font).horizontalAdvance(lowest[0]) < rect.width() - 30:
        font.setPointSize(size)
        size += 1
    return font


def create_svg(text, font, rect=None):
    if not rect:
        rect = QRect(0, 0, 200, 200)
    # Rendered into memory: Windows refuses to reopen a NamedTemporaryFile while it is still open.
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)

    generator = QSvgGenerator()
    generator.setOutputDevice(buf)
    generator.setSize(rect.size())
    generator.setViewBox(rect)
    generator.setTitle("puddletag image")
    generator.setDescription("just to see")

    painter = QPainter()
    painter.begin(generator)
    painter.fillRect(rect, Qt.GlobalColor.black)
    painter.setFont(font)
    painter.setPen(Qt.GlobalColor.white)
    painter.setBrush(QBrush(Qt.GlobalColor.white))
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    painter.end()

    buf.close()
    return bytes(buf.data()).decode('utf-8')


class ArtworkWidget(QWidget):
    """Shows the selected files' covers the way Mp3tag's cover window does.

    One file, or files sharing the same covers: the covers, with arrows to step
    between them when there is more than one. Files whose covers differ: a
    placeholder saying so. No covers: an empty frame. Covers are added, changed,
    removed, saved, copied and pasted from the right-click menu, and saving the
    Tag Panel writes covers only after one of those changes."""

    def __init__(self, parent=None, status=None):
        QWidget.__init__(self, parent)
        self.receives = [(SELECTIONCHANGED, self.fill)]
        self.emits = []
        self.picwidget = PicWidget()
        self.picwidget.showbuttons = False
        self.picwidget.imageChanged.connect(self._changed)
        vbox = QVBoxLayout()
        vbox.addWidget(self.picwidget)
        hbox = QHBoxLayout()
        hbox.addStrut(1)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        status['images'] = self.images
        self._audios = []
        self._status = status
        self._variesPic = None
        self._varies = False
        self._dirty = False

    def _changed(self):
        self._dirty = True
        if self._varies and self.picwidget.readonly:
            placeholder = self._variesPic['data']
            if all(z.get('data') != placeholder for z in self.picwidget.images):
                # The placeholder was replaced, so the cover shown is a real one.
                self.picwidget.readonly = []
                if self.picwidget.images:
                    self.picwidget.currentImage = self.picwidget.currentImage

    def _variesPicture(self):
        if not self._variesPic:
            text = translate('Artwork', 'Covers vary')
            self._variesPic = svg_to_pic(create_svg(text, get_font(QRect(0, 0, 200, 200), text)), text)
        return dict(self._variesPic)

    def fill(self, audios=None):
        if audios is None:
            audios = self._status['selectedfiles']
        self._dirty = False
        self._varies = False
        if not audios:
            self.picwidget.setEnabled(False)
            self.picwidget.setImages(None)
            return
        if not self.isVisible():
            self._audios = audios
            return
        self.picwidget.currentFile = audios[0]
        self.picwidget.filePattern = self._status['cover_pattern']
        self.picwidget.setEnabled(True)
        images = []
        imagetags = set()
        for audio in audios:
            imagetags = imagetags.union(audio.IMAGETAGS)
            if audio.IMAGETAGS:
                images.append(audio.images)
            else:
                images.append({})

        self.picwidget.lastfilename = audios[0].filepath
        images = commonimages(images)
        self.picwidget.setImageTags(imagetags)

        if images == 0:
            # The placeholder can be changed or removed, which replaces or removes
            # every selected file's covers, but not copied, saved or described.
            self._varies = True
            self.picwidget.readonly = [0]
            self.picwidget.setImages([self._variesPicture()])
            self.picwidget.editpic.setEnabled(bool(imagetags))
            self.picwidget.removepic.setEnabled(bool(imagetags))
        elif images is None:
            self.picwidget.readonly = []
            self.picwidget.setImages(None)
        else:
            self.picwidget.readonly = []
            self.picwidget.setImages(list(images))

        if imagetags:
            self.setEnabled(True)
        else:
            self.setEnabled(False)

    def init(self):
        self.picwidget.readonly = []
        self.picwidget.setImages(None)

    def images(self):
        """None leaves every selected file's covers as they are; a list, empty
        or not, becomes the covers of every selected file."""
        if not self._dirty:
            return None
        images = self.picwidget.images
        if self._varies:
            placeholder = self._variesPic['data']
            images = [z for z in images if z.get('data') != placeholder]
        return images

    def showEvent(self, event):
        QWidget.showEvent(self, event)
        if self._audios:
            self.fill(self._audios)
            self._audios = []


control = ('Artwork', ArtworkWidget, RIGHTDOCK, False)
