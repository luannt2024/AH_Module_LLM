# import cv2
# import numpy as np
# from insightface.app import FaceAnalysis

# face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
# face_app.prepare(ctx_id=0, det_size=(640, 640))

# def compare_faces(image1, image2):
#     faces1 = face_app.get(image1)
#     faces2 = face_app.get(image2)

#     if len(faces1) == 0 or len(faces2) == 0:
#         return "Không tìm thấy khuôn mặt"

#     embedding1 = faces1[0].normed_embedding
#     embedding2 = faces2[0].normed_embedding
#     similarity = np.dot(embedding1, embedding2)

#     return "Hai khuôn mặt giống nhau" if similarity > 0.6 else "Hai người khác nhau"