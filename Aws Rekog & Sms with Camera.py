import cv2
import csv
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from playsound import playsound
import botocore



cam = cv2.VideoCapture(0)

emotion_result=""
age_result=""
gender_result=""
age_count=0
data_code=""

SENDER = "ricky_indra@hotmail.com"
RECIPIENT = "rickyindra21@gmail.com"
AWS_REGION = "ap-southeast-2"
SUBJECT = "Someone ringed your bell"
CHARSET = "utf-8"



with open('credentials.csv','r') as input:
    next(input)
    reader= csv.reader(input)
    for line in reader:
        access_key_id= line[2]
        secret_access_key = line[3]

client = boto3.client('ses',region_name=AWS_REGION,aws_access_key_id = access_key_id,
                        aws_secret_access_key = secret_access_key)
                        


def detect_faces(key, attributes=['ALL'], region="ap-southeast-2"):
	rekognition = boto3.client("rekognition", region, aws_access_key_id = access_key_id,
                        aws_secret_access_key = secret_access_key)
	response = rekognition.detect_faces(
	    Image={
			"S3Object":{ 
                            "Bucket": "test-upload-gambar1",
                            "Name": "gestur-dan-ekspresi-presiden-jokowi-tangkapan-layar-video-setpres-riyoutube.png"
		}},
	    Attributes=attributes,
	)
	return response['FaceDetails']
    
BUCKET_NAME = 'test-upload-gambar1' # replace with your bucket name
KEY = 'gestur-dan-ekspresi-presiden-jokowi-tangkapan-layar-video-setpres-riyoutube.png' # replace with your object key

s3 = boto3.resource('s3')


            
while True:
    ret, img = cam.read()

    cv2.imshow("Test", img)

    if not ret:
        break

    k=cv2.waitKey(1)

    if k%256==27:
        #For Esc key
        print("Close")
        break
    elif k%256==32:
        #For Space key
        print("Image "+"saved")
        file='C:/Files/NotDesktop/img.jpg'
        cv2.imwrite(file, img)
        try:
            s3.Bucket(BUCKET_NAME).download_file(KEY, 'gestur-dan-ekspresi-presiden-jokowi-tangkapan-layar-video-setpres-riyoutube.png')
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise
        ATTACHMENT = "C:/Files/NotDesktop/gestur-dan-ekspresi-presiden-jokowi-tangkapan-layar-video-setpres-riyoutube.png"
        photo = file
        with open(photo, 'rb') as source_image:
             source_bytes = source_image.read()           
        for face in detect_faces(photo):
            x="Face ({Confidence}%)".format(**face)
            print (x)
            # emotions
            for emotion in face['Emotions']:
                t="{Confidence}".format(**emotion)
                y="{Type}".format(**emotion)
                t=float(t)
                if(y=="CALM" and t>80):
                    print ("  {Type} : {Confidence}%".format(**emotion))
                    emotion_result="{Type} : {Confidence}%".format(**emotion)
                if(y=="ANGRY" and t>80):
                    print ("  {Type} : {Confidence}%".format(**emotion))
                    emotion_result="{Type} : {Confidence}%".format(**emotion)
                if(y=="SAD" and t>80):
                    print ("  {Type} : {Confidence}%".format(**emotion))
                    emotion_result="{Type} : {Confidence}%".format(**emotion)
                if(y=="FEAR" and t>80):
                    print ("  {Type} : {Confidence}%".format(**emotion))
                    emotion_result="{Type} : {Confidence}%".format(**emotion)
                if(y=="CONFUSED" and t>80):
                    print ("  {Type} : {Confidence}%".format(**emotion))
                    emotion_result="{Type} : {Confidence}%".format(**emotion)
                if(y=="HAPPY" and t>80):
                    print ("  {Type} : {Confidence}%".format(**emotion))
                    emotion_result="{Type} : {Confidence}%".format(**emotion)
                if(y=="SURPRISED" and t>80):
                    print ("  {Type} : {Confidence}%".format(**emotion))
                    emotion_result="{Type} : {Confidence}%".format(**emotion)
            #print emotion_result
            for gender, value in face['Gender'].items():
                g="{value}".format(value=value)
                if(g=="Male" or g=="Female"):
                    print ("  "+g)
                    gender_result=g
            strings = [3]
            for age, value in face['AgeRange'].items():
                age= "{value}".format(value=value)
                if(age_count==0):
                    low_age=age
                elif (age_count==1):
                    high_age=age
                age_count +=1
                
            age_count=0
            age_result=low_age+ " - " + high_age+" years old"
            print (low_age+" -", high_age+" years old")
        
        msg = MIMEMultipart('mixed')
        msg['Subject'] = SUBJECT 
        msg['From'] = SENDER 
        msg['To'] = RECIPIENT

        msg_body = MIMEMultipart('alternative')
        
        BODY_TEXT = "Gender : "+gender_result+"\n"+"Age : "+age_result+"\n"+"Emotion : "+emotion_result+"\n"        
        textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)

        msg_body.attach(textpart)
        att = MIMEApplication(open(ATTACHMENT, 'rb').read())
        att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))
        msg.attach(msg_body)
        msg.attach(att)    
            
            
        try:
            #Provide the contents of the email.
            response = client.send_raw_email(
                Source=SENDER,
                Destinations=[
                    RECIPIENT
                ],
                RawMessage={
                    'Data':msg.as_string(),
                },
                #ConfigurationSetName=CONFIGURATION_SET
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            
            print("Email sent! Message ID:"),
            print(response['MessageId'])
            playsound('ring.mp3')

cam.release
cv2.destroyAllWindows
