import os
import cv2
import sys
import PIL
import html
import os
import re
import six
import math
import pytesseract
import numpy as np
from models.unet import *

from keras import backend as K
import matplotlib.pyplot as plt
from multiprocessing import Pool
from google.cloud import translate
from keras.models import load_model
from keras.preprocessing import image

from PIL import Image, ImageFont, ImageDraw
from models.keras_ssd300 import ssd_300
from keras_loss_function.keras_ssd_loss import SSDLoss
from keras_layers.keras_layer_AnchorBoxes import AnchorBoxes
from keras_layers.keras_layer_DecodeDetections import DecodeDetections
from keras_layers.keras_layer_L2Normalization import L2Normalization
from ssd_encoder_decoder.ssd_output_decoder import decode_detections, \
    decode_detections_fast

# Parameter Setting
img_height = 300  # Height of the model input images
img_width = 300  # Width of the model input images
n_classes = 1  # Number of positive classes, e.g. 20 for Pascal VOC, 80 for
# MS COCO
normalize_coords = True


# Load Models
def model_load(model_path):
    model_path = model_path

    # We need to create an SSDLoss object in order to pass that to the model
    #  loader.
    ssd_loss = SSDLoss(neg_pos_ratio=3, alpha=0.8)

    K.clear_session()  # Clear previous models from memory.

    model = load_model(os.path.join(model_path, 'ssd300_all.h5'),
                       custom_objects={'AnchorBoxes': AnchorBoxes,
                                       'L2Normalization': L2Normalization,
                                       'compute_loss': ssd_loss.compute_loss})

    model2 = unet()
    model2.load_weights(os.path.join(model_path, "unet_8.hdf5"))
    return model, model2


def trans_img(img_path, img_size=(img_height, img_height)):
    orig_images = []  # Store the images here.
    input_images = []  # Store resized versions of the images here.
    # We'll only load one image in this example.
    # img_load = imread(img_path)
    img_load = Image.open(img_path).convert("RGB")

    orig_images.append(np.array(img_load))
    img = image.load_img(img_path, target_size=(img_height, img_width))
    img = image.img_to_array(img)
    input_images.append(img)
    input_images = np.array(input_images)
    return img_load, orig_images, input_images


def text_detect(orig_images, input_images, model):
    y_pred = model.predict(input_images)

    # 3: Decode the raw predictions in `y_pred`.

    y_pred_decoded = decode_detections(y_pred,
                                       confidence_thresh=0.17,
                                       iou_threshold=0.01,
                                       top_k=200,
                                       normalize_coords=normalize_coords,
                                       img_height=img_height,
                                       img_width=img_width)

    # 4: Convert the predictions for the original image + manual offset.
    # decode
    y_pred_decoded_inv = y_pred_decoded.copy()
    y_pred_decoded_inv[0][:, 2] = y_pred_decoded[0][:, 2] * \
                                  orig_images[0].shape[1] / img_width - 3
    y_pred_decoded_inv[0][:, 3] = y_pred_decoded[0][:, 3] * \
                                  orig_images[0].shape[0] / img_height - 3
    y_pred_decoded_inv[0][:, 4] = y_pred_decoded[0][:, 4] * \
                                  orig_images[0].shape[1] / img_width + 28
    y_pred_decoded_inv[0][:, 5] = y_pred_decoded[0][:, 5] * \
                                  orig_images[0].shape[0] / img_height + 28
    text_box = []
    for y_pred_decode in y_pred_decoded_inv:
        text_box.append(y_pred_decode[:, 2:].astype(np.int32))

    return text_box


#######################SEGMENTATION##############################
def mask_gen(img_load, model2):
    img_L = img_load.convert("L")
    img_array = np.array(img_L)
    sh = img_array.shape
    # print(sh)
    img_rz = trans.resize(img_array, (256, 256, 1))
    img_rz = np.expand_dims(img_rz, axis=0)
    pred = model2.predict(img_rz) > 0.2
    mask = trans.resize(pred[0][:, :, 0], sh)
    return mask


#######################OCR+Translate##############################
# Imports the Google Cloud client library

class TransGT(object):
    def __init__(self, text, source_language='ja'):
        self.text = text
        self.source_language = source_language

    def translator(self):
        translated = translate.Client().translate(
            self.text,
            source_language=self.source_language,
            model=translate.NMT,
            format_='text'
        )
        result = []
        for tran in translated:
            result.append(tran['translatedText'])
        return result


