################################################################################

try:
    from cfpackages.logger_formatter import get_logger
    logger = get_logger(__name__)
except ImportError:
    class logger:
        """A Simple Logger Class"""
        def __getattr__(self, name):
            return lambda *args, **kwargs: print(f"[{name.upper()}]", *args, **kwargs)

try:
    import build
except ImportError:
    print(f"Please install the `build` package")
    exit(1)

import subprocess
import shutil

def build_package():
    """Builds the package"""
    print("Building package...")
    subprocess.run("python -m build".split(" "))

def clean_build():
    """Cleans the build directory"""
    print("Cleaning build directory...")
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("cfpackages.egg-info", ignore_errors=True)
    shutil.rmtree("cfpackages/__pycache__", ignore_errors=True)

def upload_package():
    """Uploads the package to PyPI"""
    print("Uploading package...")
    subprocess.run("twine upload dist/*".split(" "))

def upload_test_package():
    """Uploads the package to Test PyPI"""
    print("Uploading test package...")
    subprocess.run("twine upload --repository testpypi dist/*".split(" "))

################################################################################

import questionary

if __name__ == "__main__":
    result = questionary.select("Select the options you want to run", [
        "ALL (test)",
        "ALL (production)",
        "Build Package",
        "Clean Build",
        "Upload Package",
        "Upload Test Package",
    ]).ask()
    match result:
        case "ALL (test)":
            clean_build()
            build_package()
            # upload_package()
            upload_test_package()
            clean_build()
        case "ALL (production)":
            clean_build()
            build_package()
            upload_package()
            # upload_test_package()
            clean_build()
        case "Build Package":
            build_package()
        case "Clean Build":
            clean_build()
        case "Upload Package":
            upload_package()
        case "Upload Test Package":
            upload_test_package()
        case _:
            logger.info("User iterrupted.")
    logger.info("All done!")
