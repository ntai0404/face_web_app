distance_result = "Không phát hiện khuôn mặt."
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = distances.argmin()
        best_distance = distances[best_match_index]

        if best_distance < 0.5:
            name = known_names[best_match_index]
        else:
            name = "Unknown"

        distance_result = f"{name} (khoảng cách: {best_distance:.2f})"
        cv2.rectangle(image_bgr, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image_bgr, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)