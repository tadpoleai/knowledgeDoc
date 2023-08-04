import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from starlette.middleware.cors import CORSMiddleware
import openai
from process import detect_and_crop_face, generate_headshot
from PIL import Image
import io
import cv2 as cv
import numpy

LISTENING_IP = "0.0.0.0"
LISTENING_PORT = 50001
UVICORN_WORKS = 1

def create_app():
    return Application()

class Application():
    def __init__(self):
        # start the fastapi server
        self._fastapi = FastAPI()
        self._fastapi.add_api_route(
            path="/",
            endpoint=self.index,
            methods=["GET"]
        )

        self._fastapi.add_api_route(
            path="/headshots/gen",
            endpoint=self.headshots_generator,
            methods=["POST"]
        )

        origins = ["*"]
        self._fastapi.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def __getattr__(self, attr):
        if hasattr(self._fastapi, attr):
            return getattr(self._fastapi, attr)
        else:
            raise AttributeError(f"{attr} not exist")

    async def __call__(self, *args, **kwargs):
        return await self._fastapi(*args, **kwargs)

    def index(self):
         return {"message": "Welcome to tadpole's world"}, 200

    async def headshots_generator(self, file: UploadFile = File(...)):
        image_content = await file.read()
        pil_image = Image.open(io.BytesIO(image_content))

        imput_image_cv = cv.cvtColor(numpy.asarray(pil_image), cv.COLOR_RGB2BGR)
        face_image = detect_and_crop_face(imput_image_cv)

        if face_image:
            response = generate_headshot(face_image)

            for r in response['data']:
                print(r)

            return {"message": response['data']}, 200
        else:
            return {"message": "May not detect any human faces, please try again"}, 200

        pass


if __name__ == "__main__":
    # start the unicorn
    uvicorn.run(app='main:create_app', host=LISTENING_IP, port=int(LISTENING_PORT), workers=int(UVICORN_WORKS), factory='true')
    pass