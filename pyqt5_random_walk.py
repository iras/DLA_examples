import sys, random
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer


# graphics canvas boilerplate code.
class App( QMainWindow ):

    def __init__( self ):
        super().__init__()
        self.title = 'random walk'
        self.left = 20
        self.top = 20
        self.width = 200
        self.height = 200
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
        self.timer.start( 1.6 )

        self.show()


class PaintWidget( QWidget ):

    def __init__( self, item ):
        super().__init__( item )
        self.x = 100
        self.y = 100

    def paintEvent( self, event ):
        qp = QPainter( self )
        qp.setPen( Qt.white )

        self.x += random.randint( -1, 1 )
        self.y += random.randint( -1, 1 )

        qp.drawPoint( self.x, self.y )



if __name__ == '__main__':
    app = QApplication( sys.argv )
    ex = App()
    sys.exit( app.exec_() )