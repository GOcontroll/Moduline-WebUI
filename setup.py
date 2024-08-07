from pathlib import Path

from setuptools import setup

root = Path(__file__).parent
long_description = (root / "README.md").read_text()

setup(
    name="ModulineWebUI",
    version="0.0.1",
    description="A web UI to configure GOcontroll Moduline controllers",
    url="https://github.com/GOcontroll/Moduline-WebUI",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GOcontroll",
    author_email="info@gocontroll.com",
    maintainer="Maud Spierings",
    install_requires=["microdot", "PyJWT", "netifaces"],
    packages=[
        "ModulineWebUI",
        "ModulineWebUI/assets",
        "ModulineWebUI/static",
        "ModulineWebUI/js",
        "ModulineWebUI/style",
    ],
    package_data={"": ["*.js", "*.html", "*.css", "*.jpg", "*.ico", "*.png"]},
    entry_points={
        "console_scripts": [
            "go-webui = ModulineWebUI.__main__:execute_script",
        ]
    },
)
