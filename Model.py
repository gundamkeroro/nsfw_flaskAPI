#!/usr/bin/env python
#encoding: utf-8
import numpy as np
import os
os.environ['GLOG_minloglevel'] = '2'
import sys
import argparse
import glob
import time
from PIL import Image
from StringIO import StringIO
import caffe

def resize_image(data, sz=(256, 256)):
    """
    Resize image. Please use this resize logic for best results instead of the
    caffe, since it was used to generate training dataset
    :param str data:
        The image data
    :param sz tuple:
        The resized image dimensions
    :returns bytearray:
        A byte array with the resized image
    """
    img_data = str(data)
    im = Image.open(StringIO(img_data))
    if im.mode != "RGB":
        im = im.convert('RGB')
    imr = im.resize(sz, resample=Image.BILINEAR)
    fh_im = StringIO()
    imr.save(fh_im, format='JPEG')
    fh_im.seek(0)
    return bytearray(fh_im.read())

def caffe_preprocess_and_compute(pimg, caffe_transformer=None, caffe_net=None,
    output_layers=None):
    """
    Run a Caffe network on an input image after preprocessing it to prepare
    it for Caffe.
    :param PIL.Image pimg:
        PIL image to be input into Caffe.
    :param caffe.Net caffe_net:
        A Caffe network with which to process pimg afrer preprocessing.
    :param list output_layers:
        A list of the names of the layers from caffe_net whose outputs are to
        to be returned.  If this is None, the default outputs for the network
        are returned.
    :return:
        Returns the requested outputs from the Caffe net.
    """
    if caffe_net is not None:

        # Grab the default output names if none were requested specifically.
        if output_layers is None:
            output_layers = caffe_net.outputs

        img_data_rs = resize_image(pimg, sz=(256, 256))
        image = caffe.io.load_image(StringIO(img_data_rs))

        H, W, _ = image.shape
        _, _, h, w = caffe_net.blobs['data'].data.shape
        h_off = max((H - h) / 2, 0)
        w_off = max((W - w) / 2, 0)
        crop = image[h_off:h_off + h, w_off:w_off + w, :]
        transformed_image = caffe_transformer.preprocess('data', crop)
        transformed_image.shape = (1,) + transformed_image.shape

        input_name = caffe_net.inputs[0]
        all_outputs = caffe_net.forward_all(blobs=output_layers,
                    **{input_name: transformed_image})

        outputs = all_outputs[output_layers[0]][0].astype(float)
        return outputs
    else:
        return []


def run(filename):
    pycaffe_dir = os.path.dirname(__file__)

    image_data = open(filename).read()

    # Pre-load caffe model.
    nsfw_net = caffe.Net('nsfw_model/deploy.prototxt',  # pylint: disable=invalid-name
        'nsfw_model/resnet_50_1by2_nsfw.caffemodel', caffe.TEST)

    # Load transformer
    # Note that the parameters are hard-coded for best results
    caffe_transformer = caffe.io.Transformer({'data': nsfw_net.blobs['data'].data.shape})
    caffe_transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost
    caffe_transformer.set_mean('data', np.array([104, 117, 123]))  # subtract the dataset-mean value in each channel
    caffe_transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
    caffe_transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR

    # Classify.
    scores = caffe_preprocess_and_compute(image_data, caffe_transformer=caffe_transformer, caffe_net=nsfw_net, output_layers=['prob'])

    # Scores is the array containing SFW / NSFW image probabilities
    # scores[1] indicates the NSFW probability
    threshold = scores[0]
    confidence = calc_confidence(threshold)
    return confidence

def calc_confidence(threshold):
    #通过正常图片概率生成三个值
    #threshold1, threshold2 分别是正常和色情的两个阈值，小于threshold1为色情，大于threshold2为正常
    #threshold1, threshold2 处的置信度默认为60%，通过替换下面计算过程中的0.6来调节该处的置信度
    #threshold3，用来调节性感置信度为100的值，改变threshold3可以改变性感图片的置信度计算策略
    threshold1 = 0.08
    threshold2 = 0.7
    threshold3 = 0.15
    #print '原始置信度：', threshold
    confidence = [0, 0, 0]

    #正常置信度
    if threshold < threshold2:
        confidence[0] = 0.6 * threshold / threshold2
    else:
        confidence[0] = (threshold - (threshold2 - 0.6) / ( 1 - 0.6)) / (1 - (threshold2 - 0.6) / (1 - 0.6))

    #性感置信度
    if threshold < threshold1:
        confidence[1] = 0.6 * threshold / threshold1
    elif threshold < threshold3:
        confidence[1] = (1 - 0.6) * (threshold - threshold1) / (threshold3-threshold1) + 0.6
    elif threshold < threshold2:
        confidence[1] = (1 - 0.6) * (threshold2 - threshold) /(threshold2 - threshold3) + 0.6
    else:
        confidence[1] = 0.6 * (1 - threshold) / (1 - threshold2)
   
    #色情置信度
    if threshold < threshold1:
        confidence[2] = (threshold1 / (1 - 0.6) - threshold) *(1 - 0.6) / threshold1
    else:
        confidence[2] = 0.6 * (1 - threshold) / (1 - threshold1)
    return confidence

