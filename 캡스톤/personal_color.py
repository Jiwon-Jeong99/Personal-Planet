import cv2 as cv
import numpy as np
import dlib


def createBox(img, points, check=0, color=0, plus=0):

    mask = np.zeros_like(img)
    result = cv.fillPoly(mask, [points], (255, 255, 255))

    if check == 1:
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        color = cv.cvtColor(color, cv.COLOR_BGR2HSV)

        bbox = cv.boundingRect(points)
        x, y, w, h = bbox

        for i in range(y, y + h):
            for j in range(x, x + w):
                hsv[i][j][0] = color[i][j][0]

                if abs(hsv[i][j][1] - color[i][j][1]) >= 10:
                    if hsv[i][j][1] > color[i][j][1] and hsv[i][j][1] - 10 > 0:
                        hsv[i][j][1] -= 10
                    elif hsv[i][j][1] > color[i][j][
                            1] and hsv[i][j][1] + 10 < 255:
                        hsv[i][j][1] += 10

                if abs(hsv[i][j][2] - color[i][j][2]) >= 10:
                    if hsv[i][j][2] > color[i][j][1] and hsv[i][j][2] - 10 > 0:
                        hsv[i][j][2] -= 10
                    elif hsv[i][j][2] > color[i][j][
                            2] and hsv[i][j][2] + 10 < 255:
                        hsv[i][j][2] += 10

        masked = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
        result = cv.bitwise_and(masked, result)

    return result


def faceDetect(img, b, g, r):
    input = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    bgr = np.zeros_like(img)

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    faces = detector(input)

    if faces:
        face = faces[0]

        bgr[:] = b, g, r
        landmarks = predictor(input, face)
        myPoints = []

        for n in range(68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            myPoints.append([x, y])

        # get masks
        myPoints = np.array(myPoints)
        masked = createBox(img, myPoints[48:68])
        nudeLips = createBox(img, myPoints[48:68], 1, bgr, 1)

        # make nude lip
        sub = cv.subtract(img, masked)
        lip = cv.add(sub, nudeLips)

        # resize image
        t, b, l, r = face.top(), face.bottom(), face.left(), face.right()
        if t < 0:
            t = 0
        if b > img.shape[0]:
            b = img.shape[0]
        if l < 0:
            l = 0
        if r > img.shape[1]:
            r = img.shape[1]

        result = lip[t:b, l:r]
        result = cv.resize(result, dsize=(720, 720))

        return result


def show_result(background, img):
    background[1300:2020, 225:945, :] = 0
    background[1300:2020, 225:945] = img[:, :]

    return background


#이후에 변동할 예정
#순서

# 01. 이미지를 입력받는다
# 02. 톤별로 리컬러링을 진행한다
# 03. 리컬러링 결과를 사용자가 입력한다
# 04. 최종 퍼스널 컬러와 리컬러링 결과를 합성한 이미지를 불러온다
# 05. 버튼을 누르면 다운로드 가능


def start(filename, ext):
    img = cv.imread(f"{filename}{ext}")
    warm_spring = faceDetect(img, 49, 64, 227)
    cool_summer = faceDetect(img, 165, 122, 255)
    warm_autumn = faceDetect(img, 31, 26, 173)
    cool_winter = faceDetect(img, 40, 0, 130)

    cv.imwrite(f"{filename}_warm_spring{ext}", warm_spring)
    cv.imwrite(f"{filename}_cool_summer{ext}", cool_summer)
    cv.imwrite(f"{filename}_warm_autumn{ext}", warm_autumn)
    cv.imwrite(f"{filename}_cool_winter{ext}", cool_winter)


def final(result, filen):
    if result == "1":
        background = cv.imread("html/bg_spring.png")
    elif result == "2":
        background = cv.imread("html/bg_summer.png")
    elif result == "3":
        background = cv.imread("html/bg_autumn.png")
    elif result == "4":
        background = cv.imread("html/bg_winter.png")

    filename = f"html/{filen}"
    file = cv.imread(filename)
    result = show_result(background, file)
    cv.imwrite(f"{filename}.png", result)
    return f"{filen}.png"
