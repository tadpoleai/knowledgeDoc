import openai
import numpy as np
import math
import cv2 as cv
import imutils
import mediapipe as mp
import matplotlib.pyplot as plt
# from PIL import Image
import uuid
import threading
import os
from dotenv import load_dotenv
load_dotenv()

MAX_IMAGE_DIM = 1024

def detect_and_crop_face(image_cv, debug = False):
    def rotateImage(face):
        face_data = face.location_data
        rx = face_data.relative_keypoints[0].x
        ry = face_data.relative_keypoints[0].y
        lx = face_data.relative_keypoints[1].x
        ly = face_data.relative_keypoints[1].y
        deltaY = abs(ly - ry)
        deltaX = abs(lx - rx)
        rotationAngle = np.rad2deg(math.tan(deltaY/deltaX))
        rotatedImage = imutils.rotate(
            image_cv[:, :, ::-1].copy(), rotationAngle)
        return rotatedImage

    # resize to 1024 max
    # if max(image_cv.shape) > MAX_IMAGE_DIM:
    #     r = float(MAX_IMAGE_DIM) / max(image_cv.shape)
    #     dim = (int(image_cv.shape[1] * r), int(image_cv.shape[0] * r))
    #     image_cv = cv.resize(image_cv, dim, interpolation=cv.INTER_AREA)
        # cv.save('test.jpg', image_cv)

    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    face_detection_results = face_detection.process(image_cv[:, :, ::-1])
    if (not hasattr(face_detection_results, 'detections')) or \
            (not face_detection_results.detections) or \
            len(face_detection_results.detections) == 0:
        return None

    rotatedImage = rotateImage(face_detection_results.detections[0])

    rotated_face_detection_results = face_detection.process(
        rotatedImage[:, :, ::-1])

    boundingBox = rotated_face_detection_results.detections[0].location_data.relative_bounding_box
    xmin = int(boundingBox.xmin * image_cv.shape[1])
    ymin = int(boundingBox.ymin * image_cv.shape[0])
    width = int(boundingBox.width * image_cv.shape[1])
    height = int(boundingBox.height * image_cv.shape[0])

    rotatedImage = rotatedImage[ymin:ymin+height, xmin:xmin+height]
    print(f'face area: {xmin},{ymin},{width},{height}')

    background = np.zeros((MAX_IMAGE_DIM, MAX_IMAGE_DIM, 4), np.uint8)

    x_offset = (background.shape[0] - rotatedImage.shape[0]) // 2
    y_offset = (background.shape[1] - rotatedImage.shape[1]) // 2

    alpha = np.sum(rotatedImage, axis=-1) > 0
    alpha = np.uint8(alpha * 255)
    rotatedRGBAImage = np.dstack((rotatedImage, alpha))

    background[y_offset:y_offset+rotatedRGBAImage.shape[0],
               x_offset:x_offset+rotatedRGBAImage.shape[1]] = rotatedRGBAImage

    random_uuid = uuid.uuid4()
    unique_filename = '.'.join((str(random_uuid), str(threading.currentThread().ident), 'png'))

    cv.imwrite(unique_filename, cv.cvtColor(background, cv.COLOR_RGBA2BGRA))


    if debug:
        plt.figure(figsize=[10, 10])
        plt.title("Resultant Image")
        plt.axis('off')
        plt.imshow(background)
        plt.show()

    return unique_filename


def generate_headshot(face_image, amt = 5):
    print("start generate...")
    openai.api_key = os.getenv("OPENAI_KEY")

    response = openai.Image.create_edit(
        image=open(face_image, "rb"),
        # prompt="A Professional headshot of one person you should hire",
        prompt="A close-up headshot of a person with a neutral expression",
        n=amt,
        size="1024x1024"
    )

    print("dalle returned")
    return response