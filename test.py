import boto3
import io
from PIL import Image
import pyttsx3
import pygame
from playsound import playsound

#creating an engine for text-to-speech
engine = pyttsx3.init()


rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

image_path = input("Enter path of the image to check: ")

image = Image.open(image_path)
stream = io.BytesIO()
image.save(stream,format="JPEG")
image_binary = stream.getvalue()


response = rekognition.search_faces_by_image(
        CollectionId='famouspersons',
        Image={'Bytes':image_binary}                                       
        )

found = False
for match in response['FaceMatches']:
    print (match['Face']['FaceId'],match['Face']['Confidence'])
        
    face = dynamodb.get_item(
        TableName='face_recognition',  
        Key={'RekognitionId': {'S': match['Face']['FaceId']}}
        )
    
    if 'Item' in face:
        print ("Found Person: ",face['Item']['FullName']['S'])
        name = face['Item']['FullName']['S']
        string_to_speak = "Welcome" + name
        engine.save_to_file(string_to_speak, 'output.wav')
        engine.runAndWait()
        playsound('output.wav')
        found = True
        break

if not found:
    print("Person cannot be recognized")
    playsound('discard.mp3')