# importing time and threading 
import time 
import threading 
from pynput.mouse import Button, Controller 
import pyautogui
import numpy as np
from pyscreeze import Box
import easyocr
import PIL
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS # Cuz some version mismaches and ANTIALIAS is depricated

# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
# from json import dumps
# import matplotlib.pyplot as plt

  
# pynput.keyboard is used to watch events of  
# keyboard for start and stop of auto-clicker 
from pynput.keyboard import Listener, KeyCode 
  
  
# four variables are created to  
# control the auto-clicker
start_stop_key = KeyCode(char='i') # go (i)dle 
stop_key = KeyCode(char='k') # (k)ill program


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

# def myRGB2HSV(im):
#     return (mcolors.rgb_to_hsv(im/255.0)*np.array([360.0, 100.0, 100.0])).astype(int)

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

easyocrReader = easyocr.Reader(["en"], gpu=False)

def modBox(box, left=0, top=0, width=0, height=0):
    # Optional parameters describe the change (addative) from the original
    # move = change left/top; scale (from top left corner) = change width/height
    # scale (from center) = change -x/-y of left/top and 2x/2y of width/height
    return Box(left=box.left+left, top=box.top+top, width=box.width+width, height=box.height+height)

def increaseBox(box, increase=3):
    return modBox(box, left=-increase, top=-increase, width=2*increase, height=2*increase)

