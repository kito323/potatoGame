# importing time and threading 
import time 
import threading 
from pynput.mouse import Button, Controller 
import pyautogui
import numpy as np
import matplotlib.colors as mcolors
# from json import dumps
# import matplotlib.pyplot as plt

  
# pynput.keyboard is used to watch events of  
# keyboard for start and stop of auto-clicker 
from pynput.keyboard import Listener, KeyCode 
  
  
# four variables are created to  
# control the auto-clicker 
delay = 0.02
button = Button.left
start_stop_key = KeyCode(char='w') # (w)hack
stop_key = KeyCode(char='s') # total (s)top


# def extractPixelValues(im, xys):
#     # 'im' is image as (2D (grayscale)) np array
#     # 'xys' is tuple of 2 lists(/arrays) with interested pixel x and y values; [[x1,x2,...], [y1,y2,...]]
#     pixelValues = []
#     for y in xys[1]:
#         pixelValues.append([])
#         for x in xys[0]:
#             pixelValues[y].append(im[y, x])
#     pixelValues = np.array(pixelValues)
#     return pixelValues

def myRGB2HSV(im):
    return (mcolors.rgb_to_hsv(im/255.0)*np.array([360.0, 100.0, 100.0])).astype(int)

# def visualize_colors(color_list):
#     num_colors = len(color_list)
#     fig, ax = plt.subplots(1, 1, figsize=(10, num_colors/4))  # Adjust figsize as needed

#     for i, color in enumerate(color_list):
#         ax.axhspan(i, i+1, color=color)

#     ax.set_yticks(range(num_colors))
#     ax.set_yticklabels(color_list)
#     ax.set_title('Color Visualization')
#     ax.grid(False)
#     ax.set_xticks([])  # No x-axis ticks

#     plt.show()


# threading.Thread is used  
# to control clicks 
class ClickMouse(threading.Thread): 
    
  # delay and button is passed in class  
  # to check execution of auto-clicker 
    def __init__(self, delay, button): 
        super(ClickMouse, self).__init__() 
        self.delay = delay 
        self.button = button 
        self.running = False
        self.program_running = True
  
    def start_clicking(self): 
        self.running = True
  
    def stop_clicking(self): 
        self.running = False
  
    def exit(self): 
        self.stop_clicking() 
        self.program_running = False
  
    # method to check and run loop until  
    # it is true another loop will check  
    # if it is set to true or not,  
    # for mouse click it set to button  
    # and delay. 
    def run(self):
        while self.program_running:
            foundImage = False
            try:
                # print(pyautogui.size())
                fieldRegion = pyautogui.locateOnScreen("WhackField.PNG", confidence=0.8)
                foundImage = True
                fieldRegion = (int(fieldRegion.left), int(fieldRegion.top), int(fieldRegion.width), int(fieldRegion.height))
                field = pyautogui.screenshot(region=fieldRegion)
                field = np.array(field, dtype=int)
                xCount = 5
                yCount = 3
                xStep = fieldRegion[2]/xCount
                yStep = fieldRegion[3]/yCount
                xs = np.arange(start=int(xStep/2), step=int(xStep), stop=fieldRegion[2])
                ys = np.arange(start=int(2*yStep/3), step=int(yStep), stop=fieldRegion[3]) # y is not centered
                xsGlob = xs + fieldRegion[0]
                ysGlob = ys + fieldRegion[1]
                maxBaseValue = 20
                # thresh = 9
                colClicks = []
                prevSpots = set()
                # # Find out the base HSVs
                # basePixels = myRGB2HSV(field[np.ix_((ys-2*yStep/21).astype(int), xs)]) # V(alue) should always be 0 or close to it as we are aiming at the central black dot
                # print(basePixels[:, :, 2].max())
            except Exception as e:
                if foundImage: # But still error then print it
                    print(1, e)
                time.sleep(0.5)
                continue
            if self.running:
                try:
                    startX, startY = pyautogui.locateCenterOnScreen("WhackStart.PNG", confidence=0.8)
                    pyautogui.click(startX, startY)
                    time.sleep(3.1)
                    startTime = time.time()
                    while self.running:
                        if (time.time()-startTime) > 60: # Automatically stops clicking state
                            self.stop_clicking()
                        frame = np.array(pyautogui.screenshot(region=fieldRegion), dtype=int)
                        framePixels = myRGB2HSV(frame[np.ix_(ys, xs)])
                        diffPixels = framePixels[:, :, 2] > maxBaseValue
                        if (diffPixels).any():
                            newSpots = {tuple(row) for row in np.transpose(diffPixels.nonzero())}
                            changeSpots = list(newSpots - prevSpots)
                            if len(changeSpots) == 1 and len(newSpots) == 1: # Mby '> 0'?
                                changeSpot = changeSpots[0] # x and y are reversed btw
                                framePixel = framePixels[changeSpot[0], changeSpot[1]]
                                if (framePixel[0] >= 31) and (framePixel[0] <= 46):
                                    mouse.position = (xsGlob[changeSpot[1]], ysGlob[changeSpot[0]])
                                    # print(framePixel, newSpots)
                                    mouse.click(self.button)
                                    # time.sleep(self.delay)
                                else:
                                    time.sleep(0.2)
                                colClicks.append(framePixel)
                                prevSpots = newSpots
                except Exception as e:
                    print(2, e)
                
                potatoTypes = ["Regular", "Yellow", "Green", "?"]
                typeClicks = {key: [] for key in potatoTypes}
                for col in colClicks:
                    if (col[0] >= 31) and (col[0] <= 36): # 33 or 34 H(ue) is roughly for the brown potato
                        typeClicks["Regular"].append(col)
                    elif (col[0] >= 37) and (col[0] <= 46): # Yellow one usually around 43 or 44 but sometimes a lot lower (40/39 or so)
                        typeClicks["Yellow"].append(col)
                    elif (col[0] >= 82) and (col[0] <= 87): # Green one usually around 84 or 85
                        typeClicks["Green"].append(col)
                    else: # le wat is that
                        typeClicks["?"].append(col)
                numClicks = np.array([len(typeClicks[typ]) for typ in potatoTypes])
                numClicksSum = numClicks.sum()
                print(potatoTypes)
                print(numClicks)
                print((100*numClicks/numClicksSum).round(decimals=2))
                print(numClicksSum)
                # print(dumps(numClicks, indent=2))
                # detectedHSVs = [col for typ in potatoTypes for col in numClicks[typ]["pixels"]+[np.array([0,0,0])]]
                # detectedRGBs = mcolors.rgb_to_hsv(detectedHSVs/np.array([360.0, 100.0, 100.0]))
                # visualize_colors(detectedRGBs) # Matplotlib fails on non-main threads...
            time.sleep(1) 
  
  
# instance of mouse controller is created
mouse = Controller() 
click_thread = ClickMouse(delay, button) 
click_thread.start() 
  
  
# on_press method takes  
# key as argument 
def on_press(key): 
    
  # start_stop_key will stop clicking  
  # if running flag is set to true 
    if key == start_stop_key: 
        if click_thread.running: 
            click_thread.stop_clicking()
        else: 
            click_thread.start_clicking() 
              
    # here exit method is called and when  
    # key is pressed it terminates auto clicker 
    elif key == stop_key: 
        click_thread.exit() 
        listener.stop() 
  
  
with Listener(on_press=on_press) as listener: 
    listener.join()
