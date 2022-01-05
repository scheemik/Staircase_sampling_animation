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

gif_file = 'ITP8-1301_v_ITP1-1259.gif'
png_dir = 'frames'
print('Saving gif to', gif_file)


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
