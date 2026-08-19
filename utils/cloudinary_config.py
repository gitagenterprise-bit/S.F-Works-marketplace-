import os

import cloudinary
import cloudinary.uploader


# =========================================================
# CLOUDINARY CONFIGURATION
# =========================================================

def init_cloudinary():

    cloudinary.config(
        cloud_name=os.getenv(
            "CLOUDINARY_CLOUD_NAME"
        ),

        api_key=os.getenv(
            "CLOUDINARY_API_KEY"
        ),

        api_secret=os.getenv(
            "CLOUDINARY_API_SECRET"
        ),

        secure=True
    )


# =========================================================
# IMAGE VALIDATION
# =========================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}

MAX_IMAGE_SIZE = 8 * 1024 * 1024  # 8 MB


def validate_image(file):

    if not file:
        return False

    if not file.filename:
        return False

    # -----------------------------------------------------
    # Extension
    # -----------------------------------------------------

    filename = file.filename.lower()

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1]

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return False

    # -----------------------------------------------------
    # File size
    # -----------------------------------------------------

    try:

        file.seek(0, os.SEEK_END)

        file_size = file.tell()

        file.seek(0)

    except Exception:

        return False

    if file_size > MAX_IMAGE_SIZE:
        return False

    if file_size <= 0:
        return False

    return True


# =========================================================
# UPLOAD IMAGE
# =========================================================

def upload_image(
    file,
    folder="sfworks/workers"
):

    if not file:
        return None

    if not file.filename:
        return None

    result = cloudinary.uploader.upload(
        file,

        folder=folder,

        resource_type="image",

        overwrite=False,

        use_filename=False,

        unique_filename=True
    )

    return result


# =========================================================
# DELETE IMAGE FROM CLOUDINARY
# =========================================================

def delete_image(
    image_url
):

    if not image_url:
        return

    try:

        # Extract public_id from Cloudinary URL
        if "res.cloudinary.com" not in image_url:
            return

        parts = image_url.split("/upload/")

        if len(parts) != 2:
            return

        path = parts[1]

        # Remove transformations
        path_parts = path.split("/")

        if path_parts[0].startswith("v"):
            path_parts = path_parts[1:]

        public_id_with_extension = "/".join(
            path_parts
        )

        # Remove extension
        public_id = public_id_with_extension.rsplit(
            ".",
            1
        )[0]

        cloudinary.uploader.destroy(
            public_id,
            resource_type="image"
        )

    except Exception:

        pass
