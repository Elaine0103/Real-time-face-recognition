import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid
import cv2
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from av import VideoFrame
import os
import pickle
import face_recognition
import numpy as np
import aiohttp_cors
from PIL import Image
from io import BytesIO
import base64
import time
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import aiohttp
import requests
import socketio


# Load the service account key for Firebase authentication
cred = credentials.Certificate("react-basic/first-spa/basicaiortc__serviceAccountKey.json")
# Initialize the Firebase app with the credentials and the database URL
firebase_admin.initialize_app(cred,{
    "databaseURL":"https://basicaiortc-default-rtdb.firebaseio.com/",
    "storageBucket":"basicaiortc.appspot.com"
})


bucket = storage.bucket()

# Load the encoding file
print("Loading Encode File...")
file = open("react-basic/first-spa/backend/EncodeFile_aiortc.p", "rb")
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, clientIds = encodeListKnownWithIds # Extract the required data from the loaded content
# print(clientIds)
print(" Encode File Loaded...")

ROOT = os.path.dirname(__file__) # Get the root directory of the current script file
logger = logging.getLogger("pc") # Set up a logger named "pc" for logging messages
pcs = set() # Create an empty set to store instances of RTCPeerConnection
relay = MediaRelay() # Create a MediaRelay instance for media handling


sio = socketio.AsyncServer(cors_allowed_origins="*")
# 處理 Socket.IO 連線
@sio.on("connect")
async def connect(sid, environ):
    print("Connected:", sid)

@sio.on("disconnect")
async def disconnect(sid):
    print("Disconnected:", sid)

# 接收 Socket.IO 訊息，進行頁面跳轉
@sio.on("number_assigned", namespace="/")
async def handle_number_assigned(sid, data):
    print("Number assigned:", data)
    client_id = data.get("clientId")
    await sio.emit("number_assigned", {"clientId": client_id}, namespace="/")  # 傳送訊息給前端


# A video stream track that transforms frames from an another track.
class VideoTransformTrack(MediaStreamTrack):
    
    kind = "video"

    def __init__(self, track, transform, frame_skip):
        super().__init__() # Call the __init__() method of the parent class
        self.track = track # Store the original track
        self.transform = transform 
        self.frame_skip = frame_skip  # Set the frame skip value to the desired number
        self.frame_counter = 0 # Counter to keep track of frames processed
        self.matched_frame_base64 = None  # Variable to store the matched frame base64
        self.loop = asyncio.get_event_loop() # Get the event loop 
        self.client_info_cache = {} # Initialize an empty dictionary for client info caching
        
    async def recv(self):
        frame = await self.track.recv() # Get the frame

        self.frame_counter += 1 # Increment the counter
        if self.frame_counter % self.frame_skip != 0: 
            return frame  # Skip frames based on the frame_skip value
        
        image = frame.to_ndarray(format="bgr24")  # Convert the frame to a format

        # Perform face detection on the current frame
        faceCurFrame = face_recognition.face_locations(image) # Returns an array of bounding boxes of human faces in a image
        encodeCurFrame = face_recognition.face_encodings(image, faceCurFrame) # Given an image, return the 128-dimension face encoding for each face in the image.

        # Initialize empty lists to store face matches and face distances
        matches = [] 
        faceDis = [] 

        # Compare face encodings with known encodings
        if encodeCurFrame:
            matches = await self.loop.run_in_executor(None, face_recognition.compare_faces, encodeListKnown, encodeCurFrame[0]) # Compare a list of face encodings against a candidate encoding to see if they match.
            faceDis = await self.loop.run_in_executor(None, face_recognition.face_distance, encodeListKnown, encodeCurFrame[0]) # Compare them to a known face encoding and get a euclidean distance for each comparison face

        if len(faceDis) > 0: # Check if there are any face distance values available for comparison
            matchIndex = np.argmin(faceDis) # Find the index of the closest match to the face encoding among the known encodings
            #print("matchIndex",matchIndex)
            id = clientIds[matchIndex]
        else:
            matchIndex = None

        for (top, right, bottom, left), match, distance in zip(faceCurFrame, matches, faceDis):
            if matches[matchIndex] and faceDis[matchIndex] < 0.5:
                color = (0, 255, 0)
                matched_frame_base64 = self.encode_frame_to_base64(frame)
                self.matched_frame_base64 = matched_frame_base64  # Save the base64 data in a class variable
                self.loop.create_task(self.send_data_to_database(id))  # Call the asynchronous method to send data to the database
                client_info = await self.get_client_info(id)
                # if client_info:
                #     client_info_list = list(client_info.values())
                #     #client_name, client_phone = client_info_list
                #     #print(client_info_list)
                # else:
                #     print("None customer information found")
                
            else:
                color = (0, 0, 255)
            #cv2.rectangle(image,(left,top),(right,bottom),color,2)
            # Draw lines to create a rectangular shape with corners
            cv2.line(image, (left, top), (left + 20, top), color, 2)
            cv2.line(image, (left, top), (left, top + 20), color, 2)
            cv2.line(image, (right, top), (right - 20, top), color, 2)
            cv2.line(image, (right, top), (right, top + 20), color, 2)
            cv2.line(image, (right, bottom), (right - 20, bottom), color, 2)
            cv2.line(image, (right, bottom), (right, bottom - 20), color, 2)
            cv2.line(image, (left, bottom), (left + 20, bottom), color, 2)
            cv2.line(image, (left, bottom), (left, bottom - 20), color, 2)


        new_frame = VideoFrame.from_ndarray(image, format="bgr24") # Create a new VideoFrame object from the modified image
        new_frame.pts = frame.pts # Copy the presentation timestamp (pts) and time base from the original frame
        new_frame.time_base = frame.time_base 
        return new_frame 

    def encode_frame_to_base64(self, frame):
        # Encode the video frame to PNG format
        # The frame is converted to a NumPy array with format "bgr24" before encoding.
        _, buffer = cv2.imencode('.png', frame.to_ndarray(format="bgr24"))
        # The base64-encoded string represents the binary data in a text format.
        return base64.b64encode(buffer).decode('utf-8')
    
    async def get_client_info(self, client_id):
        if client_id in self.client_info_cache:
            # Return client info from cache if available
            return self.client_info_cache[client_id]  

        try:
            # Query the Firebase database to get the client info using the client_id
            client_info = db.reference(f'Client_Info/{client_id}').get()
            # Cache the client info for future use
            self.client_info_cache[client_id] = client_info
            return client_info
        except Exception as e:
            print("Error fetching client info from Firebase:", e)
            return None
        

    async def send_redirect(self, client_id):
        await sio.emit("number_assigned", {"clientId": client_id}, namespace="/")

    async def send_data_to_database(self, client_id):
        if self.matched_frame_base64 is not None:
            try:
                # Prepare the data to be sent to the database
                client_info = await self.get_client_info(client_id)
                if client_info:
                    client_info_list = list(client_info.values())
                    client_name, client_phone = client_info_list
                    data = {
                        "base64": self.matched_frame_base64,
                        "client_name": client_name,
                        "client_phone": client_phone
                    }
                    # print("Base64 data:", self.matched_frame_base64)
                    print("client_name", client_name)
                    print("client_phone", client_phone)

                    # Send the data to the database using API endpoint
                    url = "http://localhost:443/api/assign_number"  # Replace with your actual API endpoint
                    async with aiohttp.ClientSession() as session:
                        async with await session.post(url, json=data) as response:
                            if response.status == 200:
                                print("Data sent to the database successfully.")
                                start_time = datetime.datetime.now() 
                                await asyncio.sleep(10) # Pause the code execution for 10 seconds
                                end_time = datetime.datetime.now()  
                                #time_interval = end_time - start_time
                                #print("Sleep time:", time_interval.total_seconds(), "seconds")
                                await self.send_redirect(client_id)
                            else:
                                print("Failed to send data to the database.")
            except Exception as e:
                print("Error sending data to the database:", e)

