
# %%
import glob
import cv2
import os.path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
os.system('clear')


# %%
Well = 'T2'
cores_per_image = 6
uvFiles = glob.glob('./Photos/*.jpg')
filedos = []

for l in range(len(uvFiles)):
    filedos.append(int(uvFiles[l][9:13]))
indices = [index for index, value in sorted(enumerate(filedos), reverse=False, key=lambda x: x[1]) if value > 1]
uvFiles = [uvFiles[i] for i in indices]


a = []
b = []
DEPTH = []
GRAY = []
PHOTO = []
dos = []
dns = []
doo = 0
dnn = 1
lg =0
ImgStack = []


# %%
def oneventlbuttondown(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        a.append(x)
        b.append(y)
        cv2.circle(img, (x, y), 10, (0, 0, 255), thickness=-1)
        #        cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness=1)
        cv2.imshow("image", img)
core_length = 3


for k in range(len(uvFiles)): #Loop through various files containing images
    vc = []  #Reset stacked photo when switching from one photo to the other one


    fname = uvFiles[k][9:25]
    # Picture path
    img = cv2.imread(uvFiles[k])
    do = int(fname[0:4])
    dn = int(fname[5:9])    

    dos.append(do)
    dns.append(dn)


    for i in range(cores_per_image):
        if k == 0 and i == 0:
            print(k, i)

            cv2.namedWindow("image", cv2.WINDOW_NORMAL)
            # cv2.resizeWindow("output", 400, 300)
            cv2.setMouseCallback("image", oneventlbuttondown)
            cv2.imshow("image", img)
            print(
                'Click 1) left upper corner 2) right lower corner in leftmost core and 3) leftupper corner in second core')
            cv2.waitKey(0)
            y = b[0];
            x = a[0];
            dy = b[1] - b[0];
            dx = a[1] - a[0]
            gap = a[2] - a[1]

   

        if i == 0:
            x = a[0]; y = b[0];
        if i == 3:
            midgap = gap * 4
        else:
            midgap = 0
        if i > 0: 
            x = x + (dx + gap) + midgap
            



        crop_img = img[y:y + dy, x:x + dx]
        
        if i == 0:# and k == 0:
            vc = crop_img
        else:
            print("LINE:", k, i)
            print((vc.size), type(vc))
            print((crop_img.size), type(crop_img))

            vc = cv2.vconcat([vc, crop_img])
            
        vc_gray = cv2.cvtColor(vc, cv2.COLOR_BGR2GRAY)   



        crop_name = str(int(fname[0:4]) + (core_length * i)) + ".jpg"
        
        # if i == 0 and k == 0:
        #     ImgStack = pd.DataFrame(data=vc_gray)
        # else:
        #     ImgStack = ImgStack.append(pd.DataFrame(data=vc_gray))
        
    if k == 0:
        ImgStack = vc
    else:
        ImgStack = np.concatenate((ImgStack, vc), axis =0)



    
    path = os.path.join(os.path.relpath('Cropped', start=os.curdir), crop_name)
    cv2.imwrite(path, crop_img)

    concat_name = fname[0:4] + "-" + fname[5:9] + ".jpg"
    path = os.path.join(os.path.relpath('Cropped', start=os.curdir), concat_name)
    cv2.imwrite(path, vc)
    p = vc.shape



    if k == len(uvFiles)-1:
        doo = min(dos)
        dnn = max(dns)
        
         
#PROBLEM:   Am adding and stacking images at the same time!! :enght is growing

    img_log = np.average(vc_gray[:, 20:100], axis=1)
    print("Img Log LEnght in this subsection is: ", k, ", ", len(img_log))
    depths = np.arange(do, dn, (dn - do) / len(img_log))
   
    photo_number = np.full_like(depths, 1)*(k+1)

    DEPTH.extend(depths.tolist())
    GRAY.extend(img_log.tolist())
    PHOTO.extend(photo_number.tolist())



# %%

d = {'DEPTH': DEPTH, 'GRAY': GRAY}
sub = pd.DataFrame(np.array(DEPTH).T, columns = ['DEPTH'])
sub['GRAY'] = np.array(GRAY).T
sub['PHOTO'] = np.array(PHOTO).T
sub.to_excel("Processed_Images.xlsx",
              sheet_name=Well) 
 
# %%

dplot_o = 3675
dplot_n = 3745

istr = int(ImgStack.shape[0]*(dplot_o - doo)/(dnn-doo))
iend = int(ImgStack.shape[0]*(dplot_n - doo)/(dnn-doo))

print(ImgStack.shape)
plt.figure()
plt.subplot2grid((1, 10), (0, 0), colspan=3)
plt.plot(sub['GRAY'], sub['DEPTH'], 'green', linewidth=1);
plt.axis([90, 200, dplot_o, dplot_n]);
plt.gca().invert_yaxis();
#plt.gca().invert_xaxis()

plt.subplot2grid((1, 10), (0, 3), colspan=7)
plt.imshow(ImgStack[istr:iend,80:120], aspect='auto', origin='upper', extent=[0,1,dplot_n,dplot_o], cmap='gray');
plt.axis([0, 1, dplot_o, dplot_n]);
plt.gca().invert_yaxis()

plt.colorbar()
#plt.gca().invert_yaxis();
p_50 = np.percentile(sub['DEPTH'], 50)
plt.show()


# %%
