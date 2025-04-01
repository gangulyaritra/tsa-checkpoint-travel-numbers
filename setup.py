from setuptools import find_packages, setup

with open("./requirements/requirements.txt", "r") as req_file:
    REQUIREMENTS = req_file.read().splitlines()

setup(
    name="tsa-checkpoint-travel-numbers",
    version="1.0.0",
    author="Aritra Ganguly",
    author_email="aritraganguly.in@protonmail.com",
    description="ETL pipeline to scrape passenger travel numbers from the TSA website.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gangulyaritra/tsa-checkpoint-travel-numbers.git",
    license="MIT",
    keywords="Python, ETL, Airflow, Snowflake, Streamlit, Prophet, TSA checkpoint travel numbers",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Apache Airflow",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=REQUIREMENTS,
    package_data={"": ["*"]},
    include_package_data=True,
    zip_safe=False,
    entry_points={"console_scripts": ["run_travel_numbers = tsa_checkpoint.main:main"]},
)
