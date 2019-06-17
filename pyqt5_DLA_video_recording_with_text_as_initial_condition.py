import os, sys, random
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2


# Diffusion-limited aggregation example.
# MIT License.


# NB: unoptimised Python 3 code - very slow!


def add_text_outline( img, text, font, outline_col, pos_x, pos_y, thick ):
    drawer = ImageDraw.Draw( img )
    w = pos_x - thick, pos_y;             e = pos_x + thick, pos_y
    s = pos_x, pos_y - thick;             n = pos_x, pos_y + thick
    sw = pos_x + thick, pos_y - thick;   nw = pos_x + thick, pos_y + thick
    se = pos_x - thick, pos_y - thick;   ne = pos_x - thick, pos_y + thick
    central = ( pos_x, pos_y )
    drawer.text( w,  text, font=font, fill=outline_col )
    drawer.text( s,  text, font=font, fill=outline_col )
    drawer.text( e,  text, font=font, fill=outline_col )
    drawer.text( n,  text, font=font, fill=outline_col )
    drawer.text( sw, text, font=font, fill=outline_col )
    drawer.text( se, text, font=font, fill=outline_col )
    drawer.text( ne, text, font=font, fill=outline_col )
    drawer.text( nw, text, font=font, fill=outline_col )
    drawer.text( central,  text, font=font, fill=(0) )



SIZE_MTX = 640
HALF_SIZE = int( SIZE_MTX / 2 )

# convert an image with some text to a np matrix.
img = Image.new( mode='L', size=( SIZE_MTX, SIZE_MTX ), color=(0) )
add_text_outline(
    img,
    'diffusion-limited\naggregation',
    ImageFont.truetype( font='/Library/Fonts/Verdana.ttf', size=40 ),
    (255),
    170,
    250,
    2,
)
MTX = np.asarray( img, dtype=np.uint8 ).copy()

# create initial np matrix with central white dot.
#MTX = np.zeros( (SIZE_MTX, SIZE_MTX), dtype=np.uint8 )
#MTX [HALF_SIZE, HALF_SIZE] = 255  # initial central seed.

VIDEO = cv2.VideoWriter(
    os.path.expanduser( '~/Desktop/DLA_example.avi' ),
    cv2.VideoWriter_fourcc( *'XVID' ),
    120,
    ( SIZE_MTX, SIZE_MTX )
)


# graphics canvas init boilerplate code.
class App( QMainWindow ):

    def __init__( self ):
        super().__init__()
        self.title = 'DLA example'
        self.left = 20
        self.top = 20
        self.width = SIZE_MTX
        self.height = SIZE_MTX
        self.initUI()

    def initUI( self ):
        self.setWindowTitle( self.title )
        self.setGeometry( self.left, self.top, self.width, self.height )

        # Set window background color
        self.setAutoFillBackground( True )
        p = self.palette()
        p.setColor( self.backgroundRole(), Qt.black )
        self.setPalette( p )

        # Add paint widget and paint
        self.m = PaintWidget( self )
        self.m.move( 0, 0 )
        self.m.resize( self.width, self.height )

        self.timer = QTimer()
        self.timer.timeout.connect( self.m.update )
        self.timer.start( 1 )

        self.show()


class PaintWidget( QWidget ):

    def __init__( self, item ):
        super().__init__( item )
        self.img_counter = 0

    def paintEvent( self, event ):
        qp = QPainter( self )
        qp.setPen( Qt.red )

        # the new matrix will contain both the DLA and the random walk.
        DLA_and_random_walk_mtx = MTX.copy()

        # init random_walk item on the matrix's edge.
        rnd_start_on_border = random.randint( 1, 4*SIZE_MTX-1 )
        if rnd_start_on_border <= SIZE_MTX:
            bx = SIZE_MTX - rnd_start_on_border
            by = 0
        elif rnd_start_on_border <= 2*SIZE_MTX:
            bx = SIZE_MTX-1
            by = 2*SIZE_MTX - rnd_start_on_border
        elif rnd_start_on_border <= 3*SIZE_MTX:
            bx = 3*SIZE_MTX - rnd_start_on_border
            by = SIZE_MTX-1
        else:
            bx = 0
            by = 4*SIZE_MTX - rnd_start_on_border
        
        # random walk until hitting an existing element in the mtx.
        self.x = bx
        self.y = by
        while MTX[ self.x, self.y ] != 255:

            prev_x = self.x
            prev_y = self.y

            DLA_and_random_walk_mtx[ prev_x, prev_y ] = 10

            self.x += random.randint( -1, 1 )
            self.y += random.randint( -1, 1 )

            # freeze ordinates if random walk heads outside boundaries.
            if self.x < 1 or self.x >= SIZE_MTX:
                self.x = prev_x
            if self.y < 1 or self.y >= SIZE_MTX:
                self.y = prev_y

        try:
            MTX[ prev_x, prev_y ] = 255
        except:
            exit()

        # display DLA mtx.
        qimage = QImage(
            DLA_and_random_walk_mtx,
            SIZE_MTX,
            SIZE_MTX,
            QImage.Format_Indexed8
        )
        qimage.setColorTable( [] )
        qp.drawPixmap( 0, 0, QPixmap.fromImage( qimage ) )

        # display random walk's starting point (red).
        qp.drawPoint( bx, by )

        # generate image and append to video.
        VIDEO.write(
            cv2.cvtColor( DLA_and_random_walk_mtx, cv2.COLOR_GRAY2BGR )
        )
        self.img_counter += 1

        """
        # alternative more expensive way to write to video.
        img_filename = os.path.expanduser(
            '~/Desktop/screenshot_%s.png' % self.img_counter
        )
        Image.fromarray( DLA_and_random_walk_mtx ).save( img_filename )
        VIDEO.write( cv2.imread( img_filename ) )
        """


if __name__ == '__main__':
    app = QApplication( sys.argv )
    ex = App()
    sys.exit( app.exec_() )
