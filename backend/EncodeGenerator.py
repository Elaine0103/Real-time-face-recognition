import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# Load the service account key for Firebase authentication
cred = credentials.Certificate("basicaiortc__serviceAccountKey.json")
# Initialize the Firebase app with the credentials and the database URL
firebase_admin.initialize_app(cred,{
    "databaseURL":"https://basicaiortc-default-rtdb.firebaseio.com/",
    "storageBucket":"basicaiortc.appspot.com"
})


# Importing clients images
# Path to the folder containing client images
folderimagesPath = "Images"
# Get the list of image file names in the folder
imagePathList = os.listdir(folderimagesPath)
#print(folderimagesPath)
#print(imagePathList)

# Lists to store the images and client IDs
imgList = []
clientIds = []

# Loop through each image file
for path in imagePathList:
    # Skip the .DS_Store file on macOS
    if(path==".DS_Store"):
        continue
    
    # Read the image and append it to the imgList
    imgList.append(cv2.imread(os.path.join(folderimagesPath,path))) 
    # Extract the client ID from the file name and add it to clientIds
    clientIds.append(os.path.splitext(path)[0])
    #print(path)
    #print(os.path.splitext(path)[0])

    # Upload the image file to Firebase Storage
    fileName = os.path.join(folderimagesPath, path)
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

#print(len(imgList))
#print(clientIds)
#print(imgList)

#This function can be used to obtain face encodings for a list of images, which can then be used for face recognition or other related tasks.
# Function to find encodings for the images
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        # Convert image to RGB format
        img= cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # Find the face encoding
        encode = face_recognition.face_encodings(img)[0]
        #print(encode)
        encodeList.append(encode)
    
    return encodeList

print("Encoding Started ...")
# Find encodings for the images in imgList
encodeListKnown =findEncodings(imgList)
# Combine encodings with client IDs
print("Encoding Complete")
encodeListKnownWithIds =[encodeListKnown,clientIds]
#print(encodeListKnown)

print("Encoding Complete")

file = open("EncodeFile_aiortc","wb")
# Save the encodings with client IDs to the file
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File saved")