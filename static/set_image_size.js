// Load the image and set its size
const image = document.getElementById('overhead_image');
// log for debugging
console.log('Loading image: ' + image.src + ' to ' + image.id)

if (image.complete) {
    onImageLoad();
} else {
    image.onload = onImageLoad;
};

function onImageLoad() {
    // log for debugging
    console.log('Image loaded');
    // Get the width of the screen
    var screenWidth = window.innerWidth;

    // Set the size of the image's container
    var containerWidth = screenWidth * (2 / 3);
    var containerHeight = image.naturalHeight / image.naturalWidth * containerWidth;
    var imageContainer = document.querySelector('.image');
    // log for debugging
    console.log('setting container size to: ' + containerWidth + 'x' + containerHeight)
    imageContainer.style.width = containerWidth + 'px';
    imageContainer.style.height = containerHeight + 'px';
};
