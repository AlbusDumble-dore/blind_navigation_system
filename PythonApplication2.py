import cv2
import numpy as np
from matplotlib import pyplot as plt

img1 = cv2.imread("left.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("right.jpg", cv2.IMREAD_GRAYSCALE)
 
print(cv2.__version__)

#sift = cv2.xfeatures2d.SURF_create()
#orb = cv2.ORB_create()
# find the keypoints and descriptors with SIFT
#kp1, des1 = orb.detectAndCompute(img1,None)
#kp2, des2 = orb.detectAndCompute(img2,None)

# ORB Detector
orb = cv2.ORB_create()
kp1, des1 = orb.detectAndCompute(img1, None)
kp2, des2 = orb.detectAndCompute(img2, None)


#des1.convertTo(des1, CV_32F); 
#des2.convertTo(des2, CV_32F); 

# FLANN parameters
FLANN_INDEX_KDTREE = 0
FLANN_INDEX_LSH = 6
#index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
index_params= dict(algorithm = FLANN_INDEX_LSH,
                   table_number = 6, # 12
                   key_size = 12,     # 20
                   multi_probe_level = 1) #2
search_params = dict(checks=50)

flann = cv2.FlannBasedMatcher(index_params,search_params)
matches = flann.knnMatch(des1,des2,k=2)


# Brute Force Matching
#bf = cv2.BFMatcher()
#matches = bf.knnMatch(des1, des2, k=2)
#matches = sorted(matches, key = lambda x:x.distance)
good = []
pts1 = []
pts2 = []

# ratio test as per Lowe's paper

for m,n in matches:
   if m.distance < 1.8*n.distance:
      good.append(m)
      pts2.append(kp2[m.trainIdx].pt)
      pts1.append(kp1[m.queryIdx].pt)

#for i,(m,n) in enumerate(matches):
 #   if m.distance < 0.8*n.distance:
      #  good.append(m)
       # pts2.append(kp2[m.trainIdx].pt)
        #pts1.append(kp1[m.queryIdx].pt)


print(pts1)        

pts1 = np.int32(pts1)
pts2 = np.int32(pts2)


F, mask = cv2.findFundamentalMat(pts1,pts2,cv2.FM_LMEDS)

# We select only inlier points
pts1 = pts1[mask.ravel()==1]
pts2 = pts2[mask.ravel()==1]

def drawlines(img1,img2,lines,pts1,pts2):
    ''' img1 - image on which we draw the epilines for the points in img2
        lines - corresponding epilines '''
    r,c = img1.shape
    img1 = cv2.cvtColor(img1,cv2.COLOR_GRAY2BGR)
    img2 = cv2.cvtColor(img2,cv2.COLOR_GRAY2BGR)
    for r,pt1,pt2 in zip(lines,pts1,pts2):
        color = tuple(np.random.randint(0,255,3).tolist())
        x0,y0 = map(int, [0, -r[2]/r[1] ])
        x1,y1 = map(int, [c, -(r[2]+r[0]*c)/r[1] ])
        img1 = cv2.line(img1, (x0,y0), (x1,y1), color,1)
        img1 = cv2.circle(img1,tuple(pt1),5,color,-1)
        img2 = cv2.circle(img2,tuple(pt2),5,color,-1)
    return img1,img2
# Find epilines corresponding to points in right image (second image) and
# drawing its lines on left image
lines1 = cv2.computeCorrespondEpilines(pts2.reshape(-1,1,2), 2,F)
lines1 = lines1.reshape(-1,3)
img5,img6 = drawlines(img1,img2,lines1,pts1,pts2)

# Find epilines corresponding to points in left image (first image) and
# drawing its lines on right image
lines2 = cv2.computeCorrespondEpilines(pts1.reshape(-1,1,2), 1,F)
lines2 = lines2.reshape(-1,3)
img3,img4 = drawlines(img2,img1,lines2,pts2,pts1)

plt.subplot(121),plt.imshow(img5)
plt.subplot(122),plt.imshow(img3)
plt.show()