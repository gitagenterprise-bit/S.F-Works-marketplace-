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
