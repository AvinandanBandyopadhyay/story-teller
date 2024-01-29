import os
import re
import glob
import boto3
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

s3 = boto3.client('s3')

bucketName = "experimental-repo-aviband"
storyKey = "story"
temp_video_file = "videoChunks/video{0}.mp4"


def add_static_image_to_audio(inputImage, inputAudio, frameInx):
    audio = AudioFileClip(inputAudio)
    clip = ImageClip(inputImage).set_duration(audio.duration)
    clip = clip.set_audio(audio)
    clip.write_videofile(temp_video_file.format(frameInx), fps=24)
    return clip

def getObjectCount():
    s3p = s3.get_paginator('list_objects_v2')
    audioKey = "/".join([storyKey, "audio"])
    s3i = s3p.paginate(Bucket=bucketName, Prefix=audioKey)
    fileCount = 0
    for KeyCount in s3i.search('KeyCount'):
        fileCount += KeyCount
    return fileCount
 
imageFileGeneric = 'image{0}.png'
def getImageFile(indx):
    fileName = "/".join(["images", imageFileGeneric.format(indx)])
    key = "/".join([storyKey, fileName])
    s3.download_file(bucketName, key, fileName)
    return fileName

def getAudioFileNames():
    fileNames = []
    prefix = "/".join([storyKey, "audio"])
    result = s3.list_objects_v2(Bucket=bucketName, Prefix=prefix)
    for item in result['Contents']:
        files = item['Key']
        fileNames.append(files)
    return fileNames

audioFileGeneric = 'audio{0}.mp3'
def getAudioFile(indx, audioFileNames):
    subPath = "/".join(["story", "audio", "audio"])
    audioregexTerm = subPath + f'{indx}' + "\."
    audioregex = re.compile(audioregexTerm)
    keys = filter(audioregex.match, audioFileNames)
    keyList = list(keys)
    key = keyList[0]
    fileName = "/".join(["audios", audioFileGeneric.format(indx)])
    print(key)
    s3.download_file(bucketName, key, fileName)
    return fileName

def createMovie():
    videoClips = []
    imgPath = "images"
    isExist = os.path.exists(imgPath)
    if not isExist:
        os.makedirs(imgPath)
    else:
        fileNames = imgPath+'/*.png'
        for filename in glob.glob(fileNames):
            os.remove(filename)
    audioPath = "audios"
    isExist = os.path.exists(audioPath)
    if not isExist:
        os.makedirs(audioPath)
    else:
        fileNames = audioPath+'/*.mp3'
        for filename in glob.glob(fileNames):
            os.remove(filename)
    videoPath = "videoChunks"
    isExist = os.path.exists(videoPath)
    if not isExist:
        os.makedirs(videoPath)
    else:
        fileNames = videoPath+'/*.mp3'
        for filename in glob.glob(fileNames):
            os.remove(filename)
    objectCount = getObjectCount()
    audioFileNames = getAudioFileNames()
    print(audioFileNames)
    for indx in range(objectCount):
        actualIndx = indx + 1
        audioFile = getAudioFile(actualIndx, audioFileNames)
        imageFile = getImageFile(actualIndx)
        videoClip = add_static_image_to_audio(imageFile, audioFile, actualIndx)
        videoClips.append(videoClip)
    mergedClip = concatenate_videoclips(videoClips)
    mergedClip.write_videofile("story.mp4", fps=24)
    return

createMovie()