# This code snippet is responsible for handling the HTTP request 
# for the index page and returning the corresponding HTML content to the client.
async def index(request):
    content = open(os.path.join(ROOT, "APP-FULL-Finish/react-basic/first-spa/public/facere.html"), "r").read() # Read the content of the "index.html" file
    return web.Response(content_type="text/html", text=content) # Create and return a web response with the HTML content

# This code snippet is responsible for handling the HTTP request 
# for the JavaScript file and returning the corresponding JavaScript content to the client.
async def javascript(request):
    content = open(os.path.join(ROOT, "APP-FULL-Finish/react-basic/first-spa/src/Client.js"), "r").read() # Read the content of the "client.js" file
    return web.Response(content_type="application/javascript", text=content) # Create and return a web response with the JavaScript content


async def offer(request):
    params = await request.json() # Extract the JSON parameters from the request
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"]) # Create an RTCSessionDescription object from the offer parameters

    pc = RTCPeerConnection() # Create a new RTCPeerConnection
    pc_id = "PeerConnection(%s)" % uuid.uuid4() # Generate a unique ID for the PeerConnection
    pcs.add(pc) # Add the PeerConnection to the set of connections

    #＃ Define a logging function that includes the PeerConnection ID
    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote) # Log the creation of the PeerConnection

    
    # player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))
    # prepare local media 
    # Check if the "record_to" argument is provided
    if args.record_to:
        recorder = MediaRecorder(args.record_to)
    else:
        recorder = MediaBlackhole()


    # Setup of event handlers for data channel messages
    # allowing the PeerConnection to send and receive data messages during the WebRTC communication.
    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])


    # Define an event handler for the "connectionstatechange" event on the PeerConnection
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # Define an event handler for the "track" event on the PeerConnection
    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind) # Log the received track kind

        # Add a video track to the PeerConnection with transformation and skipping frames
        if track.kind == "video":
            pc.addTrack(
                VideoTransformTrack(
                    relay.subscribe(track), 
                    transform=params["video_transform"],
                    frame_skip=6
                )
            )
            # Check if recording is enabled
            if args.record_to:
                recorder.addTrack(relay.subscribe(track)) # Add the video track to the recorder

        @track.on("ended") # Define an event handler for the "ended" event on the track
        # async def on_ended():
        async def on_ended():
            log_info("Track %s ended", track.kind) # Log that the track has ended
            await recorder.stop()  # Stop the recorder
            new_video_track = await pc.addTrack(...) 
            await pc.setLocalDescription(await pc.createOffer())

    # Handle offer
    # Handle the offer by setting the remote description on the PeerConnection
    await pc.setRemoteDescription(offer)
    await recorder.start()

    # send answer
    answer = await pc.createAnswer() # Create an answer to the offer
    await pc.setLocalDescription(answer) # Set the local description of the PeerConnection to the created answer

    # Prepare the response to be sent back as a JSON object
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs] # Close the peer connections
    await asyncio.gather(*coros)
    pcs.clear() # Clear the set of peer connections

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video / data-channels demo"
    )
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=7070, help="Port for HTTP server (default: 7070)"
    )
    parser.add_argument("--record-to", help="Write received media to a file."),
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)


    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    web.run_app(
        app, access_log=None, host=args.host, port=args.port, ssl_context=ssl_context
    )