def crop_words(img, boxes):
    """
    make sure that the vertices of all boxes are inside the image
    """
    words = []
    for j in range(len(boxes)):
        h, w = img.shape[:2]
        if boxes.shape[1] == 4:
            # box case
            box = boxes[j]
            xmin, ymin, xmax, ymax = box
            if xmin == xmax:
                xmax += 5
            if ymin == ymax:
                ymax += 5
            word = img[ymin:ymax, xmin:xmax, :]
        words.append(word)
    return words


def ocr(image):
    r = re.compile(r'[-A-Za-z0-9(){}\[\]\【】/|~《》』\\<ぇー_]+')
    r2 = re.compile(r'[二p:"=]+')
    #     ret,image = cv2.threshold(image,117,250,cv2.THRESH_BINARY)
    t = pytesseract.image_to_string(image, lang='jpn_vbest',
                                    config="--psm 12 --oem 1")
    t = r.sub(' ', t).split()
    t = "".join(t)
    t = r2.sub('!!', t)
    return t


def translate_img(image_seg, text_box):
    ocr_page_tran = []
    text_box_clean = []

    cropped = crop_words(image_seg, text_box[0])
    cropped_filter = []
    mask_text = []
    for j in range(len(cropped)):
        # h, w, _ = cropped[j].shape
        # if h < w / 1.5:
        #     continue
        cropped_filter.append(cropped[j])
        mask_text.append(j)

    text_box_clean.append(text_box[0][mask_text])

    pool1 = Pool(36)
    text_ocr = pool1.map(ocr, cropped_filter)
    pool1.close()
    pool1.join()

    eng = TransGT(text_ocr)
    text_ocr_tran = eng.translator()
    ocr_page_tran.append(np.array(text_ocr_tran))

    return ocr_page_tran, text_box_clean


# Word Level fill in
def text_fill(image, axis, text, mask, background_color):
    # Turn the image into array
    im_array = np.array(image)
    im_array[mask == 1] = background_color
    masked_im = Image.fromarray(im_array)

    # Set default font_size to 12
    font_size = 15
    main_path = 'product-analytics-group7/server/'
    font = ImageFont.truetype(main_path + "mangat.ttf", font_size)
    space = 5
    # Return im_array

    for coord, t in zip(axis[0], text):

        # Set default text color to white
        text_color = 0
        # Set default background to white
        bg = background_color
        # Calculate the width and height of text bubbles
        width = coord[2] - coord[0]
        height = coord[3] - coord[1]

        if im_array[coord[1]:coord[3], coord[0]:coord[2]].mean() < 100:
            bg = background_color
            text_color = 0

        # Create a new image size equal to the text box
        img = Image.new("1", (width, height), color=bg)
        draw = ImageDraw.Draw(img)
        # Set default coordinates for drawing to 0
        v_coord = 0
        h_coord = 0
        words = t.split()
        #         draw.text((v_coord, h_coord), words[0], text_color,
        # font=font)
        if not words:
            words = ['....']
        #         print(words)
        lst_word_len, word_height = font.getsize(words[0])

        for i, word in enumerate(words[1:]):
            font_width, font_height = font.getsize(word)
            #             print(width,h_coord,v_coord,font_width,space)
            #             print((width-h_coord)<(font_width+space))
            if (width - (h_coord + (lst_word_len + space))) > (
                    font_width + space):
                h_coord += (lst_word_len + space)
                draw.text((h_coord, v_coord), word, text_color, font=font)
                lst_word_len, word_height = font.getsize(word)
            else:
                h_coord = 0
                v_coord += font_size
                draw.text((h_coord, v_coord), word, text_color, font=font)
                lst_word_len, _ = font.getsize(word)

        gap = (height - v_coord) / 2 - word_height
        #         img = Image.new("1", (width, height), color=bg)
        draw = ImageDraw.Draw(masked_im)
        # Set default coordinates for drawing to 0
        v_coord = gap
        h_coord = 0
        #         print(gap)
        font_size = 15
        font = ImageFont.truetype(main_path + "mangat.ttf", font_size)
        if gap > 40:
            font_size = 18
            if image.size[0]>3000:
                font_size = 27
            font = ImageFont.truetype(main_path + "mangat.ttf", font_size)
        words = t.split()
        if not words:
            words = ['....']
        draw.text((h_coord + coord[0], v_coord + coord[1]), words[0],
                  text_color, font=font)
        lst_word_len, _ = font.getsize(words[0])

        for i, word in enumerate(words[1:]):
            font_width, font_height = font.getsize(word)
            if (width - (h_coord + (lst_word_len + space))) > (
                    font_width + space):
                h_coord += (lst_word_len + space)
                draw.text((h_coord + coord[0], v_coord + coord[1]), word,
                          text_color, font=font)
                lst_word_len, _ = font.getsize(word)
            else:
                h_coord = 0
                v_coord += font_size
                draw.text((h_coord + coord[0], v_coord + coord[1]), word,
                          text_color, font=font)
                lst_word_len, _ = font.getsize(word)

    return masked_im


