import os
from PhotoModel import PhotoModel

def test_photomodel_with_image_and_text(image_path: str, user_text: str):
    """Test PhotoModel with both image and user input."""
    if not os.path.exists(image_path):
        print(f"Error: Test image not found at {image_path}")
        return

    photo_model = PhotoModel()

    print("Testing with image and user input...")
    result = photo_model.analyze_image(image_path, user_text)

    print(f"Result: {result}")

if __name__ == "__main__":
    test_image_path = "test_images/test_image.jpg"
    user_text = "The person in photo is girl"

    # Run the test
    print("Running PhotoModel Test...")
    test_photomodel_with_image_and_text(test_image_path, user_text)

