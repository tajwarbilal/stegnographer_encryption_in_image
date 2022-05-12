import os
import pathlib
# PIL module is used to extract
# pixels of image and modify it
from PIL import Image
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

count = 0

PARENT_PATH = str(pathlib.Path(__file__).parent.resolve())
UPLOAD_FOLDER = PARENT_PATH
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'hellowehavesomedata'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Python program implementing Image Steganography

# Convert encoding data into 8-bit binary
# form using ASCII value of characters
def genData(data):
    # list of binary codes
    # of given data
    newd = []

    for i in data:
        newd.append(format(ord(i), '08b'))
    return newd


# Pixels are modified according to the
# 8-bit binary data and finally returned
def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):

        # Extracting 3 pixels at a time
        pix = [value for value in imdata.__next__()[:3] +
               imdata.__next__()[:3] +
               imdata.__next__()[:3]]

        # Pixel value should be made
        # odd for 1 and even for 0
        for j in range(0, 8):
            if (datalist[i][j] == '0' and pix[j] % 2 != 0):
                pix[j] -= 1

            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                if (pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1
            # pix[j] -= 1

        # Eighth pixel of every set tells
        # whether to stop ot read further.
        # 0 means keep reading; 1 means thec
        # message is over.
        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if (pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1

        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]


def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), data):

        # Putting modified pixels in the new image
        newimg.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1


# Encode data into image
def encode(filename, message):
    image = Image.open(filename, 'r')

    if len(message) == 0:
        raise ValueError('Data is empty')

    newimg = image.copy()
    encode_enc(newimg, message)
    global count
    count = count + 1
    new_img_name = str(count) + filename
    newimg.save(new_img_name, str(new_img_name.split(".")[1].upper()))


# Decode the data in the image
def decode(filename):
    img = filename
    image = Image.open(img, 'r')

    data = ''
    imgdata = iter(image.getdata())

    while (True):
        pixels = [value for value in imgdata.__next__()[:3] +
                  imgdata.__next__()[:3] +
                  imgdata.__next__()[:3]]

        # string of binary data
        binstr = ''

        for i in pixels[:8]:
            if (i % 2 == 0):
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            return data


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        filefirst = request.files['filefirst']
        filefirst.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filefirst.filename)))

        inputtohide = request.form.get('inputtohide')
        encode(filefirst.filename, inputtohide)

    return render_template('index.html')


@app.route('/revealtext', methods=['POST', 'GET'])
def revealtext():
    if request.method == 'POST':
        try:
            filesecond = request.files['filesecond']
            #filesecond.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filesecond.filename)))
            fetch_data = decode(secure_filename(filesecond.filename))
        except:
            print('didnt get anyfile')
    return render_template('index.html', fetch_data=fetch_data)


if __name__ == '__main__':
    app.run(debug=True)
