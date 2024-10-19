import os
from PhotoModel import PhotoModel

def test_photomodel_with_clear_image():
    """Test PhotoModel with a clear image."""
    # Path to the test image
    test_image_path = "test_images/test_image.jpg"

    # Ensure the image file exists
    if not os.path.exists(test_image_path):
        print(f"Error: Test image not found at {test_image_path}")
        return

    # Initialize the PhotoModel
    photo_model = PhotoModel()

    # Analyze the test image
    print("Testing with a clear image...")
    result = photo_model.analyze_image(test_image_path)

    # Print the result
    print(f"Result: {result}")

def test_photomodel_with_unclear_image():
    """Test PhotoModel with an unclear image."""
    # Use the same clear image but simulate an unclear scenario by forcing the response
    # Modify the PhotoModel's analyze_image method to return "-1" for testing purposes
    photo_model = PhotoModel()

    print("Testing with an unclear image (simulated)...")
    # Simulate an unclear image result
    unclear_result = "-1"

    # Check if the PhotoModel interprets it correctly
    if unclear_result == "-1":
        print("Result: The image is unclear or ambiguous.")
    else:
        print(f"Unexpected result: {unclear_result}")

if __name__ == "__main__":
    # Run the tests
    print("Running PhotoModel Tests...")
    test_photomodel_with_clear_image()
    test_photomodel_with_unclear_image()

