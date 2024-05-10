# Resizing photos
from PIL import Image
from pathlib import Path

HEIGHT_BASED = 0
WIDTH_BASED = 1

def setPPI(img: Image, targetRatio: tuple, targetPPI: int):

    maxWidth = round(targetPPI * targetRatio[0]/1.75) # At most, allowed to be 1/2 of the target width
    maxHeight = targetPPI * targetRatio[1]  # Must fit within the target ratio height

    # Assume width = maxWidth, (eg, ppi * 2 in a 4x6)
    # and then find what the height is
    newWidth = maxWidth
    downsizeRatio = newWidth / img.width # to do that, find how the ratio that downsized the width
    newHeight =  round(img.height * downsizeRatio)

    i = 1
    while (newHeight > maxHeight):
        newWidth -= i  # Decreases width by 1, until the heights fits
        downsizeRatio = newWidth / img.width
        newHeight = round(img.height * downsizeRatio)


    return img.resize((newWidth, newHeight))



def change_dimensions(img: Image, newDimension: tuple):
    # Header
    if img.width > img.height:
        raise ValueError("Image should be in portrait not landscape")
    if newDimension[0] > newDimension[1]:
        raise ValueError("Ratio should be in portrait not landscape")
    newRatio = newDimension[0] / newDimension[1]

    # Calculating new size
    possibleWidth = img.height * newRatio
    possibleHeight = img.width / newRatio

    if possibleWidth < img.width:
        possibleWidth = None
    newSize = (possibleWidth, img.height) if possibleWidth else (img.width, possibleHeight)
    newSize = round(newSize[0]), round(newSize[1])

    # Getting dimensions of the whitespace boxes
    if possibleWidth:
        landscapeBox = None
        portraitBox = possibleWidth - img.width, img.height
    else:
        portraitBox = None
        landscapeBox = img.width, possibleHeight - img.height

    # Creating the new image
    whitespace = Image.new("RGB", newSize, "white")
    whitespace.paste(img)

    resizedImage = {
        "object": whitespace,
        "portraitBox": portraitBox,
        "landscapeBox": landscapeBox,
    }
    return resizedImage


def convertWxH(size: tuple, dim: tuple) -> tuple:
    # To convert any ratio to a target one without clipping
    sizeByWidth = (size[0], round(size[0] / dim[0] * dim[1]))
    sizeByHeight = (round(size[1] / dim[1] * dim[0]), size[1])

    # idk how to explain clipping but yeah this figures out
    # what the number should be to avoid clipping

    # if height calculated by width is smaller than the real height,
    # then it will be clipped
    if sizeByWidth[1] < size[1]:
        return (sizeByHeight, HEIGHT_BASED)

    return (sizeByWidth, WIDTH_BASED)


def setInches(img: Image, targetInches, newDim) -> Image:
    """
    Creates a whitespace with given newDim and pastes the image on to it
    :param img:
    :param targetInches:
    :param newDim:
    :return:
    """

    # Get the new size, and which dimension that was based on
    newSize, dimBase = convertWxH(img.size, newDim)

    whitespace = Image.new("RGB", newSize, "white")
    if img.height > whitespace.height or img.width > whitespace.width:
        print("Image is too big, result will be clipped")
    whitespace.paste(img)

    return whitespace


def downsize(img: Image, targetValue, newDim):

    resizedImage = change_dimensions(img, newDim)
    img = resizedImage["object"]
    if targetValue == 0:
        return resizedImage
    else:
        targetPercent = targetValue
        whiteSpacePercent = 1 + (1 - targetPercent)
        newSize = round(img.width * whiteSpacePercent), round(img.height * whiteSpacePercent)
        portraitBox = newSize[0] - img.width, newSize[1]
        landscapeBox = newSize[0], newSize[1] - img.height
        whitespace = Image.new("RGB", newSize, "white")
        whitespace.paste(img)
        resizedImage["object"] = whitespace
        resizedImage["portraitBox"] = portraitBox
        resizedImage["landscapeBox"] = landscapeBox
        resizedImage["originalSize"] = img.size
        return resizedImage


def fitsBox(baseBox, secondaryBox):

    if baseBox[0] >= secondaryBox[0] and baseBox[1] >= secondaryBox[1]:
        return True
    else:
        return False


