import tkinter as tk
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageOps, ImageFilter, ImageEnhance, ImageTk
import time
import cv2

frame_side=800
cuts, reps = 20, 8

blankimg = Image.new('RGB', (frame_side, frame_side), color=0)
root = tk.Tk()
label = tk.Label(root)
label.pack()
img = blankimg.copy()

colors = [(255,250,240), (240,248,255), (248,248,255), (240,255,240), 
          (255,255,240), (240,255,255), (255,250,250)]
flash_colors = colors



l = len(colors)
f_l = len(flash_colors)
i = 0

#cropimg = ImageOps.crop(img, border=size*.05)

cut, step = 0, 0
while True:
    i += 1
    if step == 0:
        cut = (cut + 1) % (cuts * reps)
        rand = np.random.RandomState(cut % cuts + 100)
        
        rotation = np.exp(rand.uniform(0, np.pi) * 2j)
        ang_shift = np.array([rotation * 1j]).view(float)
        
        offset = rand.uniform(-0.1, 0.1)
        
        random_line = np.cumsum(rand.uniform(-0.0015, 0.0015, 2*frame_side))
        smooth_line = np.convolve(random_line, np.ones(rand.randint(5, 20))/10,'same')
        centered_line = (smooth_line - smooth_line[len(smooth_line) // 2])
        offset_line = centered_line + offset
        complex_line = offset_line * 1j + np.linspace(-1, 1, len(offset_line))
        maskbox =  [1 -2j, -1 -2j]
        masked_line = np.hstack((maskbox, complex_line))
        rotated_line = masked_line * rotation
        listed_line = list(((rotated_line.view(float) + 0.5) * frame_side).astype(int))
        
        img_line = blankimg.copy()
        flash_line = blankimg.copy()
        
        color = colors[rand.randint(l)]
        flash_color = flash_colors[rand.randint(f_l)]
        
        ImageDraw.Draw(img_line).line(listed_line, fill = color, width=4)
        ImageDraw.Draw(flash_line).line(listed_line, fill = flash_color, width=2)
        
        mask1 = img_line.copy()
        ImageDraw.Draw(mask1).polygon(listed_line, fill = color)
        mask2 = ImageChops.lighter(img_line, ImageChops.invert(mask1))

        img = ImageChops.lighter(img, img_line)
        
        split1 = ImageChops.darker(img, mask1)
        split2 = ImageChops.darker(img, mask2)
        
        splitsize = rand.randint(10, 20)
        lineblur = flash_line.filter(ImageFilter.GaussianBlur(radius=10))

    shift = 2 + splitsize * step / 10 
    splitstep = (ang_shift*shift).astype(int)

    shifted1 =  ImageChops.offset(split1, *-(splitstep))
    shifted2 =  ImageChops.offset(split2, *(splitstep))
    img = ImageChops.lighter(shifted1, shifted2)
    
    flash = ImageEnhance.Contrast(lineblur).enhance(10 - 2 * step)
    flashimg = ImageChops.lighter(img, flash)
    cropimg = ImageOps.crop(flashimg, border=frame_side*.05)
    
    #if i%2 == 0:
    #    cropimg = ImageChops.invert(cropimg)
    
    tkimg = ImageTk.PhotoImage(cropimg)
    label.config(image=tkimg)
    step = (step + 1) % 8

    # just crash out when window closed, terrible I know
    root.update()
    time.sleep(0.04)