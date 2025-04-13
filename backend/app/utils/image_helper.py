import base64

def get_test_image_base64():
    with open("app/fakedata/logo-test.png", "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

if __name__ == "__main__":
    # Print the base64 string when run directly
    print(get_test_image_base64()) 