def collage(baseImg: Image, imageBox, portraitBox, landscapeBox, images):
    i = 1
    while True:
        #print(i)
        if i >= len(images):
            break
        pastedImage = False
        argumentImage = images[i]

        if argumentImage.width > argumentImage.height:
            return ValueError
            #argumentImage = argumentImage.rotate(90, expand=True)

        if portraitBox != (0, 0) and fitsBox(portraitBox, argumentImage.size):
            # Header
            portraitBoxWidth, portraitBoxHeight = portraitBox
            landscapeBoxWidth, landscapeBoxHeight = landscapeBox
            pastedImage = True

            # Removes reference to boxed pasted into, and updates size of the clipped box
            portraitBox = (0, 0)
            if landscapeBox != (0, 0) and argumentImage.height > portraitBoxHeight:
                landscapeBox = (landscapeBoxWidth - portraitBoxWidth, landscapeBoxHeight)

            # Pasting the image
            baseImg.paste(argumentImage, (imageBox[0], 0))

        elif landscapeBox != (0, 0) and fitsBox(landscapeBox, (argumentImage.height, argumentImage.width)):
            # Header
            portraitBoxHeight = portraitBox
            landscapeBoxWidth, landscapeBoxHeight = landscapeBox
            pastedImage = True

            # Removes reference to boxed pasted into, and updates size of the clipped box
            landscapeBox = (0, 0)
            if portraitBox != (0, 0) and argumentImage.width > landscapeBoxWidth:
                portraitBox = (portraitBoxHeight - landscapeBoxHeight)

            # Pasting the image
            baseImg.paste(argumentImage.rotate(-90, expand=True), (0, imageBox[1]))

        if pastedImage:
            images.pop(i)
            i -= 1
            if portraitBox == (0, 0) and landscapeBox == (0, 0):
                break
        i += 1

    #baseImg.show()
    return baseImg


def batch_edit(filePaths, saveDir: Path, newDim=(0, 0), downsizeTarget=0.0, doCollage=False):
    filePaths = list(map(lambda dir: Path(dir), filePaths))
    saveLocations = []
    print("Getting save locations of photos")
    for location in filePaths:
        print(location)
        saveLocations.append((saveDir / location.stem).with_suffix(".jpg"))

    if doCollage:
        print("Resizing images for collaging")
        imageSizes = []
        for i in range(len(filePaths)):
            with Image.open(filePaths[i]) as firstImg:
                firstImg = firstImg.convert('RGB')
                # Rotating the img to match wxh
                if firstImg.width > firstImg.height:
                    firstImg = firstImg.rotate(90, expand=True)

                targetPPI = 600
                firstImg = setPPI(firstImg, newDim, targetPPI)
                imageSizes.append(firstImg.size)
                firstImg.save(saveLocations[i])
                print(f"{targetPPI}ppi: {filePaths[i].name} {firstImg.size}")

        # Now that the images are the right dpi,
        # pasting one onto the collage, and pasting others that fit
        collageIth = 0
        while (len(saveLocations) > 0):
            firstImg = Image.open(saveLocations.pop(0))  # Getting the first im
            imageSizes.pop(0)
            # Getting the background to paste it on
            collageSize = (targetPPI * newDim[0], targetPPI * newDim[1])
            bg = Image.new("RGB", collageSize, "white")


            # Leftover space to paste images into
            openRightBox = (collageSize[0] - firstImg.width, collageSize[1])
            openBottomBox = (collageSize[0], collageSize[1] - firstImg.height)
            i = 0


            while i < len(saveLocations) and (openRightBox != (0,0) or openBottomBox != (0,0)):
                print(i)
                print("len: " + str(len(filePaths)))
                if fitsBox(openRightBox, imageSizes[i]):  # note that in right box is portrait, same as image
                    secondaryImg = Image.open(saveLocations.pop(i))
                    imageSizes.pop(i)
                    bg.paste(secondaryImg, (firstImg.width, 0))  # Top right corner of first image = top left corner of secondary
                    openRightBox = (0,0)

                    # adjusting bottom box height, if it is clipped by the secondary image
                    if firstImg.height < secondaryImg.height:
                        openBottomBox = (openBottomBox[0], collageSize[1] - secondaryImg.height)
                    continue # since we popped, img[i] is a new number, so start loop over

                # Note that everytime item is popped, we restart, so no worries about
                # and edge case where there are no items b/c above if popped the only one in the list
                if fitsBox(openBottomBox, tuple(reversed(imageSizes[i])) ):
                    secondaryImg = Image.open(saveLocations.pop(i))
                    imageSizes.pop(i)
                    bg.paste(secondaryImg.rotate(-90, expand=True), (0, firstImg.height))
                    openBottomBox = (0,0)
                    continue  # since we popped, img[i] is a new number, so start loop over

                i += 1
            bg.paste(firstImg, (0, 0))
            bg.save( (saveDir / str(collageIth)).with_suffix(".jpeg"))
            collageIth += 1








        # resize images to be small enough to fit multiple per thing
        # add photos on,  to a whitespace, testing every possiblity?

        # sort the arrary to optimize collaging?


    else:
        print("Now editing")
        while len(filePaths) > 0:
            # Header
            print(saveLocations[0])
            with Image.open(filePaths[0]) as img:


                # Resizing it
                img = setInches(img, downsizeTarget, newDim)

                img.save(saveLocations[0].resolve())
                filePaths.pop(0)
                saveLocations.pop(0)