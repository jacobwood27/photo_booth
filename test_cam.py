import cv2
import time


cap = cv2.VideoCapture("rtsp://192.168.1.2:8080/out.h264")
while(1):
    ret, frame = vcap.read()
    cv.imshow('VIDEO', frame)
    cv.waitKey(1)

# # availableBackends = [cv2.videoio_registry.getBackendName(b) for b in cv2.videoio_registry.getBackends()]
# # print(availableBackends)

# # availableBackends = [cv2.CAP_FFMPEG, cv2.CAP_GSTREAMER, cv2.CAP_INTEL_MFX, cv2.CAP_MSMF, cv2.CAP_V4L2, cv2.CAP_UEYE]

# # for be in availableBackends:
# #     print(be)

# cap = cv2.VideoCapture("/dev/video2", cv2.CAP_V4L2)
# # cap = cv2.VideoCapture("v4l2src device=/dev/video2 ! appsink")
# # cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
# # cap.set(cv2.CAP_PROP_FPS, 30.0)
# # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# # out = cv2.VideoWriter("out.avi", cv2.VideoWriter_fourcc(*'MP42'), 30, (640, 480))
# # out = cv2.VideoWriter("out.mp4", cv2.VideoWriter_fourcc(*'mp4v'), 30, (1280, 720))

# t_start = time.time()

# frames = 0
# while True:
#     _,frame = cap.read() # numpy array shape (720, 1280, 3)


#     frames += 1
#     # out.write(frame)
#     cv2.imshow("a", frame)

#     #   sleep( 40 / 1000) # mimic the processing time

#     if time.time() - t_start > 5:
#         break

# print(frames, frames/5)
# cap.release()
# cv2.destroyAllWindows()
