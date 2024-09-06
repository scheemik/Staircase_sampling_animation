"""
Author: Mikhail Schee
Creates a gif of a set of png images in the stated directory.

Script created: 2019/03/19, Mikhail Schee
Last updated: 2022/01/04, Mikhail Schee
"""

"""
Using imageio
https://imageio.readthedocs.io/en/latest/installation.html
install using:
    conda install -c conda-forge imageio
OR
    pip install imageio
Skeleton script from
https://stackoverflow.com/questions/41228209/making-gif-from-images-using-imageio-in-python
"""

import os
import imageio
from PIL import Image
dark_mode = False

gif_file = 'ITP8-1301_v_ITP1-1259.gif'
png_dir = 'frames'
print('Saving gif to', gif_file)

# In order to keep the transparency of the png images in the gif
# found this solution from:
# https://stackoverflow.com/questions/46850318/transparent-background-in-gif-using-python-imageio
def generate_alpha_frame(file_path):
    im = Image.open(file_path)
    alpha = im.getchannel('A')
    # Convert the image into P mode but only use 255 colors in the palette out of 256
    im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
    # print(im.getcolors())
    # exit(0)
    if dark_mode:
        # Set all pixel values below 128 to 255 , and the rest to 0
        mask = Image.eval(alpha, lambda a: 255 if a <=10 else 0)
    else:
        # Set all pixel values below 128 to 255 , and the rest to 0
        mask = Image.eval(alpha, lambda a: 255 if a <=20 else 0)
    # Paste the color of index 255 and use alpha as a mask
    im.paste(255, mask)
    # The transparency index is 255
    im.info['transparency'] = 255
    return im

images = []
# need to sort because os.listdir returns a list of arbitrary order
for file_name in sorted(os.listdir(png_dir)):
    if file_name.endswith('.png'):
        file_path = os.path.join(png_dir, file_name)
        images.append(generate_alpha_frame(file_path))
images[0].save(gif_file, save_all=True, append_images=images[1:], duration=100, loop=0, optimize=False, disposal=2)
exit(0)

# To set the frames per second
fps = 12
frame_duration = 1.0 / fps

images = []
# need to sort because os.listdir returns a list of arbitrary order
for file_name in sorted(os.listdir(png_dir)):
    if file_name.endswith('.png'):
        file_path = os.path.join(png_dir, file_name)
        images.append(imageio.imread(file_path))
imageio.mimsave(gif_file, images, duration=frame_duration)
