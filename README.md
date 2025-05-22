# lego-plotter-project-v2
A plotter robot built with Lego that draws cartoonized faces. If you want to draw things other than faces, you can see the [previous version of the project](https://github.com/liugetu/lego-plotter-project).

[Build instructions (PDF / 44MB)](https://jander.me.uk/LEGO/resources/Plott3r.pdf)

Based on a work at http://jander.me.uk/LEGO/plott3r.html.

[Set up to use Python with the Lego brick](https://education.lego.com/en-us/product-resources/mindstorms-ev3/teacher-resources/python-for-ev3/)

# Cartoon Yourself API
I used the [Cartoon Yourself API](https://rapidapi.com/ailabapi-ailabapi-default/api/cartoon-yourself) to transform personal photos into cartoon images. It offers a free plan.

Remember to **enter your API key** in `main.py`. There, if you wish, you can also change the drawing style where it says `"type"`.

# Instructions
First, take a photo of yourself (or you can also use an existing photo). Then, execute 

<pre><code>python3 main.py</code></pre>

You will have to select a photo in the file browser. It will generate a file `coordenadas.txt` containing the drawing coordinates, and a window will pop up where you can preview what will be drawn (it will be deformed because it doesn't have the same aspect ratio as the paper, and mirrored):

To send the files to the robot (change the IP address to yours):
<pre><code>scp exec4.py coordenadas.txt stop.py robot@169.254.206.221:/home/robot/</code></pre>

The default password to access the robot is `maker`.

To enter the robot and start drawing (I recommend using a different terminal):
<pre><code>ssh robot@169.254.206.221
python3 exec4.py</code></pre>

To exit this mode, just enter `exit`.

In case it doesn't work well and can't stop, or you want to level up the pen:
<pre><code></code>python3 stop.py</code></pre>

Note: a white paper should be used, otherwise, the color sensor might not work well.
