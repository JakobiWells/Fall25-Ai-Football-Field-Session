Experimentation folder is for testing and unofficial work.

To install dependecies
pip install -r requirements.txt





Canny is a 4 step process to detect edges in an image.
1. Gaussian blue is added to the image to reduce noise.
2. A brightness gradient is calculated for each pixel in the image.
3. Edges should be thin edges, thus find the local maxima(sharpest part of the gradient) and discard the rest.
4. Find pixels with high edges which are definitely edges. Weak pixels are considered an edge if they are connected to strong edges. 


Hough Transfrom is a clever way to identify lines in an image. Lines in cartesian coordinates are represented by y = mx + b. 
This is inconvenient for computers because vertical lines have infinite slope. As such, it is smarter to represent the lines in polar.

The normal form of a polar line is p = x cos theta +  y sin theta. 
Where p is the perpendicular distance from the line to the origin and theta is the angle of that perpendicular line from theta = 0.

Each (x,y) point in the image corresponds to all lines that go through it. As theta goes from 0 to 180 
a circle of lines that pass through x,y are generated.

1.	Image space (x,y):
	•	A pixel at (100,50) is just a point.
	•	A line is a straight segment drawn through it.
2.	Hough space (ρ,θ):
	•	That single pixel at (100,50) becomes a sinusoidal curve.
	•	Every possible line through that pixel is now represented as one point on that curve.

As we continue checking more pixels in the image, we will end up with more sinusoidal curves in hough space. 
Intersections between these curves indicate lines in the image. Each intersection is essentially a vote, 
we can fine tune thresholds for the number of votes to identify lines.