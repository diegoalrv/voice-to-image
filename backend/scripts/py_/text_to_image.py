import boto3
import requests
import json
import datetime
from PIL import Image, ImageDraw
from io import BytesIO
import qrcode
import csv
import os

class StableDiffusionAPIConnection:
    def __init__(self, api_key_path, s3_credentials_csv_path, bucket_name):
        self.api_key = self.load_api_key(api_key_path)
        self.aws_access_key_id, self.aws_secret_access_key = self.load_s3_credentials(s3_credentials_csv_path)
        self.s3_client = boto3.client('s3', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
        self.s3_bucket_name = bucket_name
        self.s3_filename = ""

    def load_api_key(self, json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
        return data.get("key", None)

    def load_s3_credentials(self, csv_file):
        with open(csv_file, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            access_key, secret_access_key = next(csv_reader)
        return access_key, secret_access_key

    def generate_s3_filename(self, extension="png"):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}.{extension}"
        return filename

    def generate_image(self, input_prompt):
        prompt = input_prompt
        # print(self.api_key)
        response = requests.post('https://clipdrop-api.co/text-to-image/v1',
                                 files={'prompt': (None, prompt, 'text/plain')},
                                 headers={'x-api-key': os.getenv("sdapi")})
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            response.raise_for_status()

    def upload_to_s3(self, image):
        buffer = BytesIO()
        image.save(buffer, 'PNG')
        buffer.seek(0)
        s3_filename = self.generate_s3_filename()
        self.s3_client.put_object(Bucket=self.s3_bucket_name, Key=s3_filename, Body=buffer)
        return s3_filename

    def generate_presigned_url(self, s3_filename):
        return self.s3_client.generate_presigned_url('get_object',
                                                     Params={'Bucket': self.s3_bucket_name, 'Key': s3_filename},
                                                     ExpiresIn=3600)

    def add_qr_to_image(self, image, qr_url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img_resized = qr_img.resize((150, 150))

        image_copy = image.copy()
        margin = 10
        position = (image_copy.width - qr_img_resized.width - margin, margin)
        
        # Dibuja un cuadrado blanco en la posición donde irá el código QR
        draw = ImageDraw.Draw(image_copy)
        end_position = (position[0] + qr_img_resized.width, position[1] + qr_img_resized.height)
        draw.rectangle([position, end_position], fill="white")
        
        # Pega el código QR sobre el cuadrado blanco sin usar la máscara
        image_copy.paste(qr_img_resized, position)
        return image_copy

    def process_image(self, input_prompt):
        image = self.generate_image(input_prompt)
        self.s3_filename = self.upload_to_s3(image)
        download_link = self.generate_presigned_url(self.s3_filename)
        final_image = self.add_qr_to_image(image, download_link)
        return final_image
