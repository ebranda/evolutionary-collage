add_library('opencv_processing')
from gab.opencv import OpenCV

cv = None


def detect(img, scalefactor, threshold, tolerance, drawblobs=True):
    if not isinstance(img, PImage):
        img = PImage(img.getImage()) # Convert PGraphics to PImage because OpenCV requires PImage
    img = img.copy()
    img.resize(int(round(scalefactor * img.width)), 0)
    global cv
    if cv is None:
        cv = OpenCV(this, img.width, img.height)
    cv.loadImage(img)
    cv.gray()
    cv.threshold(threshold)
    cv.invert()
    for i in range(abs(tolerance)):
        if tolerance < 0:
            cv.erode()
        else:
            cv.dilate()
    #cv.open(tolerance)
    findholes = False
    sortlargest = True
    contours = cv.findContours(findholes, sortlargest)
    blobs = [Blob(contour, scalefactor) for contour in contours]
    if drawblobs:
        for blob in blobs:
            blob.draw()
    return blobs


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        

class Blob(object):
    
    def __init__(self, contour, scalefactor):
        self.verts = contour.getPolygonApproximation().getPoints()
        for v in self.verts:
            v.x /= scalefactor
            v.y /= scalefactor
        
    def area(self):
        '''Compute the area of a closed polygon represented by
        a list of vertices where each vertex is an object 
        x and y attributes. Uses cross-product method. See
        https://web.archive.org/web/20100405070507/http://valis.cs.uiuc.edu/~sariel/research/CG/compgeom/msg00831.html
        '''
        segments = zip(self.verts, self.verts[1:] + [self.verts[0]])
        return 0.5 * abs(sum(v0.x*v1.y - v1.x*v0.y for (v0, v1) in segments))
    
    def polygon(self):
        return self.verts + [self.verts[0]] # Return closed list of vertices
    
    def center(self):
        '''Compute the center (average) of a list of points (not a true centroid).'''
        x = y = 0.0
        for v in self.verts:
            x += v.x
            y += v.y
        return Point(x / len(self.verts), y / len(self.verts))
        
    def draw(self):
        stroke(255,0,0)
        fill(255, 200, 200, 150)
        with beginShape():
            for v in self.polygon():
                vertex(v.x, v.y)
        return # Don't draw label for now
        noStroke()
        fill(0, 0, 255)
        c = self.center()
        textAlign(CENTER)
        text("a={}".format(self.area()), c.x, c.y)






    