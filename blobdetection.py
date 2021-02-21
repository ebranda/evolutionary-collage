try:
    add_library('opencv_processing')
    from gab.opencv import OpenCV
    #from gab.opencv import Line
except Exception as e:
    print("Error loading blobdetection module: {}".format(e))

import math
import random 

cv = None


def detect(img, scalefactor, threshold, tolerance, drawblobs=True, polygonfactor=1.0, findholes=False, drawimage=False):
    img = img.copy() # Also required in case img is a PGraphics instance. OpenCV requires PImage.
    img.resize(int(round(scalefactor * img.width)), 0)
    global cv
    if cv is None:
        cv = OpenCV(this, img.width, img.height)
    cv.loadImage(img)
    cv.gray()
    cv.threshold(threshold)
    cv.invert()
    if drawimage:
        image(cv.getSnapshot(), 0, 0)
    for i in range(abs(tolerance)):
        if tolerance < 0:
            cv.erode()
        else:
            cv.dilate()
    #for t in range(tolerance):
    #    cv.open(tolerance)
    sortlargest = True
    contours = cv.findContours(findholes, sortlargest)
    blobs = [Blob(contour, scalefactor, polygonfactor) for contour in contours]
    if drawblobs:
        for blob in blobs:
            blob.draw()
    return blobs
    

def get_rgb(img):
    global cv
    if cv is None:
        cv = OpenCV(this, img.width, img.height)
    cv.loadImage(img)
    r = cv.getSnapshot(cv.getR())
    g = cv.getSnapshot(cv.getG())
    b = cv.getSnapshot(cv.getB())
    return (r,g,b)

def get_hsb(img):
    global cv
    if cv is None:
        cv = OpenCV(this, img.width, img.height)
    cv.useColor(HSB)
    cv.loadImage(img)
    h = cv.getSnapshot(cv.getH())
    s = cv.getSnapshot(cv.getS())
    v = cv.getSnapshot(cv.getV())
    return (h,s,v)
    


def threshold(img, level):
    global cv
    if cv is None:
        cv = OpenCV(this, img.width, img.height)
    img.filter(BLUR, 0.5)
    cv.loadImage(img)
    cv.threshold(level)
    return cv.getSnapshot()

    
def multithreshold(img, levels, open=0):
    global cv
    if cv is None:
        cv = OpenCV(this, img.width, img.height)
    outputimages = []
    for level in range(len(levels)):
        cv.loadImage(img)
        cv.gray()
        cv.threshold(level)
        if open:
            cv.open(open)
        outputimages.append(cv.getSnapshot())
    return outputimages
        
    
def detect_lines(img, linethresh, minlinelength, maxlinegap, open=0, drawlines=True, drawimage=False):
    '''Find lines in an image
    https://docs.opencv.org/3.4/d3/de6/tutorial_js_houghlines.html
    https://github.com/atduskgreg/opencv-processing/blob/master/examples/HoughLineDetection/HoughLineDetection.pde
    https://github.com/atduskgreg/opencv-processing/blob/master/src/gab/opencv/OpenCV.java findLines() function
    '''
    global cv
    if cv is None:
        cv = OpenCV(this, img.width, img.height)
    cv.loadImage(img)
    cv.threshold(128)
    if open:
        cv.open(open)
    cv.findCannyEdges(128, 200)
    lines = [Line(l.start.x, l.start.y, l.end.x, l.end.y) for l in cv.findLines(linethresh, minlinelength, maxlinegap)]
    if drawimage:
        preview = cv.getSnapshot()
        image(preview, 0, 0, preview.width, preview.height)
    if drawlines:
        strokeWeight(2)
        stroke(0, 255, 0)
        for l in lines:
            line(l.start.x, l.start.y, l.end.x, l.end.y)
    return lines


class Line(object):
    
    def __init__(self, x0, y0, x1, y1):
        self.start = Point(x0, y0)
        self.end = Point(x1, y1)
        self.dx = self.end.x - self.start.x
        self.dy = self.end.y - self.start.y
        self.length = math.sqrt(self.dx**2 + self.dy**2)
        self.angle = self.angle_to(0.0, 1.0)
    
    def vector(self):
        return self.end.x - self.start.x, self.end.y - self.start.y
    
    def angle_to(self, vx, vy, smallest=True):
        a, b = self.vector()
        c, d = vx, vy
        dotProduct = a*c + b*d
        mod = math.sqrt(a*a + b*b) * math.sqrt(c*c + d*d) 
        if mod == 0: return 0
        anglecos = dotProduct/mod
        angledeg = math.degrees(math.acos(anglecos))
        if smallest and angledeg > 90.0:
            angledeg = 180 - angledeg
        return angledeg
        

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        

class Blob(object):
    
    def __init__(self, contour, scalefactor, polygonfactor):
        contour.setPolygonApproximationFactor(contour.getPolygonApproximationFactor() * polygonfactor)
        self.verts = contour.getPolygonApproximation().getPoints()
        for v in self.verts:
            v.x /= scalefactor
            v.y /= scalefactor
        self.edges = []
        for i in range(len(self.verts)):
            p0 = self.verts[i]
            p1 = self.verts[0] if i == len(self.verts)-1 else self.verts[i+1]
            self.edges.append(Line(p0.x, p0.y, p1.x, p1.y))
            
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




def sihouette_score(clusters):
    '''
    The Silhouette Coefficient for a sample is (b-a) / max(a, b). 
    Intra-cluster distance (a) is distance of sample point to its
    centroid and (b) is distance of sample point to nearest cluster 
    to which it belongs. The higher the result, the better the value
    used for k in the clustering.
    '''
    coefficients = []
    for cluster in clusters:
        for sample in cluster.samples:
            a = cluster.dist_to_centroid(sample)
            b = min(other.dist_to_centroid(sample) for other in clusters if other.c != cluster.c)
            s = float(b - a) / max(a, b)
            coefficients.append(s)
    return sum(coefficients) / len(coefficients)
        
class Cluster(object):
    def __init__(self, c, samples=[]):
        self.c = c
        self.samples = samples
        if samples:
            self.update()
    def add(self, sample):
        self.samples.append(sample)
    def clear(self):
        self.samples = []
    def dist_to_centroid(self, sample):
        return abs(sample-self.c)
    def update(self):
        if self.samples:
            self.c = float(sum(self.samples)) / len(self.samples)
            self.sum = sum(self.samples)
        else:
            self.sum = 0.0


def kmeans(samples, k, max_iterations=100):
    clusters = []
    for centroid in random.sample(samples, k):
        clusters.append(Cluster(centroid)) 
    done = False
    iterations = 0
    while not done:
        for cluster in clusters:
            cluster.clear()
        for sample in samples:
            closestcluster = None
            closestdist = None
            for cluster in clusters:
                dist = cluster.dist_to_centroid(sample)
                if closestcluster is None or dist < closestdist:
                    closestcluster = cluster
                    closestdist = dist
            closestcluster.add(sample)
        changed = False
        for cluster in clusters:
            prev = cluster.c
            cluster.update()
            changed = cluster.c != prev
        iterations += 1
        done = not changed or iterations == max_iterations
    return clusters
    