# threading.Thread is used  
# to control clicks 
class ClickMouse(threading.Thread): 
    
    def __init__(self): 
        super(ClickMouse, self).__init__()
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
        foundRestart = foundIconWhack = foundIconInv = foundIconReinc = False
        # Should the regions be pre-searched? If not, set any of the above to True
        # foundIconInv = True
        
        doRestart = doWhack = doInv = doReinc = True
        # Which parts should be active? Set any of the above to False if you do not want to include them
        # doInv = doRestart = False
        
        startTimeWhack = 0

        logTimeReinc = 10*60 # seconds
        startLogReinc = prevReincLevels = 0
        durMultReinc = 1

        sleepMain = 5
        # sleepOthers = {"Restart":  30, "Inv": 60}
        # countOthers = dict() # Counts of how many "main sleeps" are needed to satisfy individual sleep selections
        # for key, value in sleepOthers.items():
        #     countOthers[key] = value//sleepMain

        # Set regions (used in fast-finding) to default None
        centerRestart = regionIconWhack = regionWhackField = regionIconInv = regionInvRecycle = regionIconReinc = txtReincLevels = None
        
        while self.program_running:
            while self.running:
                # Try finding each thing general location first
                # Restart button
                if not foundRestart:
                    try:
                        # regionRestart = increaseBox(pyautogui.locateOnScreen("ClickToRestart.PNG", confidence=0.8))
                        centerRestart = pyautogui.locateCenterOnScreen("ClickToRestart.PNG", confidence=0.8)
                        r = 10
                        n = 100
                        jitterRestart = np.random.randint(low=-r, high=r+1, size=(n, 2)) + [centerRestart.x, centerRestart.y]
                        foundRestart = True
                        pyautogui.alert(text="Found 'Restart' stuff", title='Restart', button='OK', timeout=1000*2)
                        print("Found 'Restart' stuff:", centerRestart, jitterRestart[:4])
                    except Exception as e: pass
                    if not self.running: break # Include after things that might take awhile within single iteration
                    
                # Whack stuff
                if not foundIconWhack:
                    try:
                        regionIconWhack = increaseBox(pyautogui.locateOnScreen("IconWhack.PNG", confidence=0.8))
                        pyautogui.click(pyautogui.center(regionIconWhack))
                        for _ in range(5): # To wait the screen to open but no more than X attempts
                            try:
                                regionWhackField = increaseBox(pyautogui.locateOnScreen("WhackField.PNG", confidence=0.8))
                                break
                            except Exception as e: time.sleep(0.2)
                        else: raise ValueError("Could not pre-find Whack Field! " + e)
                        pyautogui.alert(text="Found 'Whack' stuff", title='Whack', button='OK', timeout=1000*2)
                        pyautogui.press("esc")
                        foundIconWhack = True
                        print("Found 'Whack' stuff:", regionIconWhack, regionWhackField)
                    except Exception as e: pass #print(e)
                    if not self.running: break # Include after things that might take awhile within single iteration
                
                # Inventory
                if not foundIconInv:
                    try:
                        regionIconInv = increaseBox(pyautogui.locateOnScreen("IconInvEmpty.PNG", confidence=0.9), increase=50)
                        pyautogui.click(pyautogui.center(regionIconInv))
                        for _ in range(5): # To wait the screen to open but no more than X attempts
                            try:
                                regionInvRecycle = increaseBox(pyautogui.locateOnScreen("InvRecycle.PNG", confidence=0.85))
                                break
                            except Exception as e: time.sleep(0.2)
                        else: raise ValueError("Could not pre-find InvRecycle Button! " + e)
                        pyautogui.alert(text="Found 'Inv' stuff", title='Inv', button='OK', timeout=1000*2)
                        pyautogui.press("esc")
                        foundIconInv = True
                        print("Found 'Inv' stuff:", regionIconInv, regionInvRecycle)
                    except Exception as e: pass #print(e)
                    if not self.running: break # Include after things that might take awhile within single iteration
                
                # Reincarnation level speed logging
                if not foundIconReinc:
                    try:
                        regionIconReinc = increaseBox(pyautogui.locateOnScreen("IconReinc.PNG", confidence=0.9))
                        pyautogui.click(pyautogui.center(regionIconReinc))
                        for _ in range(5): # To wait the screen to open but no more than X attempts
                            try:
                                regionReincText = increaseBox(pyautogui.locateOnScreen("ReincLevels.PNG", confidence=0.9))
                                regionReincText = modBox(regionReincText, left=-regionReincText.width, width=regionReincText.width*2)
                                break
                            except Exception as e: time.sleep(0.2)
                        else: raise ValueError("Could not pre-find Reinc Levels Text! " + e)
                        pyautogui.alert(text="Found 'Reinc' stuff", title='Reinc', button='OK', timeout=1000*2)
                        pyautogui.press("esc")
                        foundIconReinc = True
                        print("Found 'Reinc' stuff:", regionIconReinc, regionReincText)
                    except Exception as e: pass #print(e)
                    if not self.running: break # Include after things that might take awhile within single iteration
                
                
                # All locate function variables should be set to none before each clicking loop
                centerIconInv = centerInvRecycle = None
                
                # If Whack potato is ready
                durWhack = time.time() - startTimeWhack
                if doWhack and 5*60 <= durWhack:
                    try:
                        pyautogui.press("esc")
                        pyautogui.click(pyautogui.locateCenterOnScreen("IconWhack.PNG", confidence=0.9, region=regionIconWhack))
                        for _ in range(5): # To wait the screen to open but no more than X attempts
                            try:
                                pyautogui.click(pyautogui.locateOnScreen("WhackField.PNG", confidence=0.9, region=regionWhackField))
                                break
                            except Exception as e: time.sleep(0.2)
                        else:
                            print(2.5, regionWhackField)
                            raise ValueError("Could not find Whack Field! " + e)
                        # Click Whack start key here and wait it to finish its thing and pause it again with keypress
                        pyautogui.press("w")
                        time.sleep( 3 + 60 + 2 ) # start countdown + whacking time + a little delay
                        # Ended
                        # pyautogui.click(centerWhackExit)
                        pyautogui.press("esc")
                        startTimeWhack = time.time()
                    except Exception as e: pass #print("b2", e)
                    if not self.running: break # Include after things that might take awhile within single iteration
                
                # Inventory gets full
                if doInv:
                    try:
                        # Full inventory button is hard to time so try to catch it multiple fast times
                        for _ in range(10):
                            try:
                                centerIconInv = pyautogui.locateCenterOnScreen("IconInvFull.PNG", confidence=0.99, region=regionIconInv) # Even higher confidence?
                                break
                            except Exception as e: time.sleep(0.05)
                        else:
                            # print(centerIconInv)
                            raise ValueError("Didn't find Inventory Icon... " + e)
                        pyautogui.click(centerIconInv)
                        # Maybe should take two images and check that they are not same (a.k.a changing in time / animated)...?
                        
                        for _ in range(5): # To wait the screen to open but no more than X attempts
                            try:
                                centerInvRecycle = pyautogui.locateCenterOnScreen("InvRecycle.PNG", confidence=0.9, region=regionInvRecycle)
                                # if centerInvRecycle is not None: print("Found 'centerInvRecycle':", centerInvRecycle)
                                break
                            except Exception as e: time.sleep(0.2)
                        else:
                            print(3.5, centerInvRecycle)
                            raise ValueError("Could not find InvRecycle Button! " + e)
                        # Double click recycle button
                        pyautogui.click(centerInvRecycle, clicks=2, interval=0.1)
                        pyautogui.press("esc")
                    except Exception as e: pass #print("c2", e)
                    if not self.running: break # Include after things that might take awhile within single iteration
                
                # Reinc logging
                durLogReinc = time.time()-startLogReinc
                if doReinc and logTimeReinc*durMultReinc <= durLogReinc:
                    try:
                        pyautogui.click(pyautogui.locateCenterOnScreen("IconReinc.PNG", confidence=0.9, region=regionIconReinc))
                        for _ in range(5):
                            try:
                                txtReincLevels = pyautogui.locateOnScreen("ReincLevels.PNG", confidence=0.9, region=regionReincText)
                                txtReincLevels = modBox(txtReincLevels, left=-int(txtReincLevels.width*0.5 - 5), width=-int(txtReincLevels.width*0.5))
                                # Take pic at shifted image loc and find text on it
                                txtReincLevels = pyautogui.screenshot(region=(int(txtReincLevels.left),
                                                                            int(txtReincLevels.top),
                                                                            int(txtReincLevels.width),
                                                                            int(txtReincLevels.height))).convert("L")
                                txtReincLevels.save("ReincTempLvl.jpg")
                                txtReincLevels = easyocrReader.readtext(np.asarray(txtReincLevels)) # Text detection beast is here
                                break
                            except Exception as e: time.sleep(0.2)
                        else:
                            print(4.5, txtReincLevels)
                            raise ValueError("Could not find image or failed extracting text! " + e)
                        
                        if txtReincLevels and txtReincLevels[0][2] > 0.4:
                            newReincLevels = int(txtReincLevels[0][1][1:])
                            if newReincLevels != prevReincLevels:
                                print("Last logging period:", round(durLogReinc/60, 2), "min;",
                                    "Interpolated hourly rate:", round((newReincLevels-prevReincLevels)*((60*60)/durLogReinc), 2))
                                prevReincLevels = newReincLevels
                                durMultReinc = 1
                                startLogReinc = time.time()
                            else: durMultReinc += 1
                        
                        pyautogui.press("esc")
                    except Exception as e: pass #print("c2", e)
                    if not self.running: break # Include after things that might take awhile within single iteration
                
                if foundRestart and doRestart:
                    # Pass time by clicking on the restart button location to boost attack speed
                    # This doubles as automatically skipping the round end wait time too
                    startSleep = time.time()
                    while time.time()-startSleep <= sleepMain:
                        for pointRestart in jitterRestart:
                            if time.time()-startSleep > sleepMain:
                                break
                            pyautogui.click(pointRestart[0], pointRestart[1])
                else:
                    # Just wait
                    pyautogui.alert(text=str(sleepMain) + " second break. No clicking...", title='Sleep', button='Skip', timeout=1000*sleepMain)
                    # time.sleep(sleepMain)
                # As a last step, it won't be needing a separate break-check (will be checked right away before starting next iteration)
            
            time.sleep(1) # When program loops emptily then save recources with longer sleep times
  
  
# instance of mouse controller is created
mouse = Controller() 
click_thread = ClickMouse() 
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