def water_mask(image):
    # create a new image for the watermark
    watermark = Image.new("RGB", image.size)
    # create a canvas so we can draw
    waterdraw = ImageDraw.ImageDraw(watermark, "RGB")
    # basic info
    width, height = image.size
    # auto-adjust fontsize
    if width < 400:
        fontsize = 32
    elif width < 600:
        fontsize = 48
    elif width < 800:
        fontsize = 64
    elif width < 1000:
        fontsize = 80
    elif width < 1200:
        fontsize = 100
    elif width < 1400:
        fontsize = 128
    elif width < 1800:
        fontsize = 156
    elif width < 2200:
        fontsize = 192
    elif width < 2600:
        fontsize = 256
    elif width < 3100:
        fontsize = 300
    else:
        fontsize=300

    # define the text
    font_path = "product-analytics-group7/server/mangat.ttf"
    font = ImageFont.truetype(font_path, int(fontsize * 1.5))
    text = "D  E  M  O"
    text_w, text_h = font.getsize(text)
    # write on the canvas
    waterdraw.text([(width - text_w) / 2, (height - text_h) / 2], text,
                   fill=(128, 128, 128, 128), font=font)
    textRotate = watermark.rotate(30)

    # rotate the text and crop that
    rLen = math.sqrt((text_w / 2) ** 2 + (text_h / 2) ** 2)
    oriAngle = math.atan(text_h / text_w)
    cropW = rLen * math.cos(oriAngle + math.pi / 6) * 2
    cropH = rLen * math.sin(oriAngle + math.pi / 6) * 2
    box = [int((width - cropW) / 2 - 1) - 60,
           int((height - cropH) / 2 - 1) - 50,
           int((width + cropW) / 2 + 1) + 50,
           int((height + cropH) / 2 + 1) + 50]
    textIm = textRotate.crop(box)
    pasteW, pasteH = textIm.size

    # put the rotated text on a new canvas
    textBlank = Image.new("RGB", (width, height))
    pasteBox = (int((width - pasteW) / 2 - 1), int((height - pasteH) / 2 - 1))
    textBlank.paste(textIm, pasteBox)

    # paste the mask on image
    watermask = textBlank.convert("L").point(lambda x: min(x, 100))
    watermark.putalpha(watermask)

    image.paste(watermark, None, watermark)
    return image


def main(input, output, model, model2, demo=True):
    img_height = 300  # Height of the model input images
    img_width = 300  # Width of the model input images
    n_classes = 1  # Number of positive classes, e.g. 20 for Pascal VOC,
    # 80 for MS COCO
    normalize_coords = True
    # model, model2 = model_load('product-analytics-group7/server/checkpoint')
    # img_path_test = sys.argv[1]
    img_path_test = input
    img_load, orig_images, input_images = trans_img(img_path_test)
    text_box = text_detect(orig_images, input_images, model)

    # add background color
    xmin, ymin, xmax, ymax = text_box[0][0]
    image_patch = orig_images[0][ymin:ymax, xmin:xmax, :]
    bg_color = np.quantile(image_patch[np.where(image_patch > 220)], 0.3)

    # Segmentation of text
    mask = mask_gen(img_load, model2)
    img_seg = np.array(img_load)
    img_seg[mask == 0] = bg_color

    #    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="～/product-analytics
    # -group7/sernmt-API-07b7802bb743.json"
    ocr_page_tran, text_box_clean = translate_img(img_seg, text_box)

    masked_im = text_fill(img_load, text_box_clean, list(ocr_page_tran[0]),
                          mask, int(bg_color))

    # demo image should add a water mask
    if demo:
        masked_im = water_mask(masked_im)

    masked_im.save(output)


if __name__ == '__main__':
    main